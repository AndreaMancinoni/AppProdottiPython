from flask import Flask, render_template, request, session, redirect, url_for, make_response
import mysql.connector
import csv
from matplotlib import pyplot as plt
import io
import pandas as pd
import numpy as np

class prodottipets:
    def __init__(self, nome, marca, prezzo, categoria, url, pezzi, pezziVenduti):
        self.nome = nome
        self.marca = marca
        self.prezzo = prezzo
        self.categoria = categoria
        self.url = url
        self.pezzi = pezzi
        self.pezziVenduti = pezziVenduti

class prodottiV:
    def __init__(self, nome, marca, prezzo, url):
        self.nome = nome
        self.marca = marca
        self.prezzo = prezzo
        self.url = url

    def setPezzi(self, pezziV):
        self.pezziV = pezziV

    def getPezzi(self):
        return self.pezziV


USERNAME = "admin"
PASSWORD = "password"


app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Usato per firmare la sessione

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="PyDb"
)

@app.route('/login', methods=['POST', 'GET'])
def login():
    print("--login--")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verifica le credenziali dell'utente
        if username == USERNAME and password == PASSWORD:
            session['user'] = username  # Memorizza l'utente nella sessione
            return redirect(url_for('gestore'))  # Reindirizza all'area protetta
        else:
            return "Credenziali non valide"

    return render_template("login.html")

@app.route('/gestore')
def gestore():
    print("--gestore--")
    if 'user' in session:
        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM prodottipets")


        myresult = mycursor.fetchall()


        query = "SELECT * FROM prodottipets"
        df = pd.read_sql(query, mydb)
        #pd.set_option('display.max_columns', None)
        #pd.set_option('display.max_rows', None, 'display.max_columns', None)
        #df = df.replace({'\r': ''}, regex=True)
        #df_print = df.tostring()
        #print(df.tostring())
        #print(df.info())
        #lista_prodotti = df.values.tolist()
        #print(lista_prodotti)
        sommaP = df['pezzi'].sum()
        sommaV = df['pezziVenduti'].sum()
        print(f"sommaV: {sommaV}")
        print(f"sommaP {sommaP}")

        # Calcolare il prodotto più venduto
        index_max = df['pezziVenduti'].idxmax()  # Ottieni l'indice del valore massimo

        # Calcolare l'indice del prodotto più venduto, escludendo l'ultima riga
        #index_max = df['pezziVenduti'][:-1].idxmax()  # Prende solo le righe fino all'ultima
        index_max = df['pezziVenduti'].idxmax()  # Prende solo le righe fino all'ultima
        #print(f"TEST-INDEX\n{df['pezziVenduti'][:-1]}")
        prodotto_piu_venduto = df.loc[index_max]
        prodottoMax = prodotto_piu_venduto['nome']

        #index_min = df['pezziVenduti'][:-1].idxmin()
        index_min = df['pezziVenduti'].idxmin()
        prodotto_meno_venduto = df.loc[index_min]
        prodottoMin = prodotto_meno_venduto['nome']


        query = "SELECT id, nome, marca, prezzo, categoria, url, pezzi, pezziVenduti  FROM prodottipets"
        mycursor.execute(query)
        myresult1 = mycursor.fetchall()
        # Ottenere i nomi delle colonne
        column_names = [desc[0] for desc in mycursor.description]

        # Creare un DataFrame Pandas con i nomi delle colonne
        df = pd.DataFrame(myresult1, columns=column_names)
        print("prima")
        print(df.to_string())

        mediaP = df['pezzi'].mean()
        print(f"mediaP {mediaP}")
        mediaV = df['pezziVenduti'].mean()
        print(f"mediaV {mediaV}")

        new_row = {
            'id': '',  # Imposta su NaN o su un valore predefinito
            #'nome': np.nan,  # Imposta su NaN o su un valore predefinito
            'nome': '',
            'marca': '',
            'prezzo': '',
            'categoria': '',
            'url': "Somme",  # Imposta su NaN o su un valore predefinito
            'pezzi': sommaP,  # Valore specificato
            'pezziVenduti': sommaV  # Valore specificato
        }


        new_row2 = {
            'id': '',
            'nome': '',
            'marca': '',
            'prezzo': '',
            'categoria': '',
            'url': "Medie",
            'pezzi': round(mediaP,2),
            'pezziVenduti': round(mediaV,2)
        }

        ## Creare un DataFrame dalla nuova riga
        new_row_df = pd.DataFrame([new_row])
        new_row2_df = pd.DataFrame([new_row2])

        # Aggiungere la nuova riga usando pd.concat
        df = pd.concat([df, new_row_df, new_row2_df], ignore_index=True)
        lista_prodotti = df.values.tolist()
        print(lista_prodotti)
        print("dopo")
        print(df.to_string())



        listaD = []
        for i in myresult:
            listaD.append(i[2])

        listaS = list(dict.fromkeys(listaD))
        #print(listaS)
        return render_template("gestore.html", lista = myresult, listaS = listaS, lista_prodotti = lista_prodotti, prodottoMax = prodottoMax, prodottoMin = prodottoMin)
    else:
        return redirect(url_for('login'))

@app.route('/process', methods=['POST', 'GET'])
def process():
    print("--process--")
    if request.method == 'POST':
        nome = request.form['nome']
        print(f"nome: {nome}")
        marca = request.form['marca']
        print(f"marca: {marca}")
        prezzo = request.form['prezzo']
        print(f"prezzo: {prezzo}")
        categoria = request.form['categoria']
        print(f"categoria: {categoria}")
        url = request.form['url']
        print(f"url: {url}")
        pezzi = request.form['pezzi']
        print(f"pezzi: {pezzi}")
        pezziVenduti = 0

        mycursor = mydb.cursor()
        sql = ("INSERT INTO prodottipets (nome, marca, prezzo, categoria, url, pezzi, pezziVenduti) VALUES (%s, %s, %s, %s, %s, %s, %s)")
        val = (nome, marca, prezzo, categoria, url, pezzi, pezziVenduti)
        mycursor.execute(sql, val)

        mydb.commit()

        print(mycursor.rowcount, "record inserted.")

        p1 = prodottipets(nome, marca, prezzo, categoria, url, pezzi, pezziVenduti)

    return render_template("dettagli.html", prod=p1)


@app.route("/remove", methods=['POST', 'GET'])
def remove():
    print("--remove--")
    if request.method == 'POST':
        id = int(request.form['prod'])
        mycursor = mydb.cursor()
        sql = ("DELETE FROM prodottipets WHERE id = %s")
        val = (id,)
        mycursor.execute(sql, val)
        mydb.commit()

        print(mycursor.rowcount, "record removed.")

        return(gestore())

@app.route("/search", methods=['POST', 'GET'])
def search():
    print("--search--")
    if request.method == 'POST':
        marca = request.form['marca']
        mycursor = mydb.cursor()
        sql = "SELECT * FROM prodottipets WHERE marca = (%s)"
        val = (marca,)
        mycursor.execute(sql, val)

        myresult = mycursor.fetchall()

        print(myresult)
        return render_template("stampaMarche.html", lista = myresult)

lista = []
@app.route("/")
def store():
    print("--store--")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM prodottipets")
    myresult = mycursor.fetchall()
    print(f"myresult:\n{myresult}")
    totCarrello = 0
    for i in lista:
        totCarrello += int(i.prezzo) * int(i.getPezzi())
    print(f"lista:\n{lista}")
    print(f"totCarrello:\n{totCarrello}")
    return render_template("store.html", lista = myresult, carrello = lista, totale = totCarrello )

@app.route("/updatePezzi", methods=['POST', 'GET'])
def updatePezzi():
    print("--updatePezzi--")
    if request.method == 'POST':
        id = int(request.form['prodID'])
        pezzi = request.form['Npezzi']
        mycursor = mydb.cursor()
        sql = "UPDATE prodottipets SET pezzi = pezzi + %s  WHERE id = %s"
        val = (pezzi, id)
        mycursor.execute(sql, val)
        mydb.commit()

        print(mycursor.rowcount, "record update.")

        return (gestore())


@app.route("/buy1", methods=['POST', 'GET'])
def buy1():
    print("--buy--")
    if request.method == 'POST':
        listaP = request.form.getlist('prodA')
        print(listaP)
        listaId = request.form.getlist('prodN')
        print(listaId)

    listaPr = []
    listaPrV = []
    for i, num in enumerate(listaP):
        if num != "0":

            mycursor = mydb.cursor()
            sql = "UPDATE prodottipets SET pezzi = pezzi - %s  WHERE id = %s"
            val = (num, listaId[i])
            mycursor.execute(sql, val)
            mydb.commit()

            print(mycursor.rowcount, "record update.")

            mycursor = mydb.cursor()
            sql = "UPDATE prodottipets SET pezziVenduti = pezziVenduti + %s  WHERE id = %s"
            val = (num, listaId[i])
            mycursor.execute(sql, val)
            mydb.commit()

            print(mycursor.rowcount, "record update.")
            listaPr.append(listaId[i])
            listaPrV.append(num)

    listaVendita = []
    totale = 0
    for p1 in listaPr:
        mycursor = mydb.cursor()

        sql = ("SELECT * FROM prodottipets WHERE id = %s")

        val = (p1,)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        for pr2 in myresult:
            p4 = prodottiV(pr2[1], pr2[2], pr2[3], pr2[5])
            listaVendita.append(p4)

        for i, p5 in enumerate(listaVendita):
            p5.setPezzi(listaPrV[i])

        somma = 0
        for i in listaVendita:
            somma += int(i.prezzo) * int(i.getPezzi())


    return render_template("recap.html", lista = listaVendita, somma = somma)


@app.route("/buy", methods=['POST', 'GET'])
def buy():
    print("--buy--")
    if request.method == 'POST':

        for i, p1 in enumerate(lista):
            mycursor = mydb.cursor()
            sql = "UPDATE prodottipets SET pezzi = pezzi - %s  WHERE nome = %s"
            val = (p1.getPezzi(), p1.nome)
            mycursor.execute(sql, val)
            mydb.commit()

            print(mycursor.rowcount, "record update.")

            mycursor = mydb.cursor()
            sql = "UPDATE prodottipets SET pezziVenduti = pezziVenduti + %s  WHERE nome = %s"
            val = (p1.getPezzi(), p1.nome)
            mycursor.execute(sql, val)
            mydb.commit()

            print(mycursor.rowcount, "record update.")

            '''
            mycursor = mydb.cursor()

            mycursor.execute("SELECT * FROM prodotti")

            myresult = mycursor.fetchall()
            idS = (listaId[i])
            for j in myresult:

                if (j[0]) == idS:
                    p1 = prodottiV(j[1], j[2], j[3], j[4], num)
                    print("ciao")
                    listaPr.append(p1)
            '''

    somma = 0
    for i in lista:
        somma += int(i.prezzo) * int(i.getPezzi())

    return render_template("recap.html", lista=lista, somma=somma)

@app.route("/add", methods=['POST', 'GET'])
def add():
    print("--add--")
    id = request.form.get('prodId')
    print(f"id: {id}")
    num = request.form.get('prodA')
    print(f"num: {num}")
    mycursor = mydb.cursor()

    sql = ("SELECT * FROM prodottipets WHERE id = %s")

    val = (id,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()

    for p1 in myresult:
     p2 = prodottiV(p1[1], p1[2], p1[3], p1[5])
     p2.setPezzi(num)
     lista.append(p2)
    

    return(store())

@app.route("/rimuovi", methods=['POST', 'GET'])
def rimuovi():
    print("--rimuovi--")
    if request.method == 'POST':
        nome = request.form['nome']

        for p1 in lista:
            if (p1.nome == nome):
                lista.remove(p1)

    return(store())


@app.route("/savetocsv", methods=['POST', 'GET'])
def savetocsv():
    print("--savetocsv--")
    if request.method == 'POST':
        filecsv = request.form['filecsv']
        print(f"nome: {filecsv}")
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM prodottipets")
        myresult = mycursor.fetchall()
        fp = open(filecsv, 'w', newline='')
        myFile = csv.writer(fp)
        myFile.writerow(['id', 'nome', 'marca', 'prezzo', 'categoria', 'url', 'pezzi', 'pezziVenduti'])
        myFile.writerows(myresult)
        fp.close()

        return f"ok"

@app.route('/combined_chart.png')
def plot_png():
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM prodottipets")

    prodotti = mycursor.fetchall()

    # Estrai le etichette (colonna [1]) e vendite (colonna [7]) dalle tuple
    etichette = [row[1] for row in prodotti]  # Supponiamo che row[1] sia il nome del prodotto
    vendite = [row[6] for row in prodotti]  # Sup

    # Crea una figura con due subplot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 10))  # 1 riga, 2 colonne

    # --- Grafico a barre ---
    ax1.bar(etichette, vendite, color='skyblue')
    ax1.set_title('Vendite per Prodotto (Grafico a Barre)')
    ax1.set_ylabel('Vendite')
    plt.setp(ax1.get_xticklabels(), rotation=90, horizontalalignment='right')

    # --- Grafico a torta ---
    ax2.pie(vendite, labels=etichette, autopct='%1.1f%%', startangle=90, colors=['#ff9999', '#66b3ff', '#99ff99'])
    ax2.axis('equal')  # Per mantenere la torta circolare
    ax2.set_title('Distribuzione Vendite (Grafico a Torta)')
    fig.tight_layout()
    # Salva la figura in memoria come PNG
    output = io.BytesIO()
    fig.savefig(output, format='png')
    plt.close(fig)
    output.seek(0)

    return make_response(output.getvalue(), 200, {'Content-Type': 'image/png'})

if __name__ == '__main__':
   app.run(debug = True)