import time
import json
import requests
from requests.exceptions import HTTPError, RequestException
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

#O site utiliza o modelo de paginação, logo esta função é usada para percorrer todas as páginas
def pegarCursos(html, carregarTodos=False):
   pagina = 1
   todos_itens = []

   while True:
      #Na primeira página não é necessário adicionar ?pagina=1
      if pagina == 1:
         url = html
      else:
         url = f"{html}?pagina={pagina}"

      #Tratamento de exceções para erro HTTP ou erro de Requisição
      try:
         response = requests.get(url)
         response.raise_for_status()
      except HTTPError as http_err:
         print(f"Erro HTTP ao acessar {url}: {http_err}")
         return todos_itens
      except RequestException as req_err:
         print(f"Erro de requisição ao acessar {url}: {req_err}")
         return todos_itens

      soup = BeautifulSoup(response.text, 'html.parser')
      itens = soup.find_all('article')

      if not itens:
         return todos_itens

      todos_itens.extend(itens)
      print(f"Buscando cursos na página {pagina}: {url}")
      if not carregarTodos:
         return todos_itens

      time.sleep(1)
      pagina += 1

   return todos_itens

def printItemInList(item):
   # pega cada atributo
   titulo = item.find('h3', {'class': 'm-card_title'})
   descricao = item.find('p', {'class': 'm-card_desc'})
   infoCard = item.find('div', {'class': 'm-info m-card_foot'})
   linkCurso = item.find('a', {'class': 'm-card_link'})
   area = item.get('class', [])
   linkCurso = urljoin(baseURL, linkCurso['href'])
   textoArrea = area[-1].lstrip('-').capitalize()
   textoDescricao = descricao.get_text(separator=' ', strip=True)
   textoDescricao = ' '.join(textoDescricao.split())
   # printa os dados
   print("Curso: " + titulo.get_text())
   print("Descrição: " + textoDescricao)
   print("Área: " + textoArrea)
   print("Link de acesso: " + linkCurso)

   # A duração e nível tem html igual então um for para pegar os dois e printar
   for tag in infoCard.select('p'):
      print(tag.get_text())
   print(" ")

def printList(itemList):
   for item in itemList:
      printItemInList(item)

def filtroDificuldade(itemList):
   itemListFiltrada = []
   dificuldades = {
      1: "Iniciante",
      2: "Intermediário",
      3: "Avançado"
   }
   print("selecione a dificuldade")
   selecao = int(input("1.Iniciante  2.Intermediário  3.Avançado"))
   dificuldadeEsperada = dificuldades.get(selecao)

   if dificuldadeEsperada is None:
      print("Opção inválida")
      return itemList

   for item in itemList:
      #Pega a div que contem a dificuldade
      infoCard = item.find('div', {'class': 'm-info m-card_foot'})
      p = infoCard.find_all('p')

      #Isola apenas a palavra referente a dificuldade
      dificuldadeItem = p[1].find('strong').get_text(strip=True)
      if dificuldadeItem == dificuldadeEsperada:
         itemListFiltrada.append(item)

   #Caso não encontre itens dessa dificuldade
   if itemListFiltrada is None:
      print("Nenhum item foi encontrado")
      return itemList

   printList(itemListFiltrada)
   return itemListFiltrada

def filtroArea(itemList):
   itemListFiltrada = []
   areas = {
      1: "Adm",
      2: "Professional",
      3: "Informatic",
      4: "Finances",
      5: "Visual",
   }

   print("selecione a área")
   selecao = int(input("1.Adm 2.Professional 3.Informatica 4.Finances 5.Visual"))
   print(" ")
   areaEsperada = areas.get(selecao)
   if areaEsperada is None:
      print("Opção invalida")
      return itemList

   for item in itemList:
      #Pega a última classe do article que contem o curso, remove o - e coloca a primeira letra maiúscula
      areaItem = item.get('class', [])[-1].lstrip('-').capitalize()
      if areaItem == areaEsperada:
         itemListFiltrada.append(item)

   #Caso não encontre itens dessa área
   if itemListFiltrada is None:
      print("Nenhum item foi encontrado")
      return itemList
   printList(itemListFiltrada)
   return itemListFiltrada

def pesquisaPalavra(itemList):
   string = input("Pesquise por cursos: ")
   stringLimpa = string.strip()
   # necessário manter o fr para funcionar
   # {z} identifica pedaços de palavras, \b{z}\b para apenas palavras completas
   regex = fr"\b{re.escape(stringLimpa)}\b"
   itemListFiltrada = []
   i = 0
   print("Cursos relevantes a: " + stringLimpa)
   # passa pela lista de itens procurando a palavra digitada, salva os cursos que possuem essa palavra e printa
   for item in itemList:
      if re.search(regex, item.get_text(), flags=re.IGNORECASE):
         print(" ")
         i = 1
         printItemInList(item)
         itemListFiltrada.append(item)
   if i == 0:
      print("Sem resultados")
      return itemList
   return itemListFiltrada

def salvarEmJson(itemList):
   if itemList is None:
      print("Você não possui itens para salvar")
      return

   nomeArquivo = input("Digite o nome do arquivo para salvar: ") + (".json")
   itemListJson = []
   for item in itemList:
      titulo = item.find('h3', {'class': 'm-card_title'})
      descricao = item.find('p', {'class': 'm-card_desc'})
      infoCard = item.find('div', {'class': 'm-info m-card_foot'})
      linkCurso = item.find('a', {'class': 'm-card_link'})
      area = item.get('class', [])
      linkCurso = urljoin(baseURL, linkCurso['href'])
      textoArrea = area[-1].lstrip('-').capitalize()
      textoDescricao = descricao.get_text(separator=' ', strip=True)
      textoDescricao = ' '.join(textoDescricao.split())
      duracao = None
      for tag in infoCard.select('p'):
         if duracao is None:
            duracao = tag.find('strong').get_text(strip=True)
         else:
            nivel = tag.find('strong').get_text(strip=True)
      itemJson = {
         "Curso": titulo.get_text(),
         "Descricao": textoDescricao,
         "Area": textoArrea,
         "LinkCurso": linkCurso,
         "Duracao": duracao,
         "Nivel": nivel
      }
      itemListJson.append(itemJson)

   with open(nomeArquivo, 'w', encoding='utf-8') as f:
      json.dump(itemListJson, f, ensure_ascii=False, indent=4)
   print("Itens salvos no arquivo: " + nomeArquivo)

html = 'https://www.ev.org.br/cursos'
baseURL = 'https://www.ev.org.br'

# Pega cada article da página, que são cada card de curso
itemList = pegarCursos(html)
itemListManipulada = itemList
if len(itemList) > 0:
   loop = True
else:
   loop = False
while loop:
   try:
      choice = int(input("1.Mostrar cursos 2.Filtrar por área 3.Pesquisar curso 4.Carregar mais páginas: 5.Salvar JSON 6.Sair sem salvar: "))

      if choice == 1:
         itemListManipulada = printList(itemList)
      elif choice == 2:
         itemListManipulada = filtroArea(itemList)
      elif choice == 3:
         itemListManipulada = pesquisaPalavra(itemList)
      elif choice == 4:
         itemList = pegarCursos(html, carregarTodos=True)
         itemListManipulada = itemList
         print("Todas as páginas foram carregadas!\n")
      elif choice == 5:
         salvarEmJson(itemListManipulada)
         loop = False
      elif choice == 6:
         print("Saindo...")
         loop = False
      else:
         print("Entrada inválida.\n")

   except ValueError:
      print("Entrada inválida.\n")