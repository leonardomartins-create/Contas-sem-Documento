import asyncio
from playwright.async_api import async_playwright
import os
from github import Github

# Sua URL do Databricks
URL_DATABRICKS = "https://dbc-53bd5b4a-ac3c.cloud.databricks.com/editor/queries/3841745429257799?o=1323332079465250"

async def executar_automacao():
    async with async_playwright() as p:
        print("🎬 Iniciando navegador...")
        browser = await p.chromium.launch(headless=True)
        # Contexto com resolução alta para garantir que os menus apareçam
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        try:
            print("🔗 Acessando Databricks...")
            await page.goto(URL_DATABRICKS, wait_until="domcontentloaded")

            # 1. Clique no SSO (Tentativa por texto e por papel de botão)
            print("🔘 Verificando login SSO...")
            try:
                # Espera curta para ver se a tela de login aparece
                sso_btn = page.locator('button:has-text("Continue with SSO")')
                await sso_btn.wait_for(state="visible", timeout=15000)
                await sso_btn.click()
                print("✅ Botão SSO clicado.")
            except:
                print("ℹ️ Tela de SSO não detectada ou já logado.")

            # 2. Esperar o editor SQL carregar completamente
            print("⚡ Aguardando carregamento da Query...")
            # Esperamos o botão 'Run' ou a barra lateral
            await page.wait_for_selector('button:has-text("Run")', timeout=60000)
            
            # 3. Executar e Baixar (Lógica baseada no seu vídeo)
            print("📥 Localizando botão de download...")
            # No vídeo, o download fica próximo aos resultados
            btn_download = page.locator('button[aria-label="Download"], .sql-editor-results-download-button').first
            await btn_download.wait_for(state="visible", timeout=60000)
            
            async with page.expect_download() as download_info:
                await btn_download.click()
                print("🖱️ Abrindo menu de exportação...")
                # Tenta clicar em CSV e depois em All Rows como no vídeo
                await page.get_by_text("Download CSV").click()
                await page.get_by_text("All rows").click()

            download = await download_info.value
            path = "dados.csv"
            await download.save_as(path)
            print(f"✅ Download concluído: {path}")

            # 4. Enviar ao GitHub
            print("⬆️ Atualizando repositório...")
            g = Github(os.getenv("GH_TOKEN"))
            repo = g.get_repo("leonardomartins-create/Contas-sem-Documento")
            file = repo.get_contents("dados.csv")
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            repo.update_file(file.path, "🔄 Sync Automático Databricks", content, file.sha)
            print("🎉 Missão cumprida!")

        except Exception as e:
            print(f"❌ ERRO DETALHADO: {str(e)}")
            # Captura de tela para debug se falhar
            await page.screenshot(path="erro_login.png")
            raise e
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(executar_automacao())
