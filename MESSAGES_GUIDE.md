# 📱 Vigilo - Guia de Mensagens e Payloads

Este documento descreve **todas as mensagens** que você receberá no WhatsApp e **todos os payloads** enviados para o webhook n8n, com exemplos práticos de interpretação.

---

## 📱 PARTE 1: Mensagens do WhatsApp

Todas as mensagens chegam via Evolution API no número configurado em `NOTIFY_NUMBER`.

---

### 1️⃣ Mensagem de Inicialização

**Quando acontece:** Logo após o agente iniciar (startup do container)

**Formato:**
```
✅ Vigilo Iniciado

🖥️ Host: servidor-producao
🕒 30/11/2025 14:30:15
```

**O que significa:**
- ✅ O agente está rodando e operacional
- Todas as conexões (Evolution API, n8n, Docker) foram estabelecidas
- O monitoramento começou

**Ação recomendada:** Nenhuma. É apenas informativo.

---

### 2️⃣ Mensagem de Encerramento

**Quando acontece:** Quando o agente é desligado (docker stop, SIGTERM, etc)

**Formato:**
```
🛑 Vigilo Encerrado

🖥️ Host: servidor-producao
🕒 30/11/2025 18:45:30

📊 Checagens realizadas: 1.445
```

**O que significa:**
- O agente foi desligado (intencional ou não)
- Mostra quantas checagens foram feitas desde que iniciou

**Ação recomendada:** 
- Se foi intencional: OK
- Se não esperava: Investigar logs do container

---

### 3️⃣ Alerta de CPU Crítica

**Quando acontece:** CPU ultrapassa o limiar configurado (padrão: 85%)

**Formato:**
```
⚠️ ALERTA VIGILO ⚠️

🔴 CPU em 92.5% (limite: 85.0%)

🕒 30/11/2025 15:20:10
```

**O que significa:**
- A CPU está sobrecarregada
- Pode causar lentidão ou travamentos
- O alerta tem cooldown de 30 minutos (não reenvia se continuar alto)

**Ação recomendada:**
1. Verifique processos com `top` ou `htop`
2. Identifique processos consumindo muita CPU
3. Considere escalar recursos ou otimizar aplicações

**Possíveis causas:**
- Processo travado em loop
- Ataque DDoS
- Backup pesado rodando
- Aplicação mal otimizada

---

### 4️⃣ Alerta de RAM Crítica

**Quando acontece:** Memória RAM ultrapassa o limiar (padrão: 90%)

**Formato:**
```
⚠️ ALERTA VIGILO ⚠️

🔴 RAM em 95.2% (limite: 90.0%)

🕒 30/11/2025 15:25:33
```

**O que significa:**
- A memória está quase esgotada
- Sistema pode começar a usar SWAP (muito lento)
- Risco de OOM Killer matar processos

**Ação recomendada:**
1. Verifique uso de memória: `free -h`
2. Identifique processos: `ps aux --sort=-%mem | head`
3. Considere reiniciar serviços pesados
4. Avaliar upgrade de RAM

**Possíveis causas:**
- Memory leak em aplicação
- Cache muito grande
- Muitos containers rodando
- Banco de dados sem otimização

---

### 5️⃣ Alerta de Disco Crítico

**Quando acontece:** Disco ultrapassa o limiar (padrão: 90%)

**Formato:**
```
⚠️ ALERTA VIGILO ⚠️

🔴 DISCO em 94.8% (limite: 90.0%)

🕒 30/11/2025 16:10:45
```

**O que significa:**
- O disco está quase cheio
- **CRÍTICO:** Sistema pode travar quando chegar a 100%
- Logs podem parar de funcionar

**Ação recomendada:**
1. Verifique uso: `df -h`
2. Identifique grandes arquivos: `du -sh /* | sort -h`
3. Limpe logs antigos: `/var/log/`
4. Limpe cache do Docker: `docker system prune -a`
5. Considere aumentar disco

**Possíveis causas:**
- Logs não rotacionados
- Backups antigos
- Imagens Docker acumuladas
- Arquivos temporários esquecidos

---

### 6️⃣ Alerta de Container Não Encontrado

**Quando acontece:** Um container da lista `WATCH_CONTAINERS` não existe

**Formato:**
```
⚠️ ALERTA VIGILO ⚠️

❌ Container 'postgres' não encontrado!

🕒 30/11/2025 16:15:20
```

**O que significa:**
- Um container importante foi removido
- Ou o nome está errado na configuração
- Serviço pode estar indisponível

**Ação recomendada:**
1. Verifique se o container existe: `docker ps -a | grep postgres`
2. Se foi removido acidentalmente, recrie-o
3. Se mudou de nome, atualize `WATCH_CONTAINERS`

---

### 7️⃣ Alerta de Container Parado

**Quando acontece:** Container monitorado está parado/crashed

**Formato:**
```
⚠️ ALERTA VIGILO ⚠️

🔴 Container 'api_prod' está EXITED!

🕒 30/11/2025 16:20:15
```

**O que significa:**
- Um serviço crítico está fora do ar
- Pode ter crasheado ou sido parado
- **URGENTE:** Serviço indisponível

**Ação recomendada:**
1. Veja os logs: `docker logs api_prod --tail 100`
2. Tente reiniciar: `docker restart api_prod`
3. Se não subir, verifique configuração/erro
4. Considere rollback se foi após deploy

**Status possíveis:**
- `EXITED` - Saiu/crasheou
- `RESTARTING` - Tentando reiniciar
- `PAUSED` - Foi pausado manualmente
- `DEAD` - Morto (erro grave)

---

### 8️⃣ Alerta de Container Unhealthy

**Quando acontece:** Health check do Docker detectou problema

**Formato:**
```
⚠️ ALERTA VIGILO ⚠️

⚠️ Container 'nginx' está UNHEALTHY!

🕒 30/11/2025 16:25:40
```

**O que significa:**
- Container está rodando MAS não está saudável
- Health check está falhando
- Serviço pode estar lento ou com erro

**Ação recomendada:**
1. Verifique logs: `docker logs nginx --tail 50`
2. Inspecione health: `docker inspect nginx | grep -A 20 Health`
3. Teste manualmente o serviço
4. Reinicie se necessário

**Nota:** Só funciona se o container tiver `HEALTHCHECK` configurado no Dockerfile.

---

### 9️⃣ Relatório Inicial

**Quando acontece:** Logo após o agente iniciar (2-3 segundos depois da mensagem de inicialização)

**Formato:**
```
🚀 RELATÓRIO INICIAL

📊 Relatório do Sistema

🟢 CPU: 45.2%
🟢 RAM: 65.8% (5.2GB / 8.0GB)
🟢 Disco: 72.1% (350.5GB / 486.0GB)

⏱️ Uptime: 15 days, 4:23:10
🔢 Processos: 187

🐳 Docker: 8 rodando / 2 parados

Status dos Containers:
🟢 postgres ✓
🟢 api_prod ✓
🟢 nginx ✓

📡 Status do Agente
✅ Checagens realizadas: 0
📤 Heartbeats enviados: 1

🕒 30/11/2025 16:00:05
```

**O que significa:**
- Snapshot completo do estado inicial do servidor
- Confirma que todos os sistemas estão funcionando
- Mostra quais containers estão rodando
- **NOVO na v1.1:** Antes você tinha que esperar 4 horas

**Ação recomendada:** 
- Revisar e confirmar que está tudo OK
- Se houver algo crítico (🔴), já sabe desde o início

**Por quê é útil:**
- Visibilidade imediata após restart
- Detecta problemas logo na inicialização
- Não precisa esperar pelo relatório periódico
- Útil após manutenções

---

### 🔟 Relatório Periódico

**Quando acontece:** A cada X horas (configurado em `REPORT_HOURS`, padrão: 4h)

**Formato:**
```
📊 RELATÓRIO VIGILO

📊 Relatório do Sistema

🟢 CPU: 45.2%
🟢 RAM: 65.8% (5.2GB / 8.0GB)
🟢 Disco: 72.1% (350.5GB / 486.0GB)

⏱️ Uptime: 15 days, 4:23:10
🔢 Processos: 187

🐳 Docker: 8 rodando / 2 parados

Monitorados:
🟢 postgres
🟢 api_prod
🔴 nginx

📡 Status do Agente
✅ Checagens realizadas: 1.445
📤 Heartbeats enviados: 1.443
❌ Falhas heartbeat: 2
📊 Taxa de sucesso: 99.86%

🕒 30/11/2025 16:00:05
```

**O que significa:**
- Resumo completo da saúde do servidor
- **Sempre enviado** (não tem cooldown)
- Mostra também estatísticas do próprio agente

**Interpretação dos emojis:**
- 🟢 = OK, dentro do limite
- 🔴 = Crítico, acima do limite
- ✅ = Funcionando
- ❌ = Com problema

**Ação recomendada:** 
- Revisar e arquivar
- Se houver 🔴, investigar

---

## 🎯 Resumo: Gravidade dos Alertas

| Emoji | Tipo | Gravidade | Ação |
|-------|------|-----------|------|
| ✅ | Inicialização | Info | Nenhuma |
| 🚀 | Relatório inicial | Info | Revisar estado inicial |
| 🛑 | Encerramento | Atenção | Verificar se esperado |
| 🔴 | CPU/RAM/Disco | Alta | Investigar imediatamente |
| ❌ | Container não encontrado | Crítica | Verificar urgente |
| 🔴 | Container parado | Crítica | Reiniciar serviço |
| ⚠️ | Container unhealthy | Alta | Investigar |
| 📊 | Relatório periódico | Info | Revisar |

---

## 🔔 Sistema Anti-Spam (Cooldown)

Para evitar spam de mensagens:

- **Alertas de recursos (CPU/RAM/Disco):** Cooldown de 30 minutos (padrão)
- **Alertas de containers:** Cooldown de 30 minutos (padrão)
- **Relatórios periódicos:** SEM cooldown (sempre enviados)
- **Inicialização/Encerramento:** SEM cooldown (eventos únicos)

**Exemplo:**
```
15:00 - CPU em 90% → ALERTA ENVIADO
15:10 - CPU em 92% → NÃO ENVIA (cooldown)
15:20 - CPU em 88% → NÃO ENVIA (cooldown)
15:35 - CPU em 91% → ALERTA ENVIADO (cooldown expirou)
```

**Configuração:** Altere `ALERT_COOLDOWN` em segundos (padrão: 1800 = 30min)

---

## 🌐 PARTE 2: Payloads do Webhook n8n

Todos os payloads são enviados via **POST** com `Content-Type: application/json`

---

### 1️⃣ Heartbeat Normal (A cada 60s)

**Quando:** A cada ciclo de checagem (configurado em `CHECK_INTERVAL`)

**Payload:**
```json
{
  "agent_name": "servidor-producao",
  "status": "alive",
  "timestamp": 1701368400,
  "consecutive_failures": 0,
  "total_sent": 1445,
  "total_failed": 2,
  "stats": {
    "cpu_percent": 45.2,
    "ram_percent": 65.8,
    "disk_percent": 72.1,
    "uptime_seconds": 1324990
  }
}
```

**Como interpretar:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `agent_name` | string | Nome do servidor (hostname) |
| `status` | string | Sempre "alive" em heartbeats normais |
| `timestamp` | integer | Unix timestamp (segundos desde 1970) |
| `consecutive_failures` | integer | Falhas consecutivas de heartbeat (0 = OK) |
| `total_sent` | integer | Total de heartbeats enviados com sucesso |
| `total_failed` | integer | Total de falhas de envio |
| `stats.cpu_percent` | float | CPU atual em % |
| `stats.ram_percent` | float | RAM atual em % |
| `stats.disk_percent` | float | Disco atual em % |
| `stats.uptime_seconds` | integer | Tempo ligado em segundos |

**Uso recomendado no n8n:**
1. Armazenar em banco de dados para histórico
2. Criar alerta se não receber heartbeat por 5 minutos
3. Gerar gráficos de métricas ao longo do tempo
4. Trigger para ações se `consecutive_failures` > 5

---

### 2️⃣ Evento de Inicialização

**Quando:** Logo após o agente iniciar

**Payload:**
```json
{
  "agent_name": "servidor-producao",
  "status": "alive",
  "timestamp": 1701368400,
  "consecutive_failures": 0,
  "total_sent": 1,
  "total_failed": 0,
  "event_type": "startup",
  "event_data": {
    "message": "Vigilo Agent iniciado",
    "hostname": "servidor-producao"
  }
}
```

**Como interpretar:**

| Campo | Descrição |
|-------|-----------|
| `event_type` | Sempre "startup" |
| `event_data.message` | Mensagem descritiva |
| `event_data.hostname` | Nome do servidor |

**Uso recomendado no n8n:**
- Registrar em log de eventos
- Enviar notificação para Slack/Telegram
- Atualizar dashboard de status

---

### 3️⃣ Evento de Encerramento

**Quando:** Quando o agente é desligado

**Payload:**
```json
{
  "agent_name": "servidor-producao",
  "status": "alive",
  "timestamp": 1701385200,
  "consecutive_failures": 0,
  "total_sent": 1445,
  "total_failed": 2,
  "event_type": "shutdown",
  "event_data": {
    "message": "Vigilo Agent encerrado",
    "checks_performed": 1445
  }
}
```

**Como interpretar:**

| Campo | Descrição |
|-------|-----------|
| `event_type` | Sempre "shutdown" |
| `event_data.message` | Mensagem descritiva |
| `event_data.checks_performed` | Quantas checagens foram feitas |

**Uso recomendado no n8n:**
- Registrar downtime
- Alertar se não foi agendado
- Calcular uptime

---

### 4️⃣ Evento de Alertas Gerados

**Quando:** Sempre que alertas são detectados e enviados

**Payload:**
```json
{
  "agent_name": "servidor-producao",
  "status": "alive",
  "timestamp": 1701370200,
  "consecutive_failures": 0,
  "total_sent": 150,
  "total_failed": 0,
  "event_type": "alerts_generated",
  "event_data": {
    "alert_count": 3,
    "alert_types": [
      "CPU_CRITICAL",
      "CONTAINER_NOT_RUNNING",
      "RAM_CRITICAL"
    ]
  }
}
```

**Como interpretar:**

| Campo | Descrição |
|-------|-----------|
| `event_type` | Sempre "alerts_generated" |
| `event_data.alert_count` | Quantos alertas foram gerados |
| `event_data.alert_types` | Lista dos tipos de alerta |

**Tipos de alerta possíveis:**
- `CPU_CRITICAL` - CPU acima do limite
- `RAM_CRITICAL` - RAM acima do limite
- `DISK_CRITICAL` - Disco acima do limite
- `CONTAINER_NOT_FOUND` - Container não encontrado
- `CONTAINER_NOT_RUNNING` - Container parado
- `CONTAINER_UNHEALTHY` - Container com problema
- `DOCKER_CONNECTION_ERROR` - Erro ao conectar no Docker

**Uso recomendado no n8n:**
- Escalar alertas para PagerDuty/OpsGenie
- Criar tickets automáticos
- Disparar runbooks de correção
- Notificar equipe de plantão

---

## 📊 Workflow Sugerido no n8n

### Workflow Básico de Monitoramento

```
┌─────────────┐
│   Webhook   │ (POST /webhook/vigilo)
└──────┬──────┘
       │
       ├─────────────────────────────────────┐
       │                                     │
       ▼                                     ▼
┌──────────────┐                     ┌──────────────┐
│ IF event_type│                     │ Set Variable │
│   exists?    │                     │ last_heartbeat│
└──────┬───────┘                     └──────────────┘
       │
       ├─── startup ──────► [Log + Notificar]
       │
       ├─── shutdown ─────► [Log + Verificar se esperado]
       │
       └─── alerts_generated ───► [Escalar para equipe]


┌─────────────────────────────────────────────────┐
│  Workflow Paralelo: Detector de Agente Offline │
└─────────────────────────────────────────────────┘

┌─────────────┐
│ Cron (5min) │
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ Verificar se │ (last_heartbeat)
│ recebeu HB   │
│ nos últimos  │
│   5 minutos  │
└──────┬───────┘
       │
       └─── NÃO ──► [ALERTA: Agente Offline!]
```

### Exemplo de Código n8n (IF Node)

```javascript
// Detecta tipo de evento
if ($json.event_type === 'startup') {
  return [{ json: { action: 'log_startup', data: $json } }];
}

if ($json.event_type === 'shutdown') {
  return [{ json: { action: 'log_shutdown', data: $json } }];
}

if ($json.event_type === 'alerts_generated') {
  // Se tem alertas críticos, escala
  const criticalAlerts = $json.event_data.alert_types.filter(type => 
    type.includes('CRITICAL') || 
    type.includes('CONTAINER_NOT_RUNNING')
  );
  
  if (criticalAlerts.length > 0) {
    return [{ json: { action: 'escalate', data: $json, critical: true } }];
  }
}

// Heartbeat normal
return [{ json: { action: 'store_metrics', data: $json } }];
```

---

## 🔍 Troubleshooting de Payloads

### Problema: Não recebo payloads no n8n

**Checklist:**
1. ✅ Webhook n8n está ativo? (modo Production)
2. ✅ URL está correta? (incluindo https://)
3. ✅ Firewall permite conexões do servidor?
4. ✅ Container Vigilo está rodando?
5. ✅ Verificar logs: `docker logs vigilo-agent | grep heartbeat`

**Teste manual:**
```bash
curl -X POST https://seu-n8n.com/webhook/vigilo \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "teste",
    "status": "alive",
    "timestamp": 1701368400
  }'
```

### Problema: Payloads chegam, mas com campos faltando

**Possível causa:** Versão antiga do Vigilo

**Solução:**
```bash
docker-compose pull
docker-compose up -d
```

---

## 📖 Glossário de Termos

| Termo | Significado |
|-------|-------------|
| **Heartbeat** | Sinal de vida enviado periodicamente |
| **Cooldown** | Período de espera antes de reenviar alerta |
| **Payload** | Dados JSON enviados no webhook |
| **Health Check** | Verificação automática de saúde do container |
| **Uptime** | Tempo que o sistema está ligado |
| **OOM Killer** | Mecanismo do Linux que mata processos quando RAM acaba |
| **Threshold** | Limiar/limite configurado para alertas |
| **Unix Timestamp** | Segundos desde 01/01/1970 00:00:00 UTC |

---

## 🎯 Exemplos Práticos de Uso

### Exemplo 1: Calcular Uptime no n8n

```javascript
const uptimeSeconds = $json.stats.uptime_seconds;
const days = Math.floor(uptimeSeconds / 86400);
const hours = Math.floor((uptimeSeconds % 86400) / 3600);
const minutes = Math.floor((uptimeSeconds % 3600) / 60);

return {
  json: {
    uptime: `${days}d ${hours}h ${minutes}m`,
    uptime_days: days
  }
};
```

### Exemplo 2: Detectar Tendência de Crescimento de Disco

```javascript
// Armazena histórico em banco
// Compara com média dos últimos 7 dias

const currentDisk = $json.stats.disk_percent;
const averageLast7Days = 75.0; // Buscar do banco

const growthRate = ((currentDisk - averageLast7Days) / averageLast7Days) * 100;

if (growthRate > 10) {
  // Disco crescendo mais de 10% em relação à média
  return [{ json: { alert: 'DISK_GROWING_FAST', rate: growthRate } }];
}
```

### Exemplo 3: Converter Timestamp para Data Legível

```javascript
const timestamp = $json.timestamp;
const date = new Date(timestamp * 1000);

return {
  json: {
    readable_date: date.toLocaleString('pt-BR', {
      timeZone: 'America/Sao_Paulo'
    })
  }
};
```

---

## ✅ Checklist de Implementação

Para você ou seus clientes:

- [ ] Webhook n8n configurado e testado
- [ ] Workflow para armazenar heartbeats
- [ ] Alerta quando agente fica offline (> 5min sem heartbeat)
- [ ] Workflow para processar eventos de startup/shutdown
- [ ] Workflow para escalar alertas críticos
- [ ] Dashboard com métricas históricas (opcional)
- [ ] Documentação interna de procedimentos de resposta
- [ ] Testes com alertas simulados

---

## 📞 Suporte

Se tiver dúvidas sobre alguma mensagem ou payload:

1. Consulte este guia
2. Verifique logs: `docker logs vigilo-agent`
3. Execute teste: `python3 test_config.py`
4. Abra issue no GitHub

---

**Última atualização:** 30/11/2025  
**Versão do Vigilo:** 1.0.0

