import time

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

#O site utiliza o modelo de paginação, logo esta função é usada para percorer todas as páginas
def pegarTodosOsCursos(html):
   pagina = 1
   todos_itens = []

#Substituir por While true para percorrer todas as páginas ( Demora mais )
   while pagina == 1:
      if pagina == 1:
         url = html  # primeira página não tem ?pagina=1
      else:
         url = f"{html}?pagina={pagina}"
      print(f"Scraping página {pagina}: {url}")
      response = requests.get(url)
      soup = BeautifulSoup(response.text, 'html.parser')

      itens = soup.find_all('article')  # ajusta aqui para seu seletor correto

      if not itens:
         break

      todos_itens.extend(itens)

      time.sleep(1)  # pausa de 1 segundo entre as páginas
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

   # A duração e nível tem html igual então um for pra pegar os dois e printar
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
      return

   for item in itemList:
      #Pega a div que contem a dificuldade
      infoCard = item.find('div', {'class': 'm-info m-card_foot'})
      p = infoCard.find_all('p')
      dificuldadeItem = p[1].find('strong').get_text(strip=True)
      if dificuldadeItem == dificuldadeEsperada:
         itemListFiltrada.append(item)

   printList(itemListFiltrada)

def filtroArea(itemList):
   itemListFiltrada = []
   areas = {
      1: "Adm",
      2: "Professional",
      3: "Informatica",
      4: "Finances",
      5: "Visual",
   }

   print("selecione a área")
   selecao = int(input("1.Adm 2.Professional 3.Informatica 4.Finances 5.Visual"))
   print(" ")
   areaEsperada = areas.get(selecao)
   if areaEsperada is None:
      print("Opção invalida")
      return

   for item in itemList:
      areaItem = item.get('class', [])[-1].lstrip('-').capitalize()
      if areaItem == areaEsperada:
         itemListFiltrada.append(item)

   printList(itemListFiltrada)

def pesquisaPalavra(itemList):
   # for item in itemList:
   #    print(item.get_text())
   string = input("Pesquise por cursos: ")
   stringLimpa = string.strip()
   # necessário manter o fr para funcionar
   # {z} identifica pedaços de palavras, \b{z}\b para apenas palavras completas
   regex = fr"\b{re.escape(stringLimpa)}\b"

   i = 0
   print("Cursos relevantes a: " + stringLimpa)
   for item in itemList:
      if re.search(regex, item.get_text(), flags=re.IGNORECASE):
         print(" ")
         i = 1
         printItemInList(item)
   if i == 0:
      print("Sem resultados")





html = 'https://www.ev.org.br/cursos'
baseURL = 'https://www.ev.org.br'

# Pega cada article da página, que são cada card de curso
itemList = pegarTodosOsCursos(html)
#printList(itemList)
# filtroArea(itemList)

loop = True
while loop:
   try:
      choice = int(input("1. Mostrar cursos 2. Filtrar por área 3. Pesquisar curso 4. Fechar programa: "))

      if choice == 1:
         printList(itemList)
      elif choice == 2:
         filtroArea(itemList)
      elif choice == 3:
         pesquisaPalavra(itemList)
      elif choice == 4:
         loop = False
      else:
         print("Entrada inválida.\n")

   except ValueError:
      print("Entrada inválida.\n")

# pesquisaPalavra(itemList)

