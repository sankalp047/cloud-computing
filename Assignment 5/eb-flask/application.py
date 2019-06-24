from flask import Flask, render_template, request
import os
import json
import mysql.connector
import numpy as np
from sklearn.cluster import KMeans

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

def view_cluster():
    cluster_count = int(request.form.get("cluster_count"))
    clusters = request.form.get("checked").split(",")

    q = "SELECT " + str(request.form.get("checked")) + " FROM titanic3 LIMIT 10"

    mycursor = mydb.cursor()
    mycursor.execute(q)
    data = np.array(mycursor.fetchall())
    print(data.shape)
    kmeans = KMeans(n_clusters=cluster_count, random_state=0).fit(data)
    print(kmeans.cluster_centers_)

    return render_template("index.html")

# add a rule for the index page.
application.add_url_rule('/', 'index', view_index)

application.add_url_rule('/api/clustering', 'cluster', view_cluster, methods=["POST"])

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()