# 📝 Vigilo - Changelog

## v1.1.0 - 30/11/2025

### ✨ Novas Funcionalidades

#### 1. **Nome Personalizado do Agente** (`AGENT_NAME`)

**Problema resolvido:**  
Antes, o "Host" nas mensagens mostrava o ID do container (ex: `de796e25711c`) em vez do nome do servidor.

**Solução:**  
Nova variável `AGENT_NAME` para personalizar o nome que aparece nas mensagens e heartbeats.

**Como usar:**
```env
# Deixe vazio para usar o hostname do servidor
AGENT_NAME=

# Ou personalize com um nome descritivo
AGENT_NAME=Servidor-Producao
AGENT_NAME=VPS-Principal
AGENT_NAME=App-Server-01
```

**Resultado nas mensagens:**
```
Antes: Host: de796e25711c
Agora: Host: Servidor-Producao
```

---

#### 2. **Monitoramento Automático de TODOS os Containers** (`WATCH_ALL_CONTAINERS`)

**Problema resolvido:**  
Era necessário listar manualmente cada container em `WATCH_CONTAINERS`, o que era trabalhoso e sujeito a erro.

**Solução:**  
Modo automático que monitora **TODOS** os containers rodando no Docker, sem precisar configurar nada!

**Como funciona:**

**Modo Padrão (Automático):**
```env
WATCH_ALL_CONTAINERS=true
```
- ✅ Monitora TODOS os containers automaticamente
- ✅ Detecta novos containers sem reconfigurar
- ✅ Ignora automaticamente o próprio `vigilo-agent`
- ✅ Mostra status e health de todos no relatório

**Modo Manual (Específico):**
```env
WATCH_ALL_CONTAINERS=false
WATCH_CONTAINERS=postgres,nginx,redis
```
- Monitora apenas os containers listados
- Útil se você quer ignorar containers de teste/dev

---

#### 3. **Lista de Containers Ignorados** (`IGNORE_CONTAINERS`)

**Uso:**  
Permite ignorar containers específicos no monitoramento automático.

**Exemplos de uso:**
```env
# Ignora containers temporários ou de desenvolvimento
IGNORE_CONTAINERS=container-temporario,teste-dev,sandbox

# Ignora containers de ferramentas auxiliares
IGNORE_CONTAINERS=watchtower,portainer-agent,traefik
```

**Nota:** O `vigilo-agent` já é ignorado automaticamente, não precisa adicionar.

---

### 📊 Exemplo de Relatório com o Novo Modo

**Antes (modo manual):**
```
🐳 Docker: 8 rodando / 2 parados

Monitorados:
🟢 postgres
🟢 api_prod
🔴 nginx
```

**Agora (modo automático):**
```
🐳 Docker: 8 rodando / 2 parados

Status dos Containers:
🟢 api_prod ✓
🟢 nginx ✓
🟢 postgres ✓
🟢 redis ✓
🟢 rabbitmq ✓
🔴 worker_backup
🟢 mongodb ✓
🟢 elasticsearch ✓
```

**Legenda:**
- 🟢 = Rodando
- 🔴 = Parado/Problema
- ✓ = Health check OK
- ⚠️ = Health check falhou

---

### 🔧 Configuração Recomendada

#### Para a maioria dos casos (deixe no automático):

```env
# .env
AGENT_NAME=Meu-Servidor-Producao
WATCH_ALL_CONTAINERS=true
IGNORE_CONTAINERS=
```

Pronto! O Vigilo vai monitorar tudo automaticamente. 🎉

#### Para casos específicos (controle manual):

```env
# .env
AGENT_NAME=Servidor-Producao
WATCH_ALL_CONTAINERS=false
WATCH_CONTAINERS=postgres,nginx,api_prod
```

Monitora apenas os containers críticos listados.

---

### 🆚 Comparação: Antes vs Agora

| Aspecto | Antes (v1.0) | Agora (v1.1) |
|---------|--------------|--------------|
| **Nome do agente** | ID do container | Personalizável |
| **Monitoramento** | Manual (lista) | Automático |
| **Novos containers** | Precisa reconfigurar | Detecta automaticamente |
| **Configuração** | Obrigatória | Opcional (default funciona) |
| **Flexibilidade** | Baixa | Alta |

---

### 📖 Migração da v1.0 para v1.1

**Se você já usa o Vigilo v1.0:**

1. **Adicione a nova variável (opcional):**
```env
AGENT_NAME=Nome-Do-Seu-Servidor
```

2. **Escolha o modo de monitoramento:**

**Opção A - Automático (recomendado):**
```env
WATCH_ALL_CONTAINERS=true
# Remova ou deixe vazio o WATCH_CONTAINERS
WATCH_CONTAINERS=
```

**Opção B - Manter como estava:**
```env
WATCH_ALL_CONTAINERS=false
WATCH_CONTAINERS=postgres,nginx,api  # Sua lista atual
```

3. **Restart do container:**
```bash
docker-compose down
docker-compose up -d
```

**Compatibilidade:** Totalmente retrocompatível! Se não configurar nada, funciona como antes.

---

### 📊 Relatório Inicial Automático

**Nova funcionalidade:**  
O Vigilo agora envia automaticamente um relatório completo logo após inicializar!

**Sequência de mensagens ao iniciar:**
1. ✅ Mensagem de inicialização
2. 📊 **Relatório inicial** (NOVO!)
3. Loop de monitoramento começa

**Por quê?**  
Para você ter visibilidade imediata do estado do servidor sem esperar 4 horas pelo primeiro relatório.

### 🐛 Correções

- Corrigido hostname do agente quando rodando em Docker
- Melhorado logs de inicialização (mais claro qual modo está ativo)
- Otimizado geração de relatórios Docker
- Adicionado delay de 2s no relatório inicial para estabilização

---

### 📚 Documentação Atualizada

- ✅ `.env.example` com novas variáveis
- ✅ `docker-compose.yml` atualizado
- ✅ `portainer-stack.yml` atualizado
- ✅ Este CHANGELOG criado

---

## v1.0.0 - 30/11/2025

### 🎉 Release Inicial

- ✅ Monitoramento de Host (CPU, RAM, Disco, Uptime)
- ✅ Monitoramento de Containers Docker
- ✅ Alertas via WhatsApp (Evolution API)
- ✅ Heartbeat para n8n
- ✅ Relatórios periódicos
- ✅ Sistema anti-spam (cooldown)
- ✅ Loop robusto e tolerante a falhas
- ✅ Documentação completa
- ✅ Pronto para Portainer

---

**Próxima versão planejada:** v1.2.0 (Dashboard Web - em desenvolvimento)

