from flask import Flask, render_template, request
import os
import json
import mysql.connector
import redis
from datetime import datetime

db = None
counter = 1

if os.path.isfile('credentials.json'):
    with open('credentials.json') as f:
        cred = json.load(f)
        db = cred['database'][0]

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
    q2 = "SELECT COUNT(*) AS count FROM enrollment WHERE course_num = " + str(course_num) + " and section_num = " + str(section_num)
    cur_count = search_query(q2)[0]['count']

    print(cur_count)
    print(max_count)
    # Add to enrollments
    if(int(max_count) > int(cur_count)):
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

def get_student_view():
    fname = request.args.get("fname")
    lname = request.args.get("lname")
    return stud_view(fname, lname)

def stud_view(fname, lname):
    tables = []
    
    myDetails = search_query("SELECT * FROM students WHERE LOWER(Fname) LIKE '" + fname + "' AND LOWER(Lname) LIKE '" + lname + "'")
    if len(myDetails) > 0:
        tables.append({
            "records": myDetails,
            "title": "Student Details"
        })
    else:
        return render_template('index.html', msg="Not a valid student") 

    myEnrollments = search_query("SELECT * FROM classes as c "+
                    "LEFT OUTER JOIN enrollment as e ON c.course = e.course_num AND c.section = e.section_num "+
                    "LEFT OUTER JOIN students as s ON s.idNum = e.student_id "+
                    "WHERE LOWER(s.Fname) LIKE '" + fname + "' AND LOWER(s.Lname) LIKE '" + lname + "'")
    if len(myEnrollments) > 0:
        tables.append({
            "records": myEnrollments,
            "title": "Student Enrollments"
        })
    
    if len(myEnrollments) < 3:

        addCourses = {
            "records": search_query("SELECT * FROM classes"),
            "title": "Add Enrollments",
            "student_id": myDetails[0]['IdNum']
        }
    else:
        addCourses = None

    return render_template('index.html', tables = tables, addCourse = addCourses)
    
def get_enrollmentView():
    student_id = request.args.get("student_id")
    course_num = request.args.get("course")
    section_num = request.args.get("section")
    flag = add_enrollment(student_id, course_num, section_num)
    if flag:
        return render_template('index.html', msg = "Course Added")
    else:
        return render_template('index.html', msg="Class already full")

def adminView():
    tables = []
    print("SELECT SELECT COUNT(*) as count, section_num, course_num From enrollment GROUP BY course_num, section_num")
    count_enrollments = search_query("SELECT COUNT(*) as count, section_num, course_num From enrollment GROUP BY course_num, section_num")
    if(len(count_enrollments)) > 0:
        tables.append({
            "records": count_enrollments,
            "title": "Count Enrollments"
        })
    enrollments = search_query("SELECT * FROM enrollment as e "+
                    "LEFT OUTER JOIN classes as c ON c.course = e.course_num AND c.section = e.section_num "+
                    "LEFT OUTER JOIN students as s ON s.idNum = e.student_id ")
    if(len(enrollments)) > 0:
        tables.append({
            "records": enrollments,
            "title": "All Enrollments"
        })
    return render_template('admin.html', tables = tables)

def scaleView():
    global counter
    counter = counter + 1
    return render_template('scale.html', time = datetime.now(), count = counter-1)

# add a rule for the index page.
application.add_url_rule('/', 'index', view_index)

application.add_url_rule('/api/student', 'studentView', get_student_view, methods=["GET"])
application.add_url_rule('/api/addEnrollment', 'enrollmentView', get_enrollmentView, methods=["GET"])

application.add_url_rule('/admin', 'adminView', adminView)

application.add_url_rule('/scale', 'scaleView', scaleView)

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
