import os
import requests
from github import Github

# O GitHub Actions vai preencher essas variáveis automaticamente usando os "Secrets"
SESSION_ID = os.getenv("METABASE_SESSION")
GITHUB_TOKEN = os.getenv("GH_TOKEN")

# Configurações fixas que extraímos do seu link e repositório
METABASE_URL = "https://metabase.asaas.com"
CARD_ID = "10700"
REPO_NAME = "leonardomartins-create/Contas-sem-Documento"
FILE_NAME = "dados.csv"

def atualizar():
    print(f"Refazendo a query no Metabase (Card {CARD_ID})...")
    
    # Endpoint para baixar o CSV direto do Card
    endpoint = f"{METABASE_URL}/api/card/{CARD_ID}/query/csv"
    headers = {"X-Metabase-Session": SESSION_ID}
    
    response = requests.post(endpoint, headers=headers)
    
    if response.status_code == 200:
        print("Dados recebidos! Enviando para o GitHub...")
        
        # Conexão com o GitHub para salvar o arquivo
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        
        # Puxa o arquivo atual para saber o 'sha' (identificador da versão)
        contents = repo.get_contents(FILE_NAME, ref="main")
        
        # Sobrescreve o dados.csv com as informações novas
        repo.update_file(
            path=contents.path,
            message="🔄 Atualização automática de base via Metabase API",
            content=response.text,
            sha=contents.sha,
            branch="main"
        )
        print(f"✅ Arquivo {FILE_NAME} atualizado com sucesso!")
    else:
        print(f"❌ Erro ao acessar Metabase: {response.status_code}")
        print("Isso geralmente acontece se o SESSION_ID expirou.")

if __name__ == "__main__":
    atualizar()
