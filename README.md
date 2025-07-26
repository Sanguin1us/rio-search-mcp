# Rio Search MCP Server

Servidor MCP (Model Context Protocol) especializado em pesquisas de informações governamentais do Rio de Janeiro usando um agente de pesquisa LangGraph.

## O que faz

Fornece uma ferramenta `rio_search` que:
- Realiza 15+ pesquisas automatizadas em sites oficiais do Rio
- Foca em fontes como 1746.rio, prefeitura.rio, carioca.rio
- Retorna informações estruturadas sobre serviços municipais
- Especializado em atendimento a imigrantes e cidadãos

## Configuração

### Pré-requisitos
- Python 3.10+
- Chaves de API configuradas (ver abaixo)

### Instalação
```bash
git clone https://github.com/Sanguin1us/rio-search-mcp.git
cd rio-search-mcp
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate

pip install -r requirements.txt
```

### Configuração das APIs

**IMPORTANTE:** Configure as chaves de API no arquivo `rio_search_server.py`:

```python
# Substitua os ... pelas suas chaves
os.environ["GOOGLE_API_KEY"] = "sua_chave_google_aqui"
jina_api_key = "sua_chave_jina_aqui"
```

**APIs necessárias:**
- **Google Gemini API**: https://aistudio.google.com/
- **Jina AI API**: https://jina.ai/

### Teste do servidor
```bash
python rio_search_server.py
```

## Configuração MCP

### Cliente MCP genérico

Configuração para clientes compatíveis com MCP:

```json
{
  "mcpServers": {
    "rio-search": {
      "command": "python",
      "args": ["/caminho/completo/para/rio_search_server.py"],
      "env": {}
    }
  }
}
```

**Windows (usar barras duplas):**
```json
{
  "mcpServers": {
    "rio-search": {
      "command": "python", 
      "args": ["C:\\caminho\\para\\rio_search_server.py"],
      "env": {}
    }
  }
}
```

### Especificações técnicas
- **Transporte:** stdio
- **Protocolo:** JSON-RPC
- **Ferramentas:** `rio_search(citizen_query: str)`
- **Recursos:** `rio://search/info`

## Uso

### Exemplos de consultas
```
"Sou da Venezuela e preciso de ajuda com documentos e trabalho"
"Onde conseguir atendimento de saúde gratuito no Rio?"
"Quais programas de assistência social estão disponíveis?"
"Documentos para matrícula escolar"
```

### Comportamento esperado
1. Cliente solicita permissão para usar a ferramenta
2. Servidor executa 15+ pesquisas (1-3 minutos)
3. Retorna resposta detalhada com:
   - Procedimentos específicos
   - Contatos e telefones
   - Localizações por bairro
   - Links oficiais

## Troubleshooting

### Servidor não inicia
```bash
# Verificar versão Python
python --version

# Reinstalar dependências
pip install -r requirements.txt

# Testar imports
python -c "import mcp, requests, langgraph; print('OK')"
```

### Cliente não conecta
- Verificar caminho absoluto no arquivo de configuração
- Confirmar que as chaves de API estão configuradas
- Testar servidor manualmente antes da configuração

### Respostas lentas
Normal. O servidor faz pesquisas extensivas para garantir informações precisas e completas.

## Dependências

```
mcp>=1.2.0
langchain>=0.1.0
langgraph>=0.1.0
langchain-core>=0.1.0
langchain-google-genai>=0.1.0
requests>=2.25.0
```

## Estrutura do projeto

```
rio-search-mcp/
├── rio_search_server.py    # Servidor principal
├── requirements.txt        # Dependências
├── README.md              # Esta documentação
└── .gitignore            # Arquivos ignorados pelo git
```
