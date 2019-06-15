from flask import Flask, render_template, request
import os
import json
from datetime import datetime

# Ref https://www.microsoft.com/en-us/sql-server/developer-get-started/python/mac/step/2.html
import pyodbc

# Redis
import redis

if os.path.isfile('credentials.json'):
    with open('credentials.json') as f:
        cred = json.load(f)

        db = cred['database'][0]
        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+db['hostname']+';DATABASE='+db['dbname']+';UID='+db['user']+';PWD='+ db['password'])
        cursor = cnxn.cursor()

        redis_cred = cred['redis'][0]
        r = redis.StrictRedis(host=redis_cred['hostname'], port=redis_cred['port'], db=redis_cred['db'], password=redis_cred['primary_key'], ssl=redis_cred['ssl'])
else:
    print("V-cap JSON not initialized")
    exit(1)

app = Flask(__name__)
port = int(os.getenv('PORT', 8000))

def execute_query(query):
    print("HERE")
    # try:
    return cursor.execute(query)
    # except:
        # return {"Error": "Error in search query function"}

def search_query(query):
    try:
        records = cursor.execute(query)
        rows = []
        for row in records:
            record = ({})
            for index, key in enumerate(cursor.description):
                record.update({key[0]: row[index]})
            rows.append(record)
        return rows
    except:
        return {"Error": "Error in search query function"}

def calculate_timings(n_time, sqls):
    details = []
    labels = ["Query without restriction", "Query with restriction"]
    for i, sql in enumerate(sqls):
        print(i)
        detail = ({})
        start = datetime.now()
        for j in range(n_time):
            print(j)
            rows = search_query(sql)
            # print(len(rows))
            print("-----------")
        time = datetime.now() - start
        detail.update({"label": labels[i], "time": time})
        details.append(detail)
    print("Completed SQL")
    labels = ["Query without restriction with Redis", "Query with restriction with Redis"]
    redis_labels = ["quakesAll1", "quakesConditional1"]
    sanity = ({})
    for i, sql in enumerate(sqls):
        print(i)
        detail = ({})
        start = datetime.now()
        for j in range(n_time):
            print(j)
            rows = r.get(redis_labels[i])
            if rows is None:
                rows = search_query(sql)
                r.set(redis_labels[i], str(rows))
            else:
                print("Used Redis")
        time = datetime.now() - start
        detail.update({"label": labels[i], "time": time})
        details.append(detail)
    return details

def showTable(data):
    if len(data) > 0:
        keys = data[0].keys()
    else:
        keys = []
    return render_template("select.html", keys=keys, data=data)

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/select", methods=['GET'])
def select():
    try:
        rows = search_query("SELECT * FROM earthquakes WHERE depth = -3.5600000000000001;")
        return showTable(rows)
    except:
        return showTable({"Error": "Error in select function"})

@app.route("/api/timings", methods=['POST'])
def apiTimings():
    n_time = int(request.form.get("n_time"))
    sqls = [str(request.form.get("q1")), str(request.form.get("q2"))]
    details = calculate_timings(n_time, sqls)
    return showTable(details)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)