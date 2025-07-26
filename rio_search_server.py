#!/usr/bin/env python3
"""
Rio Search MCP Server

A Model Context Protocol server that provides a single tool to query 
Rio de Janeiro government information using a LangGraph research agent.
"""

import asyncio
import logging
import os
from typing import Any
import requests
from mcp.server.fastmcp import FastMCP
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool


# Set up API keys
os.environ["GOOGLE_API_KEY"] = ...
jina_api_key = ...

# Configure logging to stderr (important for MCP servers)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Rio Search")

@tool
def web_search(query: str) -> str:
    '''Return websearch results for the specified query.'''
    url = "https://s.jina.ai/?q=" + query + "&gl=BR&hl=pt&location=Rio+de+Janeiro%2C+RJ"
    headers = {
        "Authorization": "Bearer " + jina_api_key,
        "X-Respond-With": "no-content"
    }

    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'

    return f"Web Search query: {query}, response: {response.text}"

@tool
def read_url(site: str) -> str:
    '''Read the content of the provided website url'''
    url = 'https://r.jina.ai/' + site
    headers = {
        'Authorization': "Bearer " + jina_api_key,
        'X-Remove-Selector': 'header, nav, footer, form, .login-form, .modal, .search, .navbar, #navbar, .user-nav, .menu-list-mobile, .sub-nav, .breadcrumbs, .history, #menu-principal, #menu-servicos, #menu-favoritos',
        'X-Retain-Images': 'none'
    }

    response = requests.get(url, headers=headers)

    return f"Read URL: {site}, content: {response.text}"


system_prompt = """Você é um agente especializado de pesquisa que fornece contexto para o EAí, o assistente virtual oficial da Prefeitura do Rio de Janeiro. Você DEVE usar suas ferramentas extensivamente para pesquisar e coletar informações.

REGRA CRÍTICA: Você DEVE realizar no mínimo 15 chamadas de web_search e read_url antes de fornecer sua resposta final. NUNCA forneça respostas genéricas - SEMPRE pesquise primeiro!

MISSÃO: Use as ferramentas web_search e read_url para encontrar informações autoritativas sobre a consulta do usuário, focando em informações específicas do Rio de Janeiro.

PROCESSO DE PESQUISA OBRIGATÓRIO:
1. Inicie com 2-3 pesquisas amplas sobre o tópico principal
2. Pesquise especificamente por informações municipais do Rio (site:1746.rio, site:carioca.rio, site:prefeitura.rio)
3. Procure fontes governamentais oficiais e procedimentos
4. Leia o conteúdo completo das URLs mais relevantes encontradas
5. Pesquise informações específicas de contato, endereços e procedimentos
6. Cruze informações de múltiplas fontes oficiais
7. Procure programas ou serviços específicos do Rio relacionados à consulta

ATENÇÃO ESPECIAL - CONFORMIDADE COM POLÍTICAS:

1. CLAREZA E PRECISÃO:
   - Forneça informações precisas, coerentes e que enderecem diretamente a consulta
   - Estruture as informações de forma clara e organizada
   - Evite ambiguidades ou complexidade desnecessária

2. FUNDAMENTAÇÃO (GROUNDEDNESS):
   - Use APENAS informações encontradas nas suas pesquisas
   - NUNCA adicione conhecimento externo ou suposições
   - Cada afirmação deve ser rastreável às fontes pesquisadas
   - Cite as URLs específicas de onde cada informação foi extraída

3. POLÍTICAS DE LOCALIZAÇÃO:
   - Para consultas sobre localização, use APENAS O BAIRRO
   - NUNCA solicite ou mencione endereços completos
   - Se encontrar endereços completos nas pesquisas, extraia apenas o bairro
   - Exemplo correto: "No bairro de Copacabana..."
   - Exemplo incorreto: "Na Rua Nossa Senhora de Copacabana, 123..."

4. TRATAMENTO DE EMERGÊNCIAS:
   - Se detectar risco iminente à vida/saúde/segurança na consulta, indique IMEDIATAMENTE:
   - "EMERGÊNCIA DETECTADA: Oriente ligar 190 (Polícia), 192 (SAMU) ou 193 (Bombeiros)"
   - Não faça perguntas adicionais em casos de emergência

5. SEGURANÇA E PRIVACIDADE:
   - NUNCA solicite dados pessoais (Nome, CPF, RG, endereço completo, telefone, e-mail)
   - Para localização, use APENAS bairros
   - Se o serviço requer login, indique redirecionamento para canal oficial seguro

6. COMPLETUDE DAS RESPOSTAS:
   - Garanta que TODOS os aspectos da consulta sejam pesquisados
   - Identifique todas as entidades principais mencionadas na consulta
   - Pesquise informações específicas sobre cada entidade identificada
   - Não deixe nenhum aspecto significativo sem pesquisa

ESTRATÉGIA DE BUSCA DETALHADA:
- Use termos específicos como "[tópico] Rio de Janeiro", "[serviço] prefeitura rio"
- Sempre inclua "Rio de Janeiro" nas pesquisas
- Procure endereços exatos (mas reporte apenas bairros), telefones e procedimentos específicos
- Encontre links diretos para páginas de serviços específicos

Para BENEFÍCIOS FEDERAIS (como INSS, BPC): Ainda pesquise por:
- Agências do INSS específicas no Rio de Janeiro
- Serviços municipais de apoio (localizações de CRAS no Rio)
- Pontos de contato e programas de assistência locais
- Telefones específicos no Rio

FORMATO DE SAÍDA ESTRUTURADO:
Organize o contexto em seções claras:

1. INFORMAÇÕES PRINCIPAIS:
   - Fatos específicos encontrados através da pesquisa
   - Procedimentos passo a passo com detalhes específicos do Rio

2. CONTATOS E LOCALIZAÇÕES:
   - Bairros onde os serviços estão localizados (NUNCA endereços completos)
   - Telefones específicos encontrados
   - Horários de funcionamento

3. LINKS OFICIAIS:
   - URLs EXATAS para páginas específicas (ex: https://www.1746.rio/hc/pt-br/articles/[artigo-específico])
   - Sempre prefira links diretos a artigos ou serviços específicos
   - Evite links genéricos para homepages

4. PROGRAMAS MUNICIPAIS RELEVANTES:
   - Serviços de apoio municipais relacionados
   - Programas específicos do Rio que possam ajudar

LEMBRETES CRÍTICOS:
- Você DEVE usar as ferramentas extensivamente (mínimo 15 chamadas)
- O EAí usará APENAS as informações que você fornecer
- Inclua pontos de contato e bairros específicos do Rio de Janeiro
- SEMPRE pesquise antes de responder - respostas genéricas são PROIBIDAS
- Mantenha conformidade com TODAS as políticas mencionadas
- Cada informação deve ser fundamentada em pesquisas reais"""

graph = create_react_agent(
    "google_genai:gemini-2.5-flash",
    tools=[web_search, read_url],
    prompt=system_prompt,
)

@mcp.tool()
async def rio_search(citizen_query: str) -> str:
    """
    Search for Rio de Janeiro government information and services using a specialized research agent.
    
    This tool uses an intelligent research agent that performs extensive searches across 
    Rio de Janeiro government websites and official sources to provide comprehensive 
    answers about municipal services, procedures, and programs.
    
    Args:
        citizen_query: The citizen's question about Rio de Janeiro services, procedures, 
                      documents, programs, or any government-related information
        
    Returns:
        Comprehensive research results with specific information about Rio de Janeiro services
    """
    try:
        logger.info(f"Processing citizen query: {citizen_query}")
        
        inputs = {
            "messages": [
                {
                    "role": "user", 
                    "content": citizen_query
                }
            ]
        }
        
        # Run the LangGraph agent with high recursion limit for thorough research
        result = graph.invoke(inputs, {"recursion_limit": 100})
        
        # Extract the final message from the agent
        final_message = result["messages"][-1].content
        
        logger.info(f"Successfully processed query: {citizen_query}")
        
        return final_message
        
    except Exception as e:
        error_msg = f"Error processing citizen query '{citizen_query}': {str(e)}"
        logger.error(error_msg)
        return f"Erro: Não foi possível processar a consulta '{citizen_query}'. Por favor, tente novamente ou reformule sua pergunta."

@mcp.resource("rio://search/info")
async def rio_search_info() -> str:
    """
    Information about the Rio Search service capabilities and usage.
    
    Returns:
        Service information and usage guidelines
    """
    return """
Rio Search - Serviço de Pesquisa Especializado

Este serviço utiliza um agente de pesquisa inteligente especializado em informações 
da Prefeitura do Rio de Janeiro.

CAPACIDADES:
- Pesquisa extensiva em fontes oficiais do Rio de Janeiro
- Análise de múltiplas fontes governamentais
- Informações específicas sobre serviços municipais
- Procedimentos e documentação necessária
- Contatos e localizações (apenas bairros)
- Programas e benefícios municipais

FONTES CONSULTADAS:
- 1746.rio (Portal oficial de serviços)
- prefeitura.rio (Site da Prefeitura)
- carioca.rio (Portal do cidadão)
- Órgãos e secretarias municipais
- Programas governamentais específicos

TIPOS DE CONSULTAS SUPORTADAS:
- Serviços para imigrantes e refugiados
- Documentação e procedimentos
- Programas sociais e assistência
- Saúde pública (SUS municipal)
- Educação e cultura
- Trabalho e emprego
- Habitação e moradia
- Meio ambiente e sustentabilidade

EXEMPLOS DE CONSULTAS:
- "Preciso de ajuda para regularizar minha situação no Brasil"
- "Como conseguir trabalho formal no Rio?"
- "Onde encontrar atendimento de saúde gratuito?"
- "Programas de assistência social disponíveis"
- "Documentos necessários para matrícula escolar"

O agente realiza no mínimo 15 pesquisas antes de fornecer uma resposta completa
e fundamentada em fontes oficiais.
"""

if __name__ == "__main__":
    mcp.run(transport="stdio")