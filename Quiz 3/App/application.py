from flask import Flask, render_template, request
import os
import json
from datetime import datetime
import random

# Ref https://www.microsoft.com/en-us/sql-server/developer-get-started/python/mac/step/2.html
import pyodbc

# Redis
import redis

tableCreationObject = None

if os.path.isfile('credentials.json'):
    with open('credentials.json') as f:
        cred = json.load(f)

        db = cred['database'][0]
        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+db['hostname']+';DATABASE='+db['dbname']+';UID='+db['user']+';PWD='+ db['password'])
        cursor = cnxn.cursor()

        redis_cred = cred['redis'][0]
        r = redis.StrictRedis(host=redis_cred['hostname'], port=redis_cred['port'], db=redis_cred['db'], password=redis_cred['primary_key'], ssl=redis_cred['ssl'])
else:
    print("credentials JSON not initialized")
    exit(1)

app = Flask(__name__)
# port = int(os.getenv('PORT', 8000))
port = 8000

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
        return rows
    except:
        return {"Error": "Error in search query function"}

def showTable(data):
    if len(data) > 0:
        keys = data[0].keys()
    else:
        keys = []
    return render_template("select.html", keys=keys, data=data)

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/api/magRange", methods=['GET'])
def magRange():
    from_mag = int(request.args.get("from_mag"))
    to_mag = int(request.args.get("to_mag"))
    query = "select place, cast(replace(cast(time as nvarchar(max)),'Z','') as date) as 'date', mag FROM quake3 WHERE mag BETWEEN " + str(from_mag) + " AND " + str(to_mag) 
    details = search_query(query)
    return showTable(details)

def dbsearch(from_mag, to_mag, count):
    det = []
    for i in range(count):
        diff = to_mag - from_mag
        mag1 = round(random.random()*diff + from_mag, 1)
        mag2 = round(random.random()*diff + from_mag, 1)
        l_mag = mag1 if mag1 < mag2 else mag2
        h_mag = mag1 if mag1 >= mag2 else mag2
        query = "select place, cast(replace(cast(time as nvarchar(max)),'Z','') as date) as 'date', mag FROM quake3 WHERE mag BETWEEN " + str(l_mag) + " AND " + str(h_mag) 
        start = datetime.now()
        details = search_query(query)
        time = (datetime.now() - start).total_seconds()
        det.append({'from': str(l_mag), 'to': str(h_mag), 'count': len(details), 'time': time})
    
    return showTable(det)

def redisSearch(from_mag, to_mag, count):

    det = []
    for i in range(count):
        diff = to_mag - from_mag
        mag1 = round(random.random()*diff + from_mag, 1)
        mag2 = round(random.random()*diff + from_mag, 1)
        l_mag = mag1 if mag1 < mag2 else mag2
        h_mag = mag1 if mag1 >= mag2 else mag2
        label = "label_"+str(l_mag)+"_to_"+str(h_mag)
        query = "select place, cast(replace(cast(time as nvarchar(max)),'Z','') as date) as 'date', mag FROM quake3 WHERE mag BETWEEN " + str(l_mag) + " AND " + str(h_mag) 
        start = datetime.now()
        rows = r.get(label)
        if rows is None:
            print("Used Query")
            rows = search_query(query)
            r.set(label, str(rows))
        time = (datetime.now() - start).total_seconds()
        det.append({'from': str(l_mag), 'to': str(h_mag), 'count': len(rows), 'time': time})
    
    return showTable(det)


@app.route("/api/magRangeIteration", methods=['GET'])
def magRangeIteration():
    from_mag = float(request.args.get("from_mag"))
    to_mag = float(request.args.get("to_mag"))
    count = int(request.args.get("count"))
    
    return dbsearch(from_mag, to_mag, count)

@app.route("/api/magRangeIterationRedis", methods=['GET'])
def magRangeIterationRedis():
    from_mag = float(request.args.get("from_mag"))
    to_mag = float(request.args.get("to_mag"))
    count = int(request.args.get("count"))

    return redisSearch(from_mag, to_mag, count)


@app.route("/api/typeoffunction", methods=['GET'])
def typeoffunction():
    from_mag = float(request.args.get("from_mag"))
    to_mag = float(request.args.get("to_mag"))
    count = int(request.args.get("count"))
    option = str(request.args.get("option"))
    if(option == "db"):
        return dbsearch(from_mag, to_mag, count)
    else:
        return redisSearch(from_mag, to_mag, count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)