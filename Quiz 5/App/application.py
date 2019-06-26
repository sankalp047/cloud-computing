from flask import Flask, render_template, request
import os
import json
import mysql.connector
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import copy
from datetime import datetime

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

string_attributes = ['fname', 'lname', 'survived']

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

def getTableValues(data, clusters, labels, records):
    cluster_details = []
    cluster_count = np.shape(clusters)[0]
    for i in range(cluster_count):
        this_cluster_indices = np.where(labels == i)
        this_cluster_points = data[this_cluster_indices,:]
        this_sample = None
        if len(records) > 0:
            print(this_cluster_indices[0])
            this_sample = (records[this_cluster_indices,:])
        this_count = np.shape(this_cluster_points)[1]
        this_distance = (np.max(np.sqrt(np.sum((this_cluster_points - clusters[i,:])**2, axis=1))))/this_count
        this_details = {
            "index": i + 1,
            "Centroid": str(clusters[i,:]), 
            "Distance": str(this_distance), 
            "Count": this_count,
            "Points": {
                "x": this_cluster_points[0,:,0].tolist(), 
                "y": this_cluster_points[0,:,1].tolist(),
            },
            "SampleRecord": this_sample[0,0,:]
        }
        cluster_details.append(this_details)
        # print("Centroid: " + str(clusters[i,:]) + "..... Closely Packed: "+ str(this_distance) + "..... Cluster Size: " + str(np.shape(this_cluster_points)[1]))
        # print(np.shape(this_cluster_points))

    return cluster_details

def view_cluster():

    columns = 'cabinnum, fname, lname, age, height, education, wealth, survived, lat, `long`, fare'
    columns_array = columns.split(", ")
    cluster_count = int(request.form.get("cluster_count"))
    clusters = (request.form.get("checked").split(","))
    clusters = list(map(int, clusters)) 
    string_columns = []
    print(columns_array)
    print(clusters)

    q = "SELECT "+columns+" FROM minnow WHERE "
    for i, c in enumerate(clusters):
        print(columns_array[c])
        if columns_array[c] in string_attributes:
            string_columns.append(c)
        q += " " + columns_array[c] + " IS NOT NULL AND"
    q = q[:len(q)-3]
    # q += " LIMIT 10"
    # print(q)

    mycursor = mydb.cursor()
    mycursor.execute(q)
    records = mycursor.fetchall()

    rules = []
    d = np.array(records)
    r = copy.deepcopy(d[:,clusters])
    print(r)
    for i in string_columns:
        label_encoder = LabelEncoder()
        r[:,i] = label_encoder.fit_transform(d[:,i])
        rules.append({"Attribute": clusters[i], "Classes": str(label_encoder.classes_)})
    r = r.astype(np.float)
    print(r)
    # print(string_columns)
    # print(r)
    # print(d)

    # # table = normalizeData(np.ar
    # # print(computeX(data, table.get("mean"), table.get("std")))
    # # kmeans = KMeans(n_clusters=cluster_count, random_state=0).fit(data)
    # # c = computeX(kmeans.cluster_centers_, table.get("mean"), table.get("std"))
    # # print("-----Labels------")
    # # print(kmeans.labels_)

    kmeans = KMeans(n_clusters=cluster_count, random_state=0).fit(r)
    cluster_details = getTableValues(r, kmeans.cluster_centers_, kmeans.labels_, d)
    cluster_attributes = request.form.get("checked")

    barGraph = []
    for x in cluster_details:
        label = (x['Centroid']),
        count = (x['Count']),
        barGraph.append({"label": label, "count": count})

    return render_template("index.html", clusters={
        "cluster_details": cluster_details,
        "cluster_attributes": cluster_attributes,
        "attr_count": len(clusters),
        "cluster_centroids": kmeans.cluster_centers_.tolist(),
        "rules": rules
    }, barGraph = barGraph)

    # return render_template("index.html")

def myClusterDetails(cluster_count, clusters, r):
    kmeans = KMeans(n_clusters=cluster_count, random_state=0).fit(r)
    cluster_details = getTableValues(r, kmeans.cluster_centers_, kmeans.labels_, None)
    return cluster_details

def execute_query(q):
    mycursor = mydb.cursor()
    mycursor.execute(q)
    records = mycursor.fetchall()
    return records

def view_first():

    start = datetime.now()
    q1 = "SELECT age, height from minnow WHERE age is not null and height is not null"
    r1 = execute_query(q1)
    c1 = myClusterDetails(4, ['age', 'height'], np.array(r1))
    time = (datetime.now() - start).total_seconds()
    objs.append({'cluster_details': c1, 'title': "Cluster for age, height", "time": str(time)})

    start = datetime.now()
    q2 = "SELECT cabinnum, fare from minnow WHERE cabinnum is not null and fare is not null"
    r2 = execute_query(q2)
    c2 = myClusterDetails(3, ['cabinnum', 'fare'], np.array(r2))
    time = (datetime.now() - start).total_seconds()
    objs.append({'cluster_details': c2, 'title': "Cluster for cabin num, fare", "time": str(time)})
    return render_template("index.html", part1 = objs)

def view_three():
    wealth = str(request.form.get("wealth"))
    age = str(request.form.get("age"))
    # wealth = int(request.form.get("wealth"))
    # cabin = int(request.form.get("cabin"))
    c_count = int(request.form.get("c_count"))
    selected_attributes = []
    index = []
    selected_values = []
    if len(age) != 0:
        index.append(1)
        selected_attributes.append('age')
        selected_values.append(int(age))
    if len(wealth) != 0:
        index.append(2)
        selected_attributes.append('wealth')
        selected_values.append(int(wealth))
    # if len(wealth) != 0:
    #     index.append(2)
    #     selected_attributes.append('wealth')
    #     selected_values.append(wealth)
    # if len(cabin) != 0:
    #     index.append(3)
    #     selected_attributes.append('cabin')
    #     selected_values.append(cabin)

    attributes = str(selected_attributes)
    q = "SELECT fname, age, wealth, cabinnum, survived FROM minnow WHERE "
    for i, c in enumerate(selected_attributes):
        if c in string_attributes:
            string_columns.append(i)
        q += " " + str(c) + " IS NOT NULL AND"
    q = q[:len(q)-3]
    print(q)
    records = execute_query(q)
    r = np.array(records)
    print(index)
    d = copy.deepcopy(r[:,index])
    print(d)
    kmeans = KMeans(n_clusters=c_count, random_state=0).fit(d)

    o = kmeans.predict([np.array(selected_values)])
    this_cluster_indices = np.where(kmeans.labels_ == o.tolist())
    print(this_cluster_indices)
    this_cluster_point = r[this_cluster_indices,:]
    print(this_cluster_point)

    return render_template("index.html", partfour = this_cluster_point)

# add a rule for the index page.
application.add_url_rule('/', 'index', view_index)

application.add_url_rule('/api/clustering', 'cluster', view_cluster, methods=["POST"])

application.add_url_rule('/api/first', 'first', view_first, methods=["POST"])

application.add_url_rule('/api/three', 'three', view_three, methods=["POST"])

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()