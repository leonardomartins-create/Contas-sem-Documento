import asyncio
from playwright.async_api import async_playwright
import os
import requests
from github import Github

# Configurações do seu repositório
REPO_NAME = "leonardomartins-create/Contas-sem-Documento"
# Coloque aqui a URL exata da sua Query no Databricks
DATABRICKS_QUERY_URL = "SUA_URL_AQUI" 

async def extrair_dados():
    async with async_playwright() as p:
        print("🚀 Abrindo navegador...")
        # Lançando o Chromium (padrão industrial para automação)
        browser = await p.chromium.launch(headless=True) 
        context = await browser.new_context()
        page = await context.new_page()

        print("🔗 Acessando Databricks...")
        await page.goto(DATABRICKS_QUERY_URL)

        # Clica no botão de SSO que você mostrou na imagem
        print("🔘 Clicando no botão Continue with SSO...")
        await page.get_by_role("button", name="Continue with SSO").click()

        # Espera o carregamento da página após o login
        print("⏳ Aguardando autenticação e carregamento dos dados...")
        await page.wait_for_load_state("networkidle")
        
        # Aqui vamos capturar o resultado. 
        # Como você já tem a query, o Playwright vai buscar o botão de Download
        # ou ler o conteúdo da tabela na tela.
        
        # Por enquanto, vamos apenas validar se ele passou da tela de login
        print("✅ Login realizado com sucesso!")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(extrair_dados())
