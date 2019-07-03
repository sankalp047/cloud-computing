from flask import Flask, render_template, request
import os
import json
import mysql.connector
import redis

db = None

if os.path.isfile('credentials.json'):
    with open('credentials.json') as f:
        cred = json.load(f)
        db = cred['database'][0]

        # redis_cred = cred['redis'][0]
        # r = redis.StrictRedis(host=redis_cred['endpoint'], port=redis_cred['port'], db=0)

        # print(r)
        # r.set("S", "Shruthi")
        # response = r.get("S")
        # print(response)

else:
    print("credentials JSON not initialized")
    exit(1)

def get_DbInstance():
    mydb = mysql.connector.connect(
        host = db['hostname'],
        user = db['user'],
        passwd = db['password'],
        database = db['dbname'],
        port = 3306
    )
    return mydb

def add_enrollment(student_id, course_num, section_num):

    # Find max enrollments for that class
    q1 = "SELECT max FROM classes where course = " + str(course_num) + " and section = " + str(section_num)
    max_count = search_query(q1)[0]['max']

    # Find current number of students in that class 
    q2 = "SELECT COUNT(*) AS count FROM enrollment WHERE course_num = " + str(course_num) + " and section_num = " + str(course_num)
    cur_count = search_query(q2)[0]['count']

    # Add to enrollments
    if(max_count > cur_count):
        q3 = "INSERT INTO enrollment (course_num, section_num, student_id) VALUES (%s, %s, %s)"
        val = (course_num, section_num, student_id)
        mydb = get_DbInstance()
        mycursor = mydb.cursor()
        mycursor.execute(q3, val)
        mydb.commit()
        mydb.close()
        return True
    else:
        return False

def execute_query(query):
    mydb = get_DbInstance()
    mycursor = mydb.cursor()
    mycursor.execute(query)
    mydb.commit()
    mydb.close()
    return mycursor.fetchall()

def search_query(query):
    mydb = get_DbInstance()
    mycursor = mydb.cursor()
    mycursor.execute(query)
    row_headers=[x[0] for x in mycursor.description] #this will extract row headers
    rv = mycursor.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))
    return json_data

application = Flask(__name__)

def view_index():
    return render_template("index.html")

# add a rule for the index page.
application.add_url_rule('/', 'index', view_index)


# run the app.
if __name__ == "__main__":
    application.debug = True
    application.run()

# Syntax

    # table2 = {
    #     "records" : [{"class": "fucked up"}, {"class" : "hello world"}],
    #     "title": "Dict2"
    # }
    # return render_template("index.html", tables=[table2], msg = "Hello world")

    # application.add_url_rule('/api/clustering', 'postcluster', post_view_handler, methods=["POST"])

    # application.add_url_rule('/api/clustering', 'getcluster', get_view_handler, methods=["GET"])

    # def post_view_handler():
    #     cluster_count = int(request.form.get("cluster_count"))
    #     checked = request.form.get("checked")
    #     return render_template("index.html")

    # def get_view_handler():
    #     cluster_count = int(request.args.get("cluster_count"))
    #     checked = request.args.get("checked")
    #     return render_template("index.html")
