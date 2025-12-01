# 🐳 Vigilo - Guia Docker Hub

Este guia mostra como publicar e usar o Vigilo via Docker Hub.

---

## 📤 Publicar no Docker Hub

### 1️⃣ **Edite o script de publicação:**

```bash
nano publish.sh
```

Altere a linha:
```bash
DOCKER_USER="seu_usuario"  # ← Coloque seu username do Docker Hub
```

### 2️⃣ **Execute o script:**

```bash
./publish.sh
```

O script vai:
- ✅ Verificar login no Docker Hub
- ✅ Fazer build da imagem
- ✅ Enviar para Docker Hub
- ✅ Criar tags `latest` e `1.1.0`

### 3️⃣ **Verifique:**

Acesse: `https://hub.docker.com/r/seu_usuario/vigilo`

---

## 📥 Usar em Outras VPS

### **Método 1: Docker Compose (Recomendado)**

**1. Crie uma pasta:**
```bash
mkdir vigilo && cd vigilo
```

**2. Baixe os arquivos de configuração:**
```bash
# Baixe o docker-compose.hub.yml
wget https://raw.githubusercontent.com/seu-repo/vigilo/main/docker-compose.hub.yml -O docker-compose.yml

# Baixe o .env.example
wget https://raw.githubusercontent.com/seu-repo/vigilo/main/.env.example
```

**Ou copie manualmente:**
```bash
# Copie o docker-compose.hub.yml como docker-compose.yml
# Copie o .env.example
```

**3. Configure o .env:**
```bash
cp .env.example .env
nano .env
```

**Importante configurar:**
```env
# DEFINA UM NOME ÚNICO PARA ESTA VPS!
AGENT_NAME=Producao-VPS-01

# Evolution API
EVOLUTION_URL=https://sua-api.com
EVOLUTION_TOKEN=seu_token
EVOLUTION_INSTANCE=sua_instancia
NOTIFY_NUMBER=5511999999999

# n8n Webhook
N8N_HEARTBEAT_URL=https://seu-n8n.com/webhook/vigilo
```

**4. Inicie:**
```bash
docker-compose up -d
```

**5. Veja os logs:**
```bash
docker-compose logs -f vigilo
```

---

### **Método 2: Docker Run Direto**

```bash
docker run -d \
  --name vigilo-agent \
  --restart unless-stopped \
  -e AGENT_NAME="Producao-VPS-01" \
  -e EVOLUTION_URL="https://sua-api.com" \
  -e EVOLUTION_TOKEN="seu_token" \
  -e EVOLUTION_INSTANCE="sua_instancia" \
  -e NOTIFY_NUMBER="5511999999999" \
  -e N8N_HEARTBEAT_URL="https://n8n.com/webhook/vigilo" \
  -e WATCH_ALL_CONTAINERS="true" \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /etc/localtime:/etc/localtime:ro \
  seu_usuario/vigilo:latest
```

---

### **Método 3: Portainer Stack**

**1. Acesse:** Portainer → Stacks → Add Stack

**2. Cole o conteúdo de `portainer-stack.yml`**

**3. Altere a primeira linha:**
```yaml
image: seu_usuario/vigilo:latest  # ← Seu username do Docker Hub
```

**4. Configure as variáveis de ambiente**

**5. Deploy!**

---

## 🔄 Atualizar Vigilo em Outras VPS

### Quando houver nova versão:

```bash
# 1. Pull da nova imagem
docker pull seu_usuario/vigilo:latest

# 2. Restart do container
docker-compose down
docker-compose up -d

# 3. Verificar logs
docker-compose logs -f vigilo
```

---

## 📋 Estrutura de Diretórios para Deploy

```
/opt/vigilo/              # Pasta recomendada em produção
├── docker-compose.yml    # Copiado de docker-compose.hub.yml
├── .env                  # Configurações desta VPS
└── logs/                 # (opcional) Para bind mount de logs
```

**Exemplo de setup:**
```bash
# Em cada VPS
sudo mkdir -p /opt/vigilo
cd /opt/vigilo

# Copie o docker-compose.hub.yml
# Renomeie para docker-compose.yml
# Configure o .env

docker-compose up -d
```

---

## 🏢 Exemplo: 3 VPS com Nomes Diferentes

### **VPS 1 - Produção**
```env
AGENT_NAME=Producao-Principal
```

### **VPS 2 - Homologação**
```env
AGENT_NAME=Homologacao
```

### **VPS 3 - Cliente**
```env
AGENT_NAME=Cliente-Empresa-XYZ
```

**Resultado:** Você recebe alertas diferenciados de cada VPS! 🎯

---

## 📦 Versionamento

### Tags disponíveis:

```bash
# Última versão (recomendado)
seu_usuario/vigilo:latest

# Versão específica (para produção crítica)
seu_usuario/vigilo:1.1.0
seu_usuario/vigilo:1.0.0
```

### Usar versão específica:

```yaml
# docker-compose.yml
services:
  vigilo:
    image: seu_usuario/vigilo:1.1.0  # ← Versão fixa
```

**Vantagem:** Não atualiza automaticamente, mais estabilidade.

---

## 🔍 Verificar qual versão está rodando:

```bash
docker inspect vigilo-agent | grep -A 5 "Image"
```

---

## 🆘 Troubleshooting

### Erro: "image not found"

**Causa:** Imagem não existe no Docker Hub ou nome errado

**Solução:**
```bash
# Verifique o nome correto
docker search seu_usuario/vigilo

# Pull manual
docker pull seu_usuario/vigilo:latest
```

### Erro: "permission denied" no socket

**Causa:** Container sem permissão para acessar Docker

**Solução:**
```bash
# Verifique se o volume está montado
docker inspect vigilo-agent | grep docker.sock
```

### Container não inicia

**Verificar logs:**
```bash
docker logs vigilo-agent
```

**Verificar variáveis:**
```bash
docker exec vigilo-agent env | grep EVOLUTION
```

---

## 📊 Monitoramento Multi-VPS no n8n

Com múltiplas VPS enviando para o mesmo webhook:

```javascript
// Workflow n8n - Identificar origem
const vps = $json.agent_name;

if (vps === 'Producao-Principal') {
  // Alerta crítico
  return [{ json: { priority: 'P1', team: 'ops' } }];
}

if (vps.startsWith('Cliente-')) {
  // Notifica cliente
  return [{ json: { priority: 'P2', notify_client: true } }];
}
```

---

## ✅ Checklist de Deploy em Nova VPS

- [ ] Docker instalado
- [ ] Pasta criada (`/opt/vigilo`)
- [ ] `docker-compose.yml` configurado
- [ ] `.env` criado e preenchido
- [ ] `AGENT_NAME` único definido
- [ ] `docker-compose up -d` executado
- [ ] Logs verificados
- [ ] Mensagem de inicialização recebida no WhatsApp
- [ ] Relatório inicial recebido

---

## 🔒 Segurança

### ⚠️ NUNCA commite o `.env` com tokens reais!

```bash
# Sempre use .gitignore
echo ".env" >> .gitignore
```

### Recomendações:

- ✅ Use tokens com permissões mínimas
- ✅ Rotacione tokens periodicamente
- ✅ Um `.env` diferente por VPS
- ✅ Backup dos `.env` em local seguro

---

## 📞 Suporte

- 📖 Documentação completa: [README.md](README.md)
- 🚀 Início rápido: [QUICK_START.md](QUICK_START.md)
- 📱 Guia de mensagens: [MESSAGES_GUIDE.md](MESSAGES_GUIDE.md)

---

**Última atualização:** 30/11/2025  
**Versão:** 1.1.0

