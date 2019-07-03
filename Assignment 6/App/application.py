from flask import Flask, render_template, request
import os
import json
import mysql.connector
from datetime import datetime
import random

host = None
user = None
passwd = None
database = None
port = None

if os.path.isfile('credentials.json'):
    with open('credentials.json') as f:
        cred = json.load(f)

        db = cred['database'][0]

        host = db['hostname']
        user = db['user']
        passwd = db['password']
        database = db['dbname']
        port = 3306
else:
    print("credentials JSON not initialized")
    exit(1)

def get_DbInstance():
    mydb = mysql.connector.connect(
        host = db['hostname'],
        user = db['user'],
        passwd = db['password'] ,
        database = db['dbname'],
        port = 3306
    )
    return mydb

application = Flask(__name__)


def view_index():
    return render_template("index.html")

def image_view():
    startTime = datetime.now()
    x = random.randint(0,1)
    endTime = datetime.now()
    elapsedTime = (endTime - startTime).total_seconds()
    print(x)
    return render_template("image.html", times = {
        "start": startTime,
        "end": endTime,
        "elapsed": str(elapsedTime) + " seconds",
        "x": x
    })

# add a rule for the index page.
application.add_url_rule('/', 'index', view_index)

application.add_url_rule('/image', 'image', image_view, methods=["GET"])

# run the app.
if __name__ == "__main__":
    application.debug = True
    application.run()