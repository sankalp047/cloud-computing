from flask import Flask, render_template, request
import os
import json
from datetime import datetime

# Redis
import redis

r = redis.StrictRedis(host='nxv-dns.redis.cache.windows.net',
        port=6380, db=0, password='j+AFTdXNZbULwQabkcz33gT0UwpWTZFEf8sEVSR8XT8=', ssl=True)

# Ref https://www.microsoft.com/en-us/sql-server/developer-get-started/python/mac/step/2.html
import pyodbc
server = 'nxv-assignments.database.windows.net'
database = 'alpha'
username = 'nxv'
password = 'nike@123'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

app = Flask(__name__)
port = int(os.getenv('PORT', 8000))

# header = ["hello", "world"]

def execute_query(query):
    try:
        return cursor.execute(query)
    except:
        return {"Error": "Error in search query function"}

def search_query(query):
    try:
        records = cursor.execute(query)
        rows = []
        for row in records:
            record = ({})
            for index, key in enumerate(cursor.description):
                record.update({key[0]: row[index]})
            rows.append(record)
        return records
    except:
        return {"Error": "Error in search query function"}

def calculate_timings(n_time):
    details = []
    sqls = ["SELECT * FROM earthquakes", "SELECT * FROM earthquakes WHERE latitude between -90 to 0"]
    labels = ["Query without restriction", "Query with restriction"]
    for i, sql in enumerate(sqls):
        detail = ({})
        start = datetime.now()
        for j in range(n_time):
            rows = search_query(sql)
        time = datetime.now() - start
        detail.update({"label": labels[i], "time": time})
        details.append(detail)
    return details

def calculate_timings_redis(n_time):
    details = []
    sqls = ["SELECT * FROM earthquakes", "SELECT * FROM earthquakes WHERE latitude between -90 to 0"]
    labels = ["Query without restriction", "Query with restriction"]
    redis_labels = ["quakesAll", "quakesConditional"]
    for i, sql in enumerate(sqls):
        detail = ({})
        start = datetime.now()
        for j in range(n_time):
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
    details = calculate_timings_redis(n_time)
    return showTable(details)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)