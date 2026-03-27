import asyncio
from playwright.async_api import async_playwright
import os
import requests
from github import Github

# Configurações extraídas da sua URL
DATABRICKS_URL = "https://dbc-53bd5b4a-ac3c.cloud.databricks.com/editor/queries/3841745429257799?o=1323332079465250"
REPO_NAME = "leonardomartins-create/Contas-sem-Documento"

async def extrair_dados():
    async with async_playwright() as p:
        print("🚀 Abrindo navegador...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        print("🔗 Acessando Query no Databricks...")
        await page.goto(DATABRICKS_URL)

        # 1. Login SSO
        print("🔘 Clicando no SSO...")
        await page.get_by_role("button", name="Continue with SSO").click()
        
        # Espera o editor carregar
        await page.wait_for_selector("text=Run", timeout=60000)

        # 2. Executar a Query
        print("⚡ Executando Query...")
        await page.click("text=Run")
        
        # Espera o processamento (bolinha de carregamento sumir)
        print("⏳ Aguardando resultados...")
        await page.wait_for_selector("text=Export", timeout=120000) # Espera o botão de exportar aparecer

        # 3. Download do CSV
        print("📥 Iniciando download do CSV...")
        async with page.expect_download() as download_info:
            # Clica no botão de exportar/download
            await page.click("text=Export") 
            # Se abrir um menu, clicamos em CSV. Se for direto, o Playwright captura.
            try:
                await page.click("text=CSV", timeout=5000)
            except:
                pass 
                
        download = await download_info.value
        csv_path = "dados.csv"
        await download.save_as(csv_path)
        print(f"✅ Arquivo baixado: {csv_path}")

        # 4. Enviar para o GitHub
        print("⬆️ Subindo para o GitHub...")
        with open(csv_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        g = Github(os.getenv("GH_TOKEN"))
        repo = g.get_repo(REPO_NAME)
        file = repo.get_contents("dados.csv")
        repo.update_file(file.path, "🔄 Sync Automático Databricks", content, file.sha)
        
        await browser.close()
        print("🎉 Missão cumprida!")

if __name__ == "__main__":
    asyncio.run(extrair_dados())
