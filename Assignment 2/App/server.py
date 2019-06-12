from flask import Flask, render_template, request, jsonify
import ibm_db
import atexit
import os
import json
import math
import degrees as GEO
from datetime import datetime

app = Flask(__name__, static_url_path='')

db_name = 'mydb'
table_name = "EARTHQUAKES"

port = int(os.getenv('PORT', 8000))

if os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        creds = vcap['services']['db2'][0]['credentials']
        conn_str = 'DATABASE='+creds['database']+';HOSTNAME='+creds['host']+';PORT='+str(creds['port'])+';PROTOCOL='+creds['protocol']+';UID='+creds['username']+';PWD='+creds['password']
        
        storage_details = vcap['services']['storage'][0]['details']
        storage_url = storage_details['endpoint_url']+'/'+storage_details['bucket_name']+'/'
else:
    print("V-cap JSON not initialized")
    exit(1)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def query_search(q):
    try:
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
    except:
        print("Connection to Database failed")
        exit(1)

def query_update(q):
    try:
        db2conn = ibm_db.connect(conn_str, "", "")
        if db2conn:
            statement = ibm_db.prepare(db2conn, q)
            result = ibm_db.execute(statement)
            ibm_db.close(db2conn)
            return result
    except:
        print("Connection to Database failed")
        exit(1)

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

def dispUpdateData(data):
    if data:
        keys = data[0].keys()
        body = '<table> <tr> '
        for key in keys:
            body += '<th> ' + str(key) + '</th>'
        body += '<th> Update </th> <th> Delete </th>'
        body += '</tr>'
        for record in data:
            body += '<tr> <form > '
            for key in keys:
                if record.get(key) is not None:
                    if str(key).lower() == "picture" or str(key).lower() == "image":
                        body += '<td> <img src = "' + storage_url + str(record.get(key)) + '" width=150 height=150 alt = "No image found" /> <br /> '
                        body += '<input type="file" id="'+str(key)+'" name="'+str(key)+'" /> </td> <br />'
                    elif str(key).lower() == "id":
                        body += '<td> <input type="text" id="'+str(key)+'" name="'+str(key)+'" value="'+str(record.get(key))+'" readonly> </td> '
                    else:
                        body += '<td> <input type="text" id="'+str(key)+'" name="'+str(key)+'" value="'+str(record.get(key))+'"> </td> '
                else:
                    if str(key).lower() == "picture" or str(key).lower() == "image":
                        body += '<td> <img src = "" width=150 height=150 alt = "No image found" /> <br /> '
                        body += '<input type="file" id="'+str(key)+'" name="'+str(key)+'" /> </td> <br />'
                    elif str(key).lower() == "id":
                        body += '<td> <input type="text" id="'+str(key)+'" name="'+str(key)+'" value="'+str(record.get(key))+'" readonly> </td> '
                    else:
                        body += '<td> <input type="text" id="'+str(key)+'" name="'+str(key)+'" value=""> </td>'
            body += '<td> <input type="submit" name="UPDATE" value="UPDATE" formmethod="POST" formenctype="multipart/form-data" formaction="/api/updateData" /> </td>'
            body += '<td> <input type="submit" name="DELETE" value="DELETE" formmethod="POST" formenctype="multipart/form-data" formaction="/api/DeleteData" /> </td>'
            body += '</form> </tr>'
        body += '</table>'
        return body
    else:
        return '<h3> No records found </h3>'

def constructUpdateQuery(data):
    eliminators = ["ID", "UPDATE", 'DELETE']
    q = "UPDATE "+table_name+" SET "
    for i in data:
        if i not in eliminators:
            val = data.get(i)
            if len(val) > 0:
                int_flag = is_number(val)
                if int_flag:
                    q += i + " = "+ val + ","
                else:
                    q += i + " = '"+ val + "',"
    int_flag = is_number(data.get("ID"))
    if int_flag:
        q = q[:len(q)-1] + " WHERE ID = " + data.get("ID")
    else:
        q = q[:len(q)-1] + " WHERE ID = '" + data.get("ID") + "'"

    result = query_update(q)
    if result:
        html = ' <p> Updated </p> <br /> '
    else:
        html = ' <p> Failed </p> <br /> '
    return html

header_html = '<html> <head> <title> Assignment 2 </title> </head> <body> <h2> <center> Assignment 2 </center> </h2>'
footer_html = '<br /> <h4> By: Naman Jain Vimal Kumar <h4> </body> </html>'

main_html = ('<table> <tr> <th> Query </th> <td> <form action="/api/query" method="GET"> <input type="text" name="query" id="query" required> <input type="submit"> </form> </td> <tr />'
    +'<tr> <th> EarthQuakes more than Magnitude 5.0 </th> <td> <form action = "/api/magnitude?mag=5.0" method="GET"> <input type = "submit"> </form> </td>  <tr />'
    +'<tr> <th> EarthQuakes in groups of magnitude </th> <td> <form action = "/api/dateRange" method="GET"> <input type="date" name="from_date" required>  <input type="date" name="to_date" required> <input type = "submit"> </form> </td>  <tr /> '
    +'<tr> <th> Earthquakes near me </th> <td> <form action="/api/calGeoDistance" method="POST" > <label> Latitude: </label> <input id="lat" type="text" name="latitude" value="latitude" required> '
    +'<label> Longitude: </label> <input type="text" id = "long" name="longitude" value="longitude" required> <label> Distance(km): </label> <input type="text" name="distance" value="distance" required> '
    +'<input type="submit" name="Find"> </form> <br /> <button type-"button" onclick="getMyLocation"> Find my location </button> </td> <script> function getLocation() { if (navigator.geolocation) '
    +'{navigator.geolocation.getCurrentPosition(showPosition);} else { x.innerHTML = "Geolocation is not supported by this browser.";} } function showPosition(position) { x.innerHTML = "Latitude: " + position.coords.latitude + "<br>Longitude: " + position.coords.longitude; }'
    +'</script> </tr> </table> <p id="demo"> </p> ')

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/api/query', methods=['GET'])
def apiQuery():
    q = request.args.get("query")
    data = query_search(q)
    data_html = dispSelectData(data)
    return header_html + main_html + data_html + footer_html

@app.route('/api/updateData', methods=['POST'])
def apiUpdateData():
    update_html = constructUpdateQuery(request.form)
    return header_html + main_html + update_html + footer_html

@app.route('/api/deleteData', methods=['POST'])
def apiDeleteData():
    if(is_number(forms.get("ID"))):
        q = "DELETE FROM " + table_name + " WHERE ID = " + forms.get("ID")
    else:
        q = "DELETE FROM " + table_name + " WHERE ID = '" + forms.get("ID") + "'"
    result = query_update(q)
    if result:
        update_html = ' <p> Deleted </p> <br /> '
    else:
        update_html = ' <p> Failed </p> <br /> '
    return header_html + main_html + update_html + footer_html

@app.route('/api/magnitude', methods=['GET'])
def apiMagnitude():
    magnitude = 5.0
    q = "SELECT * FROM EARTHQUAKES WHERE MAG > " + str(magnitude)
    data = query_search(q)
    data_html = '<br /> <p> <b> Number of earthquaqes more than 5.0 magnitude is equal to ' + str(len(data)) + ' <p> </b> <br />'
    data_html += dispSelectData(data)
    return header_html + main_html + data_html + footer_html

@app.route('/api/dateRange', methods=['GET'])
def apiDataRange():
    from_date = datetime.strptime(request.args.get("from_date"), '%Y-%m-%d').strftime('%d-%m-%Y')
    to_date = datetime.strptime(request.args.get("to_date"), '%Y-%m-%d').strftime('%d-%m-%Y')
    data1_html = '<table> <tr> <th> Range </th> <th> Number of EarthQuakes </th> </tr>'
    data2_html = ''
    for i in range(-4, 19, 1):
        q = "SELECT * FROM EARTHQUAKES WHERE MAG BETWEEN " + str(float(i)/2) + " AND " + str(float(i+1)/2) + " AND DATE(REPLACE(REPLACE(TIME, 'T', ' '), 'Z', '')) BETWEEN DATE(TO_DATE('"+from_date+"','DD-MM-YYYY')) AND DATE(TO_DATE('"+to_date+"','DD-MM-YYYY'))"
        data = query_search(q)
        data1_html += '<tr> <th> ' + str(float(i/2)) + " AND " + str(float(i+1)/2) + " </th> <th> " + str(len(data)) + " </th> </tr> "
        data2_html += '<br /> <br /> <p> Date from ' + str(float(i/2)) + " and " + str(float(i+1)/2) + " magnitude: </br> </p>"
        if len(data) > 0:
            data2_html += dispSelectData(data)
        else:
            data2_html += "<p> No data </p>"
    data1_html += '</table>'
    return header_html + main_html + data1_html + data2_html + footer_html

@app.route('/api/calGeoDistance', methods=['POST'])
def apiCalGeoDistance():
    latitude = float(request.form.get("latitude"))
    longitude = float(request.form.get("longitude"))
    distance = float(request.form.get("distance"))
    q = "SELECT * FROM EARTHQUAKES WHERE 1"
    data = query_search(q)
    latitudes = [ float(e['LATITUDE']) for e in data ]
    longitudes = [ float(e['LONGITUDE']) for e in data ]

    d = GEO.geoDifference(latitudes, longitudes, latitude, longitude)
    new_data = []
    for i in range(len(data)):
        if d[i] <= distance:
            new_data.append(data[i])
    update_html = dispSelectData(new_data)
    return update_html 

@app.route('/api/clusters', methods=['GET'])
def apiClusters():
    from_latitude = float(request.args.get("from_latitude"))
    from_longtitude = float(request.args.get("from_longitude"))
    to_latitude = float(request.args.get("to_latitude"))
    to_longtitude = float(request.args.get("to_longitude"))
    area = float(request.args.get("area"))
    print(area)
    print(to_latitude)
    print(to_longtitude)
    print(from_latitude)
    print(from_longtitude)
    # a .rea = 1000000
    length_area = area ** 0.5
    degree_change = length_area/100      # 111km per degree
    x_latitude = degree_change if to_latitude-from_latitude > 0 else -degree_change
    x_longitude = degree_change if to_longtitude-from_longtitude > 0 else -degree_change

    clusters = []
    lat_index = int(math.ceil((to_latitude-from_latitude)/x_latitude))
    long_index = int(math.ceil((to_longtitude-from_longtitude)/x_longitude))

    start_lat = from_latitude
    Map = []
    # clusters.append(start_lat)
    updated_html = '<table> <tr> <th> From Latitude </th> <th> From Longitude </th> <th> To Latitude </th> <th> To Longitude </th> <th> Count </th> <th> Avg Mag </th> </tr> '
    for i in range(lat_index):
        end_lat = start_lat + x_latitude
        start_long = from_longtitude
        lower_lat = start_lat if start_lat < end_lat else end_lat
        upper_lat = start_lat if start_lat > end_lat else end_lat
        for j in range(long_index):
            end_long = start_long + x_longitude
            clusters.append([start_lat, start_long, end_lat, end_long])
            lower_long = start_long if start_long < end_long else end_long
            upper_long = start_long if start_long > end_long else end_long
            q = "SELECT COUNT(*) AS COUNT, AVG(MAG) AS MAG_AVG FROM EARTHQUAKES WHERE (LATITUDE BETWEEN " + str(lower_lat) + " AND " + str(upper_lat) + ") AND (LONGITUDE BETWEEN " + str(lower_long) + " AND " + str(upper_long) + ")"
            rows = query_search(q)
            updated_html += '<tr> <td> ' + str(start_lat) + ' </td> <td> ' + str(start_long) + ' </td> <td> ' + str(end_lat) + ' </td> <td> ' + str(end_long) + ' </td> <td> ' + str(rows[0]["COUNT"]) + ' </td> <td> ' + str(rows[0]["MAG_AVG"]) + ' </td> </tr>'
            clusters.append([start_lat, start_long, end_lat, end_long, rows[0]["COUNT"]])
            # print([start_lat, start_long, end_lat, end_long, rows[0]["COUNT"], rows[0]["MAG_AVG"]])
            start_long = end_long
        start_lat = end_lat

    return updated_html + '</table>'

@app.route('/api/hourHistogram', methods=['GET'])
def apiHourHistogram():
    q = "SELECT MAG, TIME, LATITUDE, LONGITUDE FROM EARTHQUAKES WHERE MAG > 4.0"
    data = query_search(q)

    time = [ str(e['TIME']) for e in data ]
    longitudes = [ float(e['LONGITUDE']) for e in data ]

    Map = []
    for i in range(24):
        Map.append([])
    C_TIME = GEO.getCorrespondingTime(longitudes, time)
    hrs = [ int(str(e)[11:13]) for e in C_TIME ]
    for i in range(len(data)):
        Map[hrs[i]].append(data[i])
    
    update_html = '<table> <tr> <th> Hours </th> <th> Count </th> <th> Average Magnitude </th> <th> Percentage </th> </tr> '
    for i in range(24):
        update_html += '<tr> <th> ' + str(i) + ' </th> <td> ' + str(len(Map[i])) + ' </td> '
        sum_mag = 0
        for e in Map[i]:
            sum_mag += float(e['MAG'])
        update_html += '<td> ' + str(sum_mag/len(Map[i])) + '</td> '
        update_html += '<td> ' + str(float(len(Map[i]))/len(data)) + '</td> </tr>'

    return update_html


@atexit.register
def shutdown():
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
