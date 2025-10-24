import psycopg2
from flask import Flask, render_template, url_for

app = Flask(__name__)

def dbaction(selection, query):
    datas=None
    try:
        connection = psycopg2.connect(
            host="127.0.0.1",
            user="postgres",
            password="postgres",
            database="postgres")
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(query) # <--- сюда передается SQL запрос
            connection.commit()
            if selection==1:
                datas=cursor.fetchall()
    except Exception as _ex:
        print ('Error:', _ex)
    finally:
        if connection:
            connection.close()
    return datas
def genreslist():
    genres=dbaction(1, '''SELECT * FROM genres''')
    return genres
def chgenrelist(choisengenre):
    cgl=[(0, 0, 0, choisengenre, 0)]
    query="SELECT * FROM books WHERE genre='" + choisengenre + "' ORDER BY numingenre"
    cgl=cgl + dbaction(1, query)
    if cgl > [(0, 0, 0, choisengenre, 0)]:
        for i in range(len(cgl)-1):
            if cgl[i][2]==cgl[i+1][2]:
                ad=(cgl[i][0], cgl[i][1], 'еще', cgl[i][3], cgl[i][4])
                cgl[i]=ad
    else:
        cgl=[]
    return cgl
def bookslist():
    books=[]
    gl=genreslist()
    for i in range(len(gl)):
        books=books+chgenrelist(gl[i][1])
    return books

@app.route('/library')
def index ():
    books = bookslist()
    return render_template("library.html", bookslistprint=books)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=1001) # на деплое должно быть (debug=False, host='0.0.0.0', port=1001)