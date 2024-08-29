import requests
import csv

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

# Dicionário para contar a quantidade de cada linguagem
contagem_linguagens = {}

# Processar os dados e salvar as informações em um arquivo CSV
with open('DadosRQ05.csv', mode='w', newline='') as arquivo_csv:
    writer = csv.writer(arquivo_csv)
    writer.writerow(["Nome do Repositório", "Estrelas", "Linguagem Principal"])

    for index, repo in enumerate(resultados, start=1):
        repo_data = repo['node']
        linguagem = repo_data['primaryLanguage']['name'] if repo_data['primaryLanguage'] else "Não especificada"
        
        # Incrementa a contagem da linguagem
        if linguagem in contagem_linguagens:
            contagem_linguagens[linguagem] += 1
        else:
            contagem_linguagens[linguagem] = 1
        
        writer.writerow([repo_data['name'], repo_data['stargazers']['totalCount'], linguagem])

print(f"Dados das linguagens principais dos repositórios foram salvos no arquivo 'DadosRQ05.csv'.")

# Imprimir a contagem de cada linguagem
print("\nContagem de repositórios por linguagem:")
for linguagem, contagem in contagem_linguagens.items():
    print(f"{linguagem}: {contagem} repositórios")
