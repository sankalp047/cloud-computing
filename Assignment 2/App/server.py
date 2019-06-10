from flask import Flask, render_template, request, jsonify
import ibm_db
import atexit
import os
import json

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

main_html = ('<table> <tr> <th> Uplaod Excel for Earth Quakes </th> <td> <form method="POST" enctype="multipart/form-data" action="/api/dataUpload"> '
    +'<input type="file" id="file" name="file"> <br />'
    +'<input type="radio" name="append" value="True"> Append <input type="radio" name="append" value="False" checked> New Data <br />' 
    +'<input type="submit"> </form> </td> </tr>'
    +'<tr> <th> Query </th> <td> <form action="/api/query" method="GET"> <input type="text" name="query" id="query" required> <input type="submit"> </form>'
    +'<td> </td> </table> ')

@app.route('/')
def root():
    return header_html + main_html + footer_html

@app.route('/api/query', methods=['GET'])
def apiQuery():
    q = request.args.get("query")
    data = query_search(q)
    data_html = dispSelectData(data)
    data_html = dispUpdateData(data)
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

@atexit.register
def shutdown():
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
