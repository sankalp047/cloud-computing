from cloudant import Cloudant
from flask import Flask, render_template, request, jsonify
import atexit
import os
import json
import ibm_db

app = Flask(__name__, static_url_path='')

if os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        conn_str = 'DATABASE='+creds['database']+';HOSTNAME='+creds['host']+';PORT='+str(creds['port'])+';PROTOCOL='+creds['protocol']+';UID='+creds['username']+';PWD='+creds['password']

port = int(os.getenv('PORT', 8000))

######################### Views  #########################

def dispProfileView(profiles):
    html = '<html> <body> <a href = "/"> Back </a> <br /> <br /> '
    if len(profiles) == 0:
        html += '<h3> So search creteria met </h3> </body> </html> '
    else:
        html += '<table> <tr> <th> ID </th> <th> </th> <th> Name </th> <th> Salary </th> <th> Room </th> <th> Keywords </th> <th> Telnum </th> <th> </th> <th> </th> </tr>'
        for profile in profiles:
            html += ('<tr> <form method="GET" action="/api/updateData"> '+
                '<td> <img src="abc.jpg" alt="Image"> </td> '+
                '<td> <input type="text" id = "id" name = "id" value = "' + str(profile.get('ID')) + '" readonly = "readonly" /> </td>'+
                '<td> <input type="text" id = "name" name = "name" value="' + profile.get('NAME') + '" ></td>'+
                '<td> <input type="text" id = "salary" name = "salary" value="' + str(profile.get('SALARY')) + '" ></td>'+
                '<td> <input type="text" id = "room" name = "room" value="' + str(profile.get('ROOM')) + '" ></td>'+
                '<td> <input type="text" id = "keywords" name = "keywords" value="' + profile.get('KEYWORDS') + '" ></td>'+
                '<td> <input type="text" id = "telnum" name = "telnum" value="' + str(profile.get('TELNUM')) + '" ></td>'+
                '<td> <input type="submit" value="Update"/>'+
                '<td> <input type="submit" value="Delete" formaction="/api/deleteData"> </button>'
            '</form> </tr>')
        html += '</table> </body> </html>'
    return html

def dispUpdateView(flag):
    if flag:
        html = '<html> <body> <p> Updated </p> <br /> <a href = "/"> HOME </a> </body> </html>'
    else:
        html = '<html> <body> <p> Failed </p> <br /> <a href = "/"> HOME </a> </body> </html>'
    return html

def dispDeleteView(flag):
    if flag:
        html = '<html> <body> <p> Deleted </p> <br /> <a href = "/"> HOME </a> </body> </html>'
    else:
        html = '<html> <body> <p> Failed </p> <br /> <a href = "/"> HOME </a> </body> </html>'
    return html

######################### Models #########################

def searchProfiles(name, salary_min, salary_max, telnum, room):
    try:
        db2conn = ibm_db.connect(conn_str, "", "")
        if db2conn:
            query = "SELECT * FROM PROFILE WHERE 1 "
            if str(name) != "None" and len(name) != 0:
                query += " AND LOWER(Name) LIKE '%"+name.lower()+"%' "
            if str(salary_min) != "None" and str(salary_max) != "None" and len(salary_min) != 0 and len(salary_max) != 0:
                if int(salary_min) > 0 and int(salary_max) > 0:
                    query += " AND SALARY BETWEEN " + str(salary_min) + " AND " + str(salary_max)
            if str(telnum) != "None" and len(telnum) != 0 and int(room) > 0:
                query += " AND TELNUM = " + str(telnum)
            if str(room) != "None" and len(room) != 0 and int(room) > 0:
                query += " AND room = " + str(room)
            print(query)
            statement = ibm_db.prepare(db2conn, query)
            ibm_db.execute(statement)
            rows = []
            result = ibm_db.fetch_assoc(statement)
            while result != False:
                rows.append(result.copy())
                result = ibm_db.fetch_assoc(statement)
            ibm_db.close(db2conn)
            return rows
    except:
        print("Connection to Database failed")
        return False

def updateProfile(id_, name, salary, keywords, telnum, room):
    db2conn = ibm_db.connect(conn_str, "", "")
    if db2conn:
        query = "UPDATE PROFILE SET "
        query += " Name = '" + name + "' "
        if str(salary) != "None" and int(salary) > 0:
            query += ", salary = " + str(salary)
        if keywords != None:
            query += ", keywords = '" + keywords + "' "
        if str(telnum) != "None":
            query += ", telnum = " + str(telnum)
        if str(room) != "None":
            query += ", room = " + str(room)
        query += " WHERE id = " + str(id_)
        print(query)
        statement = ibm_db.prepare(db2conn, query)
        result = ibm_db.execute(statement)
        ibm_db.close(db2conn)
        return result
    # except:
        # print("Connection to Database failed")
        # return False

def deleteProfile(id_):
    try:
        db2conn = ibm_db.connect(conn_str, "", "")
        if db2conn:
            query = "DELETE FROM PROFILE WHERE id = " + str(id_)
            statement = ibm_db.prepare(db2conn, query)
            result = ibm_db.execute(statement)
            ibm_db.close(db2conn)
            return result
    except:
        print("Connection to Database failed")
        return False


####################### App Routes #######################

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/api/searchData', methods=['GET'])
def searchData():
    name = request.args.get('name')
    salary_min = request.args.get('salary_min')
    salary_max = request.args.get('salary_max')
    telnum = request.args.get('telnum')
    room = request.args.get('room')
    relevant_profiles = searchProfiles(name, salary_min, salary_max, telnum, room)
    return dispProfileView(relevant_profiles)

@app.route('/api/updateData', methods=['GET'])
def updateData():
    name = request.args.get('name')
    salary = request.args.get('salary')
    id_ = request.args.get('id')
    telnum = request.args.get('telnum')
    keywords = request.args.get('keywords')
    room = request.args.get('room')
    flag = updateProfile(id_, name, salary, keywords, telnum, room)
    return dispUpdateView(flag)

@app.route('/api/deleteData', methods=['GET'])
def deleteData():
    id_ = request.args.get('id')
    flag = deleteProfile(id_)
    return dispDeleteView(flag)

@atexit.register
def shutdown():
    return app.send_static_file('index.html') 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
