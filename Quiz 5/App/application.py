from flask import Flask, render_template, request
import os
import json
import mysql.connector
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import copy

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

string_attributes = ['name', 'sex', 'ticket', 'cabin', 'embarked', 'body', 'home.dest', 'boat']

def view_index():
    return render_template("index.html")

def normalizeData(X):
    mean_X = np.mean(X, axis=0)
    std_X = np.std(X, axis=0)
    new_X = (X-mean_X)/std_X
    return {
        "new_X": new_X,
        "mean": mean_X,
        "std": std_X
    }

def computeX(Z, mean, std):
    return Z*std + mean

def getTableValues(data, clusters, labels):
    cluster_details = []
    cluster_count = np.shape(clusters)[0]
    for i in range(cluster_count):
        this_cluster_indices = np.where(labels == i)
        this_cluster_points = data[this_cluster_indices,:]
        this_count = np.shape(this_cluster_points)[1]
        this_distance = (np.sum(np.sqrt(np.sum((this_cluster_points - clusters[i,:])**2, axis=1))))/this_count
        this_details = {
            "index": i + 1,
            "Centroid": str(clusters[i,:]), 
            "Distance": str(this_distance), 
            "Count": this_count,
            "Points": {
                "x": this_cluster_points[0,:,0].tolist(), 
                "y": this_cluster_points[0,:,1].tolist(),
            }
        }
        cluster_details.append(this_details)
        # print("Centroid: " + str(clusters[i,:]) + "..... Closely Packed: "+ str(this_distance) + "..... Cluster Size: " + str(np.shape(this_cluster_points)[1]))
        # print(np.shape(this_cluster_points))

    return cluster_details

def view_cluster():

    string_columns = []

    cluster_count = int(request.form.get("cluster_count"))
    clusters = request.form.get("checked").split(",")

    q = "SELECT " + str(request.form.get("checked")) + " FROM titanic3 WHERE "
    for i, c in enumerate(clusters):
        if c in string_attributes:
            string_columns.append(i)
        q += " " + str(c) + " IS NOT NULL AND"
    q = q[:len(q)-3]

    # q += " LIMIT 10"

    mycursor = mydb.cursor()
    mycursor.execute(q)
    records = mycursor.fetchall()

    rules = []
    d = np.array(records)
    r = copy.deepcopy(d)
    for i in string_columns:
        label_encoder = LabelEncoder()
        r[:,i] = label_encoder.fit_transform(d[:,i])
        rules.append({"Attribute": clusters[i], "Classes": str(label_encoder.classes_)})
    r = r.astype(np.float)
    # print(string_columns)
    # print(r)
    # print(d)

    # table = normalizeData(np.ar
    # print(computeX(data, table.get("mean"), table.get("std")))
    # kmeans = KMeans(n_clusters=cluster_count, random_state=0).fit(data)
    # c = computeX(kmeans.cluster_centers_, table.get("mean"), table.get("std"))
    # print("-----Labels------")
    # print(kmeans.labels_)

    kmeans = KMeans(n_clusters=cluster_count, random_state=0).fit(r)
    cluster_details = getTableValues(r, kmeans.cluster_centers_, kmeans.labels_)
    cluster_attributes = request.form.get("checked")

    return render_template("index.html", clusters={
        "cluster_details": cluster_details,
        "cluster_attributes": cluster_attributes,
        "attr_count": len(clusters),
        "cluster_centroids": kmeans.cluster_centers_.tolist(),
        "rules": rules
    })

# add a rule for the index page.
application.add_url_rule('/', 'index', view_index)

application.add_url_rule('/api/clustering', 'cluster', view_cluster, methods=["POST"])

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()