"""
Módulo de Monitoramento Docker Swarm
Monitora nodes, serviços e réplicas do cluster Docker Swarm
"""

import docker
from docker.errors import DockerException, APIError
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SwarmMonitor:
    """Classe responsável por monitorar clusters Docker Swarm"""

    def __init__(self):
        """Inicializa o monitor de Swarm"""
        self.client: Optional[docker.DockerClient] = None
        self.is_swarm_active = False
        self.is_manager = False
        self._connect()

    def _connect(self) -> None:
        """Estabelece conexão com o Docker e verifica status do Swarm"""
        try:
            self.client = docker.from_env()
            self.client.ping()

            # Verifica se estamos em um swarm
            info = self.client.info()
            swarm_info = info.get("Swarm", {})

            if swarm_info.get("LocalNodeState") == "active":
                self.is_swarm_active = True
                self.is_manager = swarm_info.get("ControlAvailable", False)

                node_id = swarm_info.get("NodeID", "unknown")
                role = "manager" if self.is_manager else "worker"
                logger.info(f"Docker Swarm ativo - Node: {node_id[:12]} ({role})")
            else:
                self.is_swarm_active = False
                self.is_manager = False
                logger.info("Docker Swarm não está ativo neste host")

        except DockerException as e:
            logger.error(f"Erro ao conectar com Docker: {e}")
            self.client = None

    def is_connected(self) -> bool:
        """Verifica se está conectado ao Docker"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except:
            return False

    def get_swarm_info(self) -> Dict[str, Any]:
        """
        Obtém informações gerais do Swarm

        Returns:
            Dicionário com informações do swarm
        """
        if not self.is_connected() or not self.is_swarm_active:
            return {"active": False}

        try:
            info = self.client.info()
            swarm_info = info.get("Swarm", {})

            return {
                "active": True,
                "node_id": swarm_info.get("NodeID", "")[:12],
                "is_manager": self.is_manager,
                "cluster_id": swarm_info.get("Cluster", {}).get("ID", "")[:12],
                "managers": swarm_info.get("Managers", 0),
                "nodes": swarm_info.get("Nodes", 0),
            }
        except Exception as e:
            logger.error(f"Erro ao obter info do Swarm: {e}")
            return {"active": False, "error": str(e)}

    def get_nodes(self) -> List[Dict[str, Any]]:
        """
        Lista todos os nodes do cluster Swarm

        Returns:
            Lista de nodes com suas informações
        """
        if not self.is_connected() or not self.is_swarm_active:
            return []

        if not self.is_manager:
            logger.debug("Node não é manager - não pode listar nodes do swarm")
            return []

        try:
            nodes = self.client.nodes.list()
            node_list = []

            for node in nodes:
                attrs = node.attrs
                spec = attrs.get("Spec", {})
                status = attrs.get("Status", {})
                manager_status = attrs.get("ManagerStatus", {})
                description = attrs.get("Description", {})
                resources = description.get("Resources", {})

                # Calcula recursos
                nano_cpus = resources.get("NanoCPUs", 0)
                cpus = nano_cpus / 1e9 if nano_cpus else 0
                memory_bytes = resources.get("MemoryBytes", 0)
                memory_gb = memory_bytes / (1024**3) if memory_bytes else 0

                node_info = {
                    "id": node.id[:12],
                    "hostname": description.get("Hostname", "unknown"),
                    "role": spec.get("Role", "worker"),
                    "availability": spec.get("Availability", "unknown"),
                    "status": status.get("State", "unknown"),
                    "status_message": status.get("Message", ""),
                    "ip_address": status.get("Addr", "").split(":")[0] if status.get("Addr") else "",
                    "cpus": round(cpus, 1),
                    "memory_gb": round(memory_gb, 2),
                    "engine_version": description.get("Engine", {}).get("EngineVersion", ""),
                    "os": description.get("Platform", {}).get("OS", ""),
                    "arch": description.get("Platform", {}).get("Architecture", ""),
                }

                # Info do manager (se aplicável)
                if manager_status:
                    node_info["manager_status"] = {
                        "leader": manager_status.get("Leader", False),
                        "reachability": manager_status.get("Reachability", "unknown"),
                    }

                node_list.append(node_info)

            # Ordena: managers primeiro, depois workers
            node_list.sort(key=lambda x: (x["role"] != "manager", x["hostname"]))

            logger.debug(f"Listados {len(node_list)} nodes do Swarm")
            return node_list

        except APIError as e:
            logger.error(f"Erro na API do Docker ao listar nodes: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado ao listar nodes: {e}")
            return []

    def get_services(self) -> List[Dict[str, Any]]:
        """
        Lista todos os serviços do Swarm

        Returns:
            Lista de serviços com seus status
        """
        if not self.is_connected() or not self.is_swarm_active:
            return []

        if not self.is_manager:
            logger.debug("Node não é manager - não pode listar serviços do swarm")
            return []

        try:
            services = self.client.services.list()
            service_list = []

            for service in services:
                attrs = service.attrs
                spec = attrs.get("Spec", {})
                mode = spec.get("Mode", {})

                # Determina modo de replicação
                replicated = mode.get("Replicated", {})
                global_mode = mode.get("Global")

                if global_mode is not None:
                    mode_type = "global"
                    desired_replicas = None  # Global = uma por node
                else:
                    mode_type = "replicated"
                    desired_replicas = replicated.get("Replicas", 1)

                # Conta tasks rodando
                tasks = service.tasks(filters={"desired-state": "running"})
                running_tasks = sum(1 for t in tasks if t.get("Status", {}).get("State") == "running")

                # Obtém imagem
                container_spec = spec.get("TaskTemplate", {}).get("ContainerSpec", {})
                image = container_spec.get("Image", "unknown")
                # Remove hash da imagem se presente
                if "@sha256:" in image:
                    image = image.split("@")[0]

                service_info = {
                    "id": service.id[:12],
                    "name": spec.get("Name", service.name),
                    "image": image,
                    "mode": mode_type,
                    "replicas_running": running_tasks,
                    "replicas_desired": desired_replicas,
                    "created": attrs.get("CreatedAt", ""),
                    "updated": attrs.get("UpdatedAt", ""),
                }

                # Calcula status de saúde do serviço
                if mode_type == "replicated":
                    if running_tasks >= desired_replicas:
                        service_info["health"] = "healthy"
                    elif running_tasks > 0:
                        service_info["health"] = "degraded"
                    else:
                        service_info["health"] = "down"
                else:
                    # Para global services, verifica se está rodando em algum lugar
                    service_info["health"] = "healthy" if running_tasks > 0 else "down"

                service_list.append(service_info)

            # Ordena por nome
            service_list.sort(key=lambda x: x["name"])

            logger.debug(f"Listados {len(service_list)} serviços do Swarm")
            return service_list

        except APIError as e:
            logger.error(f"Erro na API do Docker ao listar serviços: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado ao listar serviços: {e}")
            return []

    def get_cluster_resources(self) -> Dict[str, Any]:
        """
        Calcula recursos totais do cluster (soma de todos os nodes)

        Returns:
            Dicionário com recursos totais do cluster
        """
        nodes = self.get_nodes()

        if not nodes:
            return {}

        total_cpus = 0
        total_memory_gb = 0
        nodes_ready = 0
        nodes_down = 0
        managers_count = 0
        workers_count = 0

        for node in nodes:
            total_cpus += node.get("cpus", 0)
            total_memory_gb += node.get("memory_gb", 0)

            if node.get("status") == "ready":
                nodes_ready += 1
            else:
                nodes_down += 1

            if node.get("role") == "manager":
                managers_count += 1
            else:
                workers_count += 1

        return {
            "total_nodes": len(nodes),
            "nodes_ready": nodes_ready,
            "nodes_down": nodes_down,
            "managers": managers_count,
            "workers": workers_count,
            "total_cpus": round(total_cpus, 1),
            "total_memory_gb": round(total_memory_gb, 2),
        }

    def check_swarm_health(self) -> List[Dict[str, Any]]:
        """
        Verifica a saúde do cluster Swarm e gera alertas

        Returns:
            Lista de alertas de problemas encontrados
        """
        alerts = []

        if not self.is_connected():
            return [{
                "type": "DOCKER_CONNECTION_ERROR",
                "severity": "critical",
                "message": "❌ Não foi possível conectar ao Docker",
            }]

        if not self.is_swarm_active:
            # Não é um erro, apenas não está em swarm
            return []

        if not self.is_manager:
            # Worker não pode verificar saúde do cluster completo
            return []

        # Verifica nodes
        nodes = self.get_nodes()
        for node in nodes:
            if node.get("status") != "ready":
                alerts.append({
                    "type": "SWARM_NODE_DOWN",
                    "severity": "critical",
                    "node": node.get("hostname"),
                    "message": f"🔴 Node '{node.get('hostname')}' está {node.get('status').upper()}!",
                })

            if node.get("availability") == "drain":
                alerts.append({
                    "type": "SWARM_NODE_DRAIN",
                    "severity": "warning",
                    "node": node.get("hostname"),
                    "message": f"⚠️ Node '{node.get('hostname')}' está em modo DRAIN",
                })

            # Verifica reachability do manager
            manager_status = node.get("manager_status", {})
            if manager_status and manager_status.get("reachability") == "unreachable":
                alerts.append({
                    "type": "SWARM_MANAGER_UNREACHABLE",
                    "severity": "critical",
                    "node": node.get("hostname"),
                    "message": f"🔴 Manager '{node.get('hostname')}' está UNREACHABLE!",
                })

        # Verifica serviços
        services = self.get_services()
        for service in services:
            if service.get("health") == "down":
                alerts.append({
                    "type": "SWARM_SERVICE_DOWN",
                    "severity": "critical",
                    "service": service.get("name"),
                    "message": f"🔴 Serviço '{service.get('name')}' está completamente DOWN (0 réplicas)!",
                })
            elif service.get("health") == "degraded":
                desired = service.get("replicas_desired", "?")
                running = service.get("replicas_running", 0)
                alerts.append({
                    "type": "SWARM_SERVICE_DEGRADED",
                    "severity": "high",
                    "service": service.get("name"),
                    "message": f"⚠️ Serviço '{service.get('name')}' degradado ({running}/{desired} réplicas)",
                })

        if alerts:
            logger.warning(f"Detectados {len(alerts)} problemas no Swarm")

        return alerts

    def get_swarm_summary(self) -> str:
        """
        Gera um resumo formatado do status do Swarm

        Returns:
            String formatada com resumo do Swarm
        """
        if not self.is_connected():
            return "❌ *Swarm:* Não conectado ao Docker"

        if not self.is_swarm_active:
            return "ℹ️ *Swarm:* Não ativo (modo standalone)"

        if not self.is_manager:
            return "ℹ️ *Swarm:* Ativo (node worker - visão limitada)"

        try:
            swarm_info = self.get_swarm_info()
            resources = self.get_cluster_resources()
            nodes = self.get_nodes()
            services = self.get_services()

            # Status geral
            nodes_status = f"{resources.get('nodes_ready', 0)}/{resources.get('total_nodes', 0)} online"
            if resources.get('nodes_down', 0) > 0:
                nodes_emoji = "🟡"
            else:
                nodes_emoji = "🟢"

            # Contagem de serviços saudáveis
            healthy_services = sum(1 for s in services if s.get("health") == "healthy")
            total_services = len(services)

            if healthy_services == total_services:
                services_emoji = "🟢"
            elif healthy_services > 0:
                services_emoji = "🟡"
            else:
                services_emoji = "🔴"

            summary = f"""🐝 *Docker Swarm*

{nodes_emoji} *Nodes:* {nodes_status} ({resources.get('managers', 0)} managers, {resources.get('workers', 0)} workers)
{services_emoji} *Serviços:* {healthy_services}/{total_services} saudáveis
💻 *Recursos Totais:* {resources.get('total_cpus', 0)} CPUs, {resources.get('total_memory_gb', 0)}GB RAM

*Status dos Nodes:*"""

            for node in nodes:
                status_emoji = "🟢" if node.get("status") == "ready" else "🔴"
                role_icon = "👑" if node.get("role") == "manager" else "⚙️"
                leader = " (Leader)" if node.get("manager_status", {}).get("leader") else ""

                summary += f"\n{status_emoji} {role_icon} {node.get('hostname')}{leader}"
                summary += f"\n   └─ {node.get('cpus')} CPUs | {node.get('memory_gb')}GB RAM | {node.get('ip_address')}"

            # Lista serviços com problemas
            problem_services = [s for s in services if s.get("health") != "healthy"]
            if problem_services:
                summary += "\n\n⚠️ *Serviços com Problemas:*"
                for service in problem_services:
                    health_emoji = "🟡" if service.get("health") == "degraded" else "🔴"
                    running = service.get("replicas_running", 0)
                    desired = service.get("replicas_desired", "global")
                    summary += f"\n{health_emoji} {service.get('name')} ({running}/{desired})"

            return summary.strip()

        except Exception as e:
            logger.error(f"Erro ao gerar resumo Swarm: {e}")
            return f"❌ *Swarm:* Erro ao coletar dados - {str(e)[:50]}"

    def get_node_local_info(self) -> Dict[str, Any]:
        """
        Obtém informações do node local (funciona em manager e worker)

        Returns:
            Dicionário com informações do node local
        """
        if not self.is_connected() or not self.is_swarm_active:
            return {}

        try:
            info = self.client.info()
            swarm_info = info.get("Swarm", {})

            return {
                "node_id": swarm_info.get("NodeID", "")[:12],
                "is_manager": self.is_manager,
                "node_addr": swarm_info.get("NodeAddr", ""),
                "local_node_state": swarm_info.get("LocalNodeState", ""),
                "cluster_id": swarm_info.get("Cluster", {}).get("ID", "")[:12] if swarm_info.get("Cluster") else "",
                "managers_in_cluster": swarm_info.get("Managers", 0),
                "nodes_in_cluster": swarm_info.get("Nodes", 0),
            }
        except Exception as e:
            logger.error(f"Erro ao obter info local do node: {e}")
            return {}

    def get_full_swarm_data(self) -> Dict[str, Any]:
        """
        Obtém todos os dados do Swarm em um único dicionário
        (usado para envio via heartbeat)

        Returns:
            Dicionário completo com dados do swarm
        """
        if not self.is_swarm_active:
            return {
                "active": False,
            }

        data = {
            "active": True,
            "is_manager": self.is_manager,
            "local_node": self.get_node_local_info(),
        }

        # Apenas managers podem ver dados completos do cluster
        if self.is_manager:
            data["cluster_resources"] = self.get_cluster_resources()
            data["nodes"] = self.get_nodes()
            data["services"] = self.get_services()

            # Resumo de saúde
            alerts = self.check_swarm_health()
            data["health"] = {
                "status": "healthy" if not alerts else "unhealthy",
                "alert_count": len(alerts),
                "alerts": [a.get("type") for a in alerts],
            }

        return data
