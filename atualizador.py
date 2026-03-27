import asyncio
from playwright.async_api import async_playwright
import os
from github import Github

URL_DATABRICKS = "https://dbc-53bd5b4a-ac3c.cloud.databricks.com/editor/queries/3841745429257799?o=1323332079465250"

async def executar_automacao():
    async with async_playwright() as p:
        print("🎬 Iniciando navegador...")
        browser = await p.chromium.launch(headless=True)
        # Forçamos um tamanho de tela padrão para os botões aparecerem no mesmo lugar
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        try:
            print("🔗 Acessando Databricks...")
            await page.goto(URL_DATABRICKS, wait_until="networkidle")

            # 1. Clique no SSO (Baseado na imagem do botão azul)
            print("🔘 Procurando botão de SSO...")
            sso_button = page.get_by_role("button", name="Continue with SSO")
            if await sso_button.is_visible():
                await sso_button.click()
                print("✅ SSO clicado.")
            
            # 2. Esperar o editor e clicar em Run
            print("⚡ Aguardando o botão 'Run'...")
            await page.wait_for_selector('button:has-text("Run")', timeout=60000)
            await page.click('button:has-text("Run")')
            print("✅ Query em execução...")

            # 3. Download (Simulando o fluxo do vídeo)
            print("📥 Aguardando liberação do download...")
            # Procuramos o botão de download pelo ícone (setinha) ou texto
            btn_download = page.locator('button[aria-label="Download"]')
            await btn_download.wait_for(state="visible", timeout=120000)
            
            async with page.expect_download() as download_info:
                await btn_download.click()
                print("🖱️ Menu de download aberto...")
                await page.get_by_text("Download CSV").click()
                await page.get_by_text("All rows").click()

            download = await download_info.value
            path = "dados.csv"
            await download.save_as(path)
            print(f"✅ Arquivo salvo: {path}")

            # 4. Upload para o GitHub
            print("⬆️ Enviando para o GitHub...")
            g = Github(os.getenv("GH_TOKEN"))
            repo = g.get_repo("leonardomartins-create/Contas-sem-Documento")
            file = repo.get_contents("dados.csv")
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            repo.update_file(file.path, "🔄 Update Automático Databricks", content, file.sha)
            print("🎉 Processo finalizado com sucesso!")

        except Exception as e:
            print(f"❌ Erro durante a execução: {e}")
            # Tira um print do erro para ajudar no diagnóstico
            await page.screenshot(path="erro_debug.png")
            raise e
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(executar_automacao())
