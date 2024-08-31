import numpy as np
import requests
import csv
from datetime import datetime
from scipy import stats

# Configurações da API
GITHUB_API_URL = "https://api.github.com/graphql"
TOKEN = ""  # Substitua pelo seu token

headers = {"Authorization": f"Bearer {TOKEN}"}

# Função para executar a consulta GraphQL
def run_query(query, variables={}):
    request = requests.post(GITHUB_API_URL, json={'query': query, 'variables': variables}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(f"Query failed to run by returning code of {request.status_code}. {query}")

# Consulta GraphQL para coletar dados dos repositórios
query = """
query ($after: String) {
  search(query: "stars:>1", type: REPOSITORY, first: 10, after: $after) {
    repositoryCount
    pageInfo {
      endCursor
      hasNextPage
    }
    edges {
      node {
        ... on Repository {
          name
          stargazers {
            totalCount
          }
          pullRequests(states: MERGED) {
            totalCount
          }
          releases {
            totalCount
          }
          updatedAt
          primaryLanguage {
            name
          }
        }
      }
    }
  }
}
"""

variables = {"after": None}
resultados = []
total_repos = 0
max_repos = 1000

# Coletar dados de até 1000 repositórios
while total_repos < max_repos:
    result = run_query(query, variables)
    data = result['data']['search']
    resultados.extend(data['edges'])
    total_repos += len(data['edges'])
    if not data['pageInfo']['hasNextPage'] or total_repos >= max_repos:
        break
    variables['after'] = data['pageInfo']['endCursor']

resultados = resultados[:max_repos]

# Dicionários para armazenar os dados por linguagem
dados_por_linguagem = {}

# Processar os dados e organizar por linguagem
for repo in resultados:
    repo_data = repo['node']
    linguagem = repo_data['primaryLanguage']['name'] if repo_data['primaryLanguage'] else "Não especificada"
    
    if linguagem not in dados_por_linguagem:
        dados_por_linguagem[linguagem] = {
            "pull_requests": [],
            "releases": [],
            "tempos_atualizacao": []
        }
    
    # Coleta de dados
    pr_aceitas = repo_data['pullRequests']['totalCount']
    total_releases = repo_data['releases']['totalCount']
    data_ultima_atualizacao = datetime.strptime(repo_data['updatedAt'], '%Y-%m-%dT%H:%M:%SZ')
    tempo_atualizacao_segundos = (datetime.utcnow() - data_ultima_atualizacao).total_seconds()
    tempo_atualizacao_horas = tempo_atualizacao_segundos / 3600  
    
    # Adiciona os dados ao dicionário
    dados_por_linguagem[linguagem]["pull_requests"].append(pr_aceitas)
    dados_por_linguagem[linguagem]["releases"].append(total_releases)
    dados_por_linguagem[linguagem]["tempos_atualizacao"].append(tempo_atualizacao_horas)

# Análise Estatística por Linguagem
with open('DadosRQ07.csv', mode='w', newline='') as arquivo_csv:
    writer = csv.writer(arquivo_csv)
    writer.writerow(["Linguagem", "Média PR", "Mediana PR", "Moda PR", "Média Releases", "Mediana Releases", "Moda Releases", "Média Atualização (horas)", "Mediana Atualização (horas)", "Moda Atualização (horas)"])
    
    for linguagem, dados in dados_por_linguagem.items():
        # Pull Requests
        media_pr = np.mean(dados["pull_requests"])
        mediana_pr = np.median(dados["pull_requests"])
        moda_pr = stats.mode(dados["pull_requests"], keepdims=True)
        
        # Releases
        media_releases = np.mean(dados["releases"])
        mediana_releases = np.median(dados["releases"])
        moda_releases = stats.mode(dados["releases"], keepdims=True)
        
        # Tempos de Atualização
        media_atualizacao = np.mean(dados["tempos_atualizacao"])
        mediana_atualizacao = np.median(dados["tempos_atualizacao"])
        moda_atualizacao = stats.mode(dados["tempos_atualizacao"], keepdims=True)
        
        writer.writerow([
            linguagem,
            media_pr, mediana_pr, f"{moda_pr.mode[0]}/{moda_pr.count[0]}",
            media_releases, mediana_releases, f"{moda_releases.mode[0]}/{moda_releases.count[0]}",
            media_atualizacao, mediana_atualizacao, f"{moda_atualizacao.mode[0]}/{moda_atualizacao.count[0]}"
        ])
