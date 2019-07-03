from flask import Flask, render_template, request
import os
import json
import mysql.connector

db = None

if os.path.isfile('credentials.json'):
    with open('credentials.json') as f:
        cred = json.load(f)
        db = cred['database'][0]

else:
    print("credentials JSON not initialized")
    exit(1)

def get_DbInstance():
    mydb = mysql.connector.connect(
        host = db['hostname'],
        user = db['user'],
        passwd = db['password'],
        database = db['dbname'],
        port = 3306
    )
    return mydb

application = Flask(__name__)

def execute_query(query):
    mydb = get_DbInstance()
    mycursor = mydb.cursor()
    mycursor.execute(query)
    mydb.close()
    return mycursor.fetchall()

def search_query(query):
    mydb = get_DbInstance()
    mycursor = mydb.cursor()
    mycursor.execute(query)
    row_headers=[x[0] for x in mycursor.description] #this will extract row headers
    rv = mycursor.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))
    return json_data


def view_index():
    table = {
        "records": search_query("SELECT * FROM titanic3 LIMIT 10"),
        "title": "titanic3 Table"
    }
    table1 = {
        "records" : [{"name": "nike", "age": 10},{"name": "naman", "age": 20}],
        "title": "Dict"
    }
    table2 = {
        "records" : [{"class": "fucked up"}, {"class" : "hello world"}],
        "title": "Dict2"
    }
    tables = [table1, table2, table]
    return render_template("index.html", tables=tables)

def post_view_handler():
    cluster_count = int(request.form.get("cluster_count"))
    checked = request.form.get("checked")
    return render_template("index.html")

def get_view_handler():
    cluster_count = int(request.args.get("cluster_count"))
    checked = request.args.get("checked")
    return render_template("index.html")

# add a rule for the index page.
application.add_url_rule('/', 'index', view_index)

# application.add_url_rule('/api/clustering', 'postcluster', post_view_handler, methods=["POST"])

# application.add_url_rule('/api/clustering', 'getcluster', get_view_handler, methods=["GET"])

# run the app.
if __name__ == "__main__":
    application.debug = True
    application.run()