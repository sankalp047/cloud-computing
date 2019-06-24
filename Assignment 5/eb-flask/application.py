from flask import Flask, render_template, request
import os
import json
import mysql.connector

if os.path.isfile('credentials.json'):
    with open('credentials.json') as f:
        cred = json.load(f)

        db = cred['database'][0]

        mydb = mysql.connector.connect(
            host = db['hostname'],
            user = db['user'],
            passwd = db['password'] ,
            database = db['dbname'],
            port = 3306
        )

else:
    print("credentials JSON not initialized")
    exit(1)

application = Flask(__name__)

def view_index():
    return render_template("index.html")

# add a rule for the index page.
application.add_url_rule('/', 'index', view_index)

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()