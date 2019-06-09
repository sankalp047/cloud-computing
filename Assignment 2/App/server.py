from flask import Flask, render_template, request, jsonify
import ibm_db
import atexit
import os
import json

app = Flask(__name__, static_url_path='')

db_name = 'mydb'
client = None
db = None

port = int(os.getenv('PORT', 8000))

if os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        creds = vcap['services']['db2'][0]['credentials']
        conn_str = 'DATABASE='+creds['database']+';HOSTNAME='+creds['host']+';PORT='+str(creds['port'])+';PROTOCOL='+creds['protocol']+';UID='+creds['username']+';PWD='+creds['password']
        try:
            db2conn = ibm_db.connect(conn_str, "", "")
        except:
            print("Connection to Database failed")
            exit(1)

def query(query):
    if db2conn:
        statement = ibm_db.prepare(db2conn, query)
        ibm_db.execute(statement)
        rows = []
        result = ibm_db.fetch_assoc(statement)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(statement)
        ibm_db.close(db2conn)
        return rows
    else
        return False

@app.route('/')
def root():
    return 'html here'

@atexit.register
def shutdown():
    if db2conn:
        ibm_db.close(db2conn)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
