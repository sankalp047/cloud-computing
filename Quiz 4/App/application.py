from flask import Flask, render_template, request
import os
import json
from datetime import datetime
import random

# Ref https://www.microsoft.com/en-us/sql-server/developer-get-started/python/mac/step/2.html
import pyodbc

tableCreationObject = None

if os.path.isfile('credentials.json'):
    with open('credentials.json') as f:
        cred = json.load(f)

        db = cred['database'][0]
        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+db['hostname']+';DATABASE='+db['dbname']+';UID='+db['user']+';PWD='+ db['password'])
        cursor = cnxn.cursor()
else:
    print("credentials JSON not initialized")
    exit(1)

app = Flask(__name__)
port = int(os.getenv('PORT', 8000))
# port = 8000

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

@app.route("/api/first", methods=['GET'])
def first():
    query = "select statename from voting WHERE TOTALPOP BETWEEN 5000 and 10000"
    data = search_query(query)
    states = []
    for s in data:
        states.append(s.get('statename'))
    details = [{"label": "Between 5 and 10", "states": str(states)}]
    query = "select statename from voting WHERE TOTALPOP BETWEEN 10000 and 50000"
    data = search_query(query)
    states = []
    for s in data:
        states.append(s.get('statename'))
    details.append({"label": "Between 10 and 50", "states":str(states)})
    return showTable(details)

@app.route("/api/second", methods=['GET'])
def second():
    n_value = int(request.args.get("n"))
    query = "select statename, voted/totalpop as per from voting ORDER BY per"
    data = search_query(query)
    # labels = []
    # final_states = []
    details = []
    i = 40
    while(i < 80):
        j = i+n_value
        label = str(i) + "-" + str(j)
        states = []
        for record in data:
            percent = float(record['per'])*100
            if(percent >= i and percent < j):
                states.append(record['statename'])
        i = i + n_value
        details.append({"states": states, "count": len(states), "label": label})
    return render_template("index.html", pieChartData = details)


@app.route("/api/third", methods=['GET'])
def third():
    n1 = int(request.args.get("n1"))
    n2 = int(request.args.get("n2"))
    details = []
    i = n1
    while(i <= n2):
        x = i
        y = (i*i)+1
        print(y)
        details.append({"x": x, "y": y})
        i = i+1
    return render_template("index.html", scatterGraphData = details)

@app.route("/api/forth", methods=['GET'])
def forth():
    n_value = int(request.args.get("n"))
    query = "select statename, registered from voting ORDER BY registered"
    data = search_query(query)
    details = []
    i = 0
    end = 17
    while(i <= end):
        print(i)
        j = i+n_value
        label = str(i) + "-" + str(j) + " million"
        states = []
        for record in data:
            r = float(record['registered'])/1000
            print(r)
            if(r >= i and r < j):
                states.append(record['statename'])
        i = i + n_value
        details.append({"states": states, "count": len(states), "label": label})
    return render_template("index.html", barGraphVerticalData = details)

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

@app.route("/api/magRangeIteration", methods=['GET'])
def magRangeIteration():
    from_mag = float(request.args.get("from_mag"))
    to_mag = float(request.args.get("to_mag"))
    count = int(request.args.get("count"))
    
    return dbsearch(from_mag, to_mag, count)

@app.route('/barGraphVertical', methods=['GET'])
def barGraphVertical():
    x = [({"label": "Graduates", "value": 300}),({"label": "Undergraduates", "value": 600}),({"label": "Post Graduates", "value": 100})]
    # return render_template("barGraph.html", barGraphVerticalData = x, barGraphHorizontalData = x)
    # return render_template("barGraph.html", barGraphHorizontalData = x)
    return render_template("barGraph.html", scatterGraphData = x)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)