from datetime import datetime
import requests
import os
import mysql.connector

#print(datetime.now().strftime("%M:%S")) #Mostrar o horário que começa a execução do script

from PyPDF2 import PdfFileReader, PdfFileMerger
from pathlib import Path

d = datetime.now()

ano = d.strftime("%Y")
mes = d.strftime("%m")
diaExtenso = d.strftime("%d") # STR
meses = ['','Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
dia = str(diaExtenso)
if len(dia) == 1:
    dia = "0" + dia

cidadePDF = True
exec1PDF = True
exec2PDF = True

def formatar(n):
    a = 4 - len(str(n))
    return str(a * '0') + str(n)

# CONEXÃO MYSQL E CRIAÇÃO DO BANCO DE DADOS

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="tuca123" # <- SENHA DO MYSQL
)

mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS API_a;")
mycursor.execute("use API_a;")
mycursor.execute("CREATE table IF NOT EXISTS associado( id_associado int not null primary key auto_increment, nome varchar(55), email varchar(256), sexo varchar(10));")
mycursor.execute("Create table IF NOT EXISTS backoffice(id_back int not null primary key auto_increment, nome varchar(55));")
mycursor.execute("Create table IF NOT EXISTS email( id_email int not null primary key auto_increment, fk_id_associado int, corpo text(19999), pagina varchar(999), dataenvio datetime(6), estado bool );")
mycursor.execute("ALTER TABLE email ADD FOREIGN KEY (fk_id_associado) REFERENCES associado(id_associado);")

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="tuca123", # <- SENHA DO MYSQL
  database="API_a"
)

mycursor = mydb.cursor()

mycursor.execute("INSERT INTO associado VALUES (0, 'Marcela','marcela@gmail.com','Feminino');")
mycursor.execute("INSERT INTO associado VALUES (0, 'Vitória','marcela@gmail.com','Feminino');")

mydb.commit()

# BAIXAR PDFS DE HOJE - DIARIO OFICIAL 

for pag in range(1,9999):

    pagExtenso = formatar(pag)

    link1 = "http://diariooficial.imprensaoficial.com.br/doflash/prototipo/" + ano + "/" + meses[int(mes)] + "/" + dia + "/cidade/pdf/pg_" + pagExtenso + ".pdf"
    link2 = "http://diariooficial.imprensaoficial.com.br/doflash/prototipo/" + ano + "/" + meses[int(mes)] + "/" + dia + "/exec1/pdf/pg_" + pagExtenso + ".pdf"
    link3 = "http://diariooficial.imprensaoficial.com.br/doflash/prototipo/" + ano + "/" + meses[int(mes)] + "/" + dia + "/exec2/pdf/pg_" + pagExtenso + ".pdf"

    if (d.strftime("%w") == 0 or d.strftime("%w") == 1):
        print('Hoje não tem diário oficial')
        exit() # Se for domingo ou segunda, não tem diário oficial

    else:
        if not cidadePDF and not exec1PDF and not exec2PDF:
            break
        print(pagExtenso)

        if cidadePDF == True: # Baixar as páginas do caderno Cidade
            cidade = requests.get(link1)
            open("./paginas/cidade" + pagExtenso + ".pdf", "wb").write(cidade.content)
            f = open("./paginas/cidade" + pagExtenso + ".pdf", "r")
            if f.readline()[0:8] != "%PDF-1.4":
                if pagExtenso == "0001":
                    print("Hoje não tem diário oficial")
                else:
                    print('Ultima página do caderno "Cidade": ', int(pagExtenso) - 1)
                f.close()
                if os.path.exists("./paginas/cidade" + pagExtenso + ".pdf"):
                    os.remove("./paginas/cidade" + pagExtenso + ".pdf")
                    cidadePDF = False

        if exec1PDF == True: #Baixar as páginas do caderno Executivo 1
            exec1 = requests.get(link2)
            open("./paginas/exec1" + pagExtenso + ".pdf", "wb").write(exec1.content)
            f = open("./paginas/exec1" + pagExtenso + ".pdf", "r")

            if f.readline()[0:8] != "%PDF-1.4":
                if pagExtenso == "0001":
                    print("Hoje não tem diário oficial")
                else:
                    print('Ultima página do caderno "Executivo 1": ', int(pagExtenso) - 1)
                f.close()
                if os.path.exists("./paginas/exec1" + pagExtenso + ".pdf"):
                    os.remove("./paginas/exec1" + pagExtenso + ".pdf")
                    exec1PDF = False

        if exec2PDF == True: # Baixar as páginas do caderno Executivo 2
            exec2 = requests.get(link3)
            open("./paginas/exec2" + pagExtenso + ".pdf", "wb").write(exec2.content)
            f = open("./paginas/exec2" + pagExtenso + ".pdf", "r")

            if f.readline()[0:8] != "%PDF-1.4":
                if pagExtenso == "0001":
                    print("Hoje não tem diário oficial do executivo 2")
                else:
                    print('Ultima página do caderno "Executivo 2": ', int(pagExtenso) - 1 )
                f.close()
                if os.path.exists("./paginas/exec2" + pagExtenso + ".pdf"):
                    os.remove("./paginas/exec2" + pagExtenso + ".pdf")
                    exec2PDF = False

caminho = ".\paginas"

pdfs = sorted(os.listdir(caminho))

# CRIAÇÃO DOS CADERNOS UNINDO OS PDFS DAS PÁGINAS

# CIDADE
pdf_files = [f for f in pdfs if f.startswith("cidade")]
merger = PdfFileMerger()
for nomeArquivo in pdf_files:
    merger.append(PdfFileReader(os.path.join(caminho, nomeArquivo), "rb"))
merger.write(os.path.join(caminho, f"Caderno_cidade_{diaExtenso}_{mes}.pdf"))

# EXEC1
pdf_files = [f for f in pdfs if f.startswith("exec1")]
merger = PdfFileMerger()
for nomeArquivo in pdf_files:
    merger.append(PdfFileReader(os.path.join(caminho, nomeArquivo), "rb"))
merger.write(os.path.join(caminho, f"Caderno_exec1_{diaExtenso}_{mes}.pdf"))

# EXEC2
pdf_files = [f for f in pdfs if f.startswith("exec2")]
merger = PdfFileMerger()
for nomeArquivo in pdf_files:
    merger.append(PdfFileReader(os.path.join(caminho, nomeArquivo), "rb"))
merger.write(os.path.join(caminho, f"Caderno_exec2_{diaExtenso}_{mes}.pdf"))

#EXCLUIR PDFS DE PÁGINAS

pdf_files = [f for f in pdfs if f.startswith("cidade") or f.startswith("exec1") or f.startswith("exec2")]
for nomeArquivo in pdf_files:
    os.remove(os.path.join(caminho, nomeArquivo))

mycursor.execute("SELECT id_associado, nome FROM associado")

nomes = mycursor.fetchall()
if nomes == []:
    print("Nenhum associado cadastrado")
    exit()
#print(nomes)
txt = ''


# FAZER A BUSCA NO PDF CIDADE E ENVIAR PARA O BANCO DE DADOS

reader = PdfFileReader(f'./paginas/Caderno_cidade_{diaExtenso}_{mes}.pdf')
data = f'{ano}-{mes}-{dia}'

nomeTeste = 'Marcela'
txt = ''

for i in range(reader.getNumPages()):
    pagina = reader.getPage(i)
    numpag = formatar(i + 1)
    conteudo = pagina.extractText()
    for paragrafo in conteudo.replace('"',"'").split('\n'):
        for nome in nomes:
            if nome[1].upper() in paragrafo.upper():
                link1 = "http://diariooficial.imprensaoficial.com.br/doflash/prototipo/" + ano + "/" + meses[int(mes)] + "/" + dia + "/cidade/pdf/pg_" + str(numpag) + ".pdf"
                #print(f'INSERT INTO email VALUES (0,{nome[0]},"{paragrafo}","{link1}","{data}",0);')
                #txt += f"Página: Cidade\nPágina: {numpag}\nLink:{link1}\nParágrafo: {paragrafo}"
                mycursor.execute(f'INSERT INTO email VALUES ( 0, {nome[0]}, "{paragrafo}", "{link1}", "{data}", 0);')

# FAZER A BUSCA NO PDF EXEC1 E ENVIAR PARA O BANCO DE DADOS

reader = PdfFileReader(f'./paginas/Caderno_exec1_{diaExtenso}_{mes}.pdf')

for i in range(reader.getNumPages()):
    pagina = reader.getPage(i)
    numpag = formatar(i + 1)
    conteudo = pagina.extractText()
    for paragrafo in conteudo.replace('"',"'").split('\n'):
        for nome in nomes:
            if nome[1].upper() in paragrafo.upper():
                link2 = "http://diariooficial.imprensaoficial.com.br/doflash/prototipo/" + ano + "/" + meses[int(mes)] + "/" + dia + "/exec1/pdf/pg_" + str(numpag) + ".pdf"
                #txt += f"Página: Executivo 1\nPágina: {numpag}\nLink:{link2}\nParágrafo: {paragrafo}"
                mycursor.execute(f'INSERT INTO email VALUES (0,{nome[0]},"{paragrafo}","{link2}", "{data}", 0)')

# FAZER A BUSCA NO PDF EXEC2 E ENVIAR PARA O BANCO DE DADOS

reader = PdfFileReader(f'./paginas/Caderno_exec2_{diaExtenso}_{mes}.pdf')

for i in range(reader.getNumPages()):
    pagina = reader.getPage(i)
    numpag = formatar(i + 1)
    conteudo = pagina.extractText()
    for paragrafo in conteudo.replace('"',"'").split('\n'):
        for nome in nomes:
            if nome[1].upper() in paragrafo.upper():
                link3 = "http://diariooficial.imprensaoficial.com.br/doflash/prototipo/" + ano + "/" + meses[int(mes)] + "/" + dia + "/exec2/pdf/pg_" + str(numpag) + ".pdf"
                #txt += f"Página: Executivo 2\nPágina: {numpag}\nLink:{link3}\nParágrafo: {paragrafo}"
                mycursor.execute(f'INSERT INTO email VALUES (0,{nome[0]},"{paragrafo}","{link3}", "{data}", 0)')

mydb.commit() # :D

# TRANSFORMAR EM TXT -

# with Path(f'_{diaExtenso}_{mes}.txt').open(mode = 'w', encoding='utf-8') as output_file:
#     output_file.write(txt)

print("\nACABOU\n")

#print(datetime.now().strftime("%M:%S")) #Mostrar o horário de término de execução do script