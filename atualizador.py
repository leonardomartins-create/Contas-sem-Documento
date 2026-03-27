import asyncio
from playwright.async_api import async_playwright
import os
from github import Github

# URL da sua Query que vimos no vídeo
URL_DATABRICKS = "https://dbc-53bd5b4a-ac3c.cloud.databricks.com/editor/queries/3841745429257799?o=1323332079465250"

async def executar_automacao():
    async with async_playwright() as p:
        print("🎬 Iniciando navegador...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1366, 'height': 768})
        page = await context.new_page()

        # 1. Acesso e Login SSO
        print("🔗 Acessando Databricks...")
        await page.goto(URL_DATABRICKS)
        
        # Clica no botão de SSO (baseado na sua primeira imagem)
        try:
            await page.click('text="Continue with SSO"', timeout=10000)
            print("🔘 SSO clicado.")
        except:
            print("⚠️ Botão SSO não apareceu, tentando seguir...")

        # 2. Espera o carregamento da Query
        await page.wait_for_selector('button:has-text("Run")', timeout=60000)
        print("⚡ Editor carregado. Rodando query...")
        await page.click('button:has-text("Run")')

        # 3. Processo de Download (Exatamente como no vídeo)
        print("⏳ Aguardando resultados para download...")
        # Espera o ícone de download (a setinha para baixo)
        await page.wait_for_selector('button[aria-label="Download"]', timeout=120000)
        
        async with page.expect_download() as download_info:
            print("🖱️ Clicando em Download -> All rows...")
            await page.click('button[aria-label="Download"]')
            # No vídeo, você clica em "Download CSV" -> "All rows"
            await page.click('text="Download CSV"')
            await page.click('text="All rows"')

        download = await download_info.value
        path = "dados.csv"
        await download.save_as(path)
        print(f"✅ Arquivo baixado com sucesso: {path}")

        # 4. Enviar para o GitHub
        print("⬆️ Atualizando o GitHub...")
        g = Github(os.getenv("GH_TOKEN"))
        repo = g.get_repo("leonardomartins-create/Contas-sem-Documento")
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        file = repo.get_contents("dados.csv")
        repo.update_file(file.path, "🔄 Update via Databricks Automático", content, file.sha)
        
        await browser.close()
        print("🎉 Tudo pronto! Dash atualizada.")

if __name__ == "__main__":
    asyncio.run(executar_automacao())
