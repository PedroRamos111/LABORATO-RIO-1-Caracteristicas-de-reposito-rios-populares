import requests
from datetime import datetime
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import langcodes
import csv

# Para resultados consistentes
DetectorFactory.seed = 0

# Configurações da API
GITHUB_API_URL = "https://api.github.com/graphql"
TOKEN = ""

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
          createdAt
          stargazers {
            totalCount
          }
          releases {
            totalCount
          }
          primaryLanguage {
            name
          }
          object(expression: "HEAD:README.md") {
            ... on Blob {
              text
            }
          }
        }
      }
    }
  }
}
"""

# Variável para paginação
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

# Processar os dados para detectar o idioma do README.md e salvar as informações em um arquivo csv
idiomas = []
with open('DadosRQextra.csv', mode='w', newline='') as arquivo_csv:
    writer = csv.writer(arquivo_csv)
    writer.writerow(["Nome do Repositório", "Estrelas", "Idioma"])
    for index, repo in enumerate(resultados, start=1):
        repo_data = repo['node']
        readme_text = repo_data['object']['text'] if repo_data['object'] else ""
        
        if readme_text:
            try:
                idioma_sigla = detect(readme_text)
                idioma_nome_completo = langcodes.Language.get(idioma_sigla).display_name()
            except LangDetectException:
                idioma_nome_completo = "Não detectado"
        else:
            idioma_nome_completo = "README.md ausente"
        
        idiomas.append(idioma_nome_completo)
        writer.writerow([repo_data['name'], repo_data['stargazers']['totalCount'], f"{idioma_nome_completo}"])

print("Os dados foram salvos no arquivo 'DadosRQextra.csv'.")