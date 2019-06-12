from flask import Flask, render_template, request, jsonify
import atexit
import os
import json
import ibm_db
from datetime import datetime

app = Flask(__name__, static_url_path='')

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

if os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        creds = vcap['services']['db2'][0]['credentials']
        conn_str = 'DATABASE='+creds['database']+';HOSTNAME='+creds['host']+';PORT='+str(creds['port'])+';PROTOCOL='+creds['protocol']+';UID='+creds['username']+';PWD='+creds['password']
        print(conn_str)
        storage_details = vcap['services']['storage'][0]['details']
        storage_url = storage_details['endpoint_url']+'/'+storage_details['bucket_name']+'/'
else:
    print("V-cap JSON not initialized")
    exit(1)

def query_update(q):
    try:
        db2conn = ibm_db.connect(conn_str, "", "")
        if db2conn:
            statement = ibm_db.prepare(db2conn, q)
            result = ibm_db.execute(statement)
            print(result)
            ibm_db.close(db2conn)
            return result
    except:
        print("Connection to Database failed")
        exit(1)

def query_search(q):
    # try:
    db2conn = ibm_db.connect(conn_str, "", "")
    if db2conn:
        statement = ibm_db.prepare(db2conn, q)
        ibm_db.execute(statement)
        rows = []
        result = ibm_db.fetch_assoc(statement)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(statement)
        ibm_db.close(db2conn)
        return rows
    else:
        return False
    # except:
    #     print("Connection to Database failed")
    #     exit(1)

def dispSelectData(data):
    if data:
        keys = data[0].keys()
        body = '<table> <tr> '
        for key in keys:
            body += '<th> ' + str(key) + '</th>'
        body += '</tr>'
        for record in data:
            body += '<tr>'
            for key in keys:
                if record.get(key) is not None:
                    if str(key).lower() == "picture" or str(key).lower() == "image":
                        body += '<td> <img src = "' + storage_url + str(record.get(key)) + '" width=150 height=150 alt = "No image found"/> </td>'
                    else:
                        body += '<td> ' + str(record.get(key)) + '</td>'
                else:
                    body += '<td> </td>'
            body += '</tr>'
        body += '</table>'
        return body
    else:
        return '<h3> No records found </h3>'

header_html = '<html> <head> <title> Quiz 2 </title> </head> <body> <h1> ID: 1001670153 </h1> <h1> Name: Vimal Kumar, Naman Jain </h1> <br />'


@app.route('/')
def root():
    body_html = '<table> <tr> <th> Count </th> <td> Total number of Quakes = '
    q = "SELECT COUNT(*) AS COUNT FROM QUAKES"
    rows = query_search(q)
    body_html = '<table> <tr> <th> Count </th> <td> Total number of Quakes = '+str(rows[0]['COUNT'])+'</td> </tr> '
    q = "SELECT PLACE, LATITUDE, LONGITUDE FROM QUAKES WHERE MAG = (SELECT MAX(MAG) FROM QUAKES WHERE 1)"
    rows = query_search(q)
    body_html += '<table> <tr> <th> MAX MAG QUAKE </th> <td> Place: '+str(rows[0]['PLACE'])+' <br /> <td> Location(Lat, Long): ('+str(rows[0]['LATITUDE'])+ ', ' + str(rows[0]['LONGITUDE']) + ') </td> </tr>'

    body_html += '<tr> <th> Input Mag Range </th> <td> <form method="POST" action="/api/magRange"> <label> From: </label> <input type = "text" name="from" id="from" required> <br /> <label> To: </label> <input type = "text" name="to" id="to" required> <br /> <input type="submit"> </form> </td> </tr>'

    body_html += '<tr> <th> Input 2 Locations </th> <td> <form method="POST" action="/api/locRange"> <label> From(lat, long): </label> <input type = "text" name="from_lat" id="from_lat" required>  <input type = "text" name="from_long" id="from_long" required> <br /> <label> To(lat, long): </label> <input type = "text" name="to_lat" id="to_lat" required>  <input type = "text" name="to_long" id="to_long" required> <br /> <input type="submit"> </form> </td> </tr>'
    
    body_html += '<tr> <th> Input Date (Deletion) </th> <td> <form method="POST" action="/api/deleteDate"> <label> Date: </label> <input type = "date" name="delete_date" id="delete_date" required> <br /> <input type="submit"> </form> </td> </tr>'

    body_html += '<tr> <th> Search </th> <td> <form method="POST" action="/api/search"> <label> State: </label> <input type = "text" name="state" id="state" required> <br /> <label> Location(lat, long): </label> <input type = "text" name="lat" id="lat" required>  <input type = "text" name="long" id="long" required>  <input type="submit"> </form> </td> </tr>'
    return header_html+body_html

@app.route('/api/magRange', methods=['POST'])
def apiMagRange():
    from_mag = float(request.form.get("from"))
    to_mag = float(request.form.get("to"))

    start = from_mag
    shift_index = 0.1
    updated_html = '<table> <tr> <th> Range </th> <th> COUNT </th> </tr>'
    while(start <= to_mag):
        q = "SELECT COUNT(*) AS COUNT FROM QUAKES WHERE MAG BETWEEN " + str(start) + " AND " + str(start + 0.1)
        rows = query_search(q)
        updated_html += '<tr> <th> '+str(start) + " AND " + str(start + 0.1) + "</th> <td> " + str(rows[0]['COUNT']) + '</td> </tr>'
        start = start + 0.1

    return header_html+updated_html 

@app.route('/api/locRange', methods=['POST'])
def apiLocRange():
    from_lat = float(request.form.get("from_lat"))
    to_lat = float(request.form.get("to_lat"))
    from_long = float(request.form.get("from_long"))
    to_long = float(request.form.get("to_long"))

    upper_lat = from_lat if from_lat > to_lat else to_lat
    lower_lat = from_lat if from_lat < to_lat else to_lat
    upper_long = from_long if from_long > to_long else to_long
    lower_long = from_long if from_long < to_long else to_long

    q = "SELECT LATITUDE, LONGITUDE, PLACE FROM QUAKES WHERE (LATITUDE BETWEEN " + str(lower_lat) + " AND " + str(upper_lat) + ") AND (LONGITUDE BETWEEN " + str(lower_long) + " AND " + str(upper_long) + ")"
    rows = query_search(q)
    updated_html = dispSelectData(rows)

    return header_html+updated_html 

@app.route('/api/deleteDate', methods=['POST'])
def apiDeleteDate():
    delete_date = datetime.strptime(request.form.get("delete_date"), '%Y-%m-%d').strftime('%Y-%m-%d')

    q = "SELECT COUNT(*) AS COUNT FROM QUAKES WHERE DATE(REPLACE(REPLACE(TIME, 'T', ' '), 'Z', '')) = '" + delete_date + "'" 
    rows = query_search(q)
    count = rows[0]['COUNT']
    q = "DELETE FROM QUAKES WHERE DATE(REPLACE(REPLACE(TIME, 'T', ' '), 'Z', '')) = '" + delete_date + "'" 
    status = query_update(q)
    if status: 
        updated_html = '<br/> <p> Query Executed. Number of rows deleted = ' + str(count) + '</p> '
    else: 
        updated_html = '<br/> <p> Query Failed. Try Again </p> '

    return header_html+updated_html

@app.route('/api/search', methods=['POST'])
def apiSearch():
    state = str(request.form.get("state"))
    lat = float(request.form.get("lat"))
    long_ = float(request.form.get("long"))

    q = "SELECT * FROM QUAKES WHERE (LATITUDE BETWEEN " + str(lat-2) + " AND " + str(lat+2) + ") AND (LONGITUDE BETWEEN " + str(long_-2) + " AND " + str(long_+2) + ") AND LOWER(PLACE) LIKE '%" + str(state.lower()) + "%'"
    rows = query_search(q)
    updated_html = dispSelectData(rows)

    return header_html+updated_html 


@atexit.register
def shutdown():
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
