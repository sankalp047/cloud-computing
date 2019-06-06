from cloudant import Cloudant
from flask import Flask, render_template, request, jsonify
import atexit
import os
import json
import ibm_db
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from datetime import datetime

def create_app():
    app = Flask(__name__, static_url_path='')

    with app.app_context():
        print(app.name)

    return app

app = create_app()

if os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['db2'][0]['credentials']
        storage_details = vcap['services']['storage'][0]['details']
        conn_str = 'DATABASE='+creds['database']+';HOSTNAME='+creds['host']+';PORT='+str(creds['port'])+';PROTOCOL='+creds['protocol']+';UID='+creds['username']+';PWD='+creds['password']
        storage_url = storage_details['endpoint_url']+'/'+storage_details['bucket_name']+'/'

        COS_ENDPOINT = storage_details['endpoint_url']
        COS_API_KEY_ID = storage_details['ibm_api_key_id']
        COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
        COS_RESOURCE_CRN = storage_details['ibm_service_instance_id']

        cos = ibm_boto3.resource("s3",
            ibm_api_key_id=COS_API_KEY_ID,
            ibm_service_instance_id=COS_RESOURCE_CRN,
            ibm_auth_endpoint=COS_AUTH_ENDPOINT,
            config=Config(signature_version="oauth"),
            endpoint_url=COS_ENDPOINT
        )
        
port = int(os.getenv('PORT', 8000))

######################### Views  #########################

def dispProfileView(profiles):
    html = '<html> <body> <a href = "/"> Back </a> <br /> <br /> '
    if len(profiles) == 0:
        html += '<h3> So search creteria met </h3> </body> </html> '
    else:
        html += '<table> <tr> <th> ID </th> <th> </th> <th> Name </th> <th> Salary </th> <th> Room </th> <th> Keywords </th> <th> Telnum </th> <th> </th> <th> </th> </tr>'
        for profile in profiles:
            html += ('<tr> <form method="GET"> '+
                '<td> <img width="120" height="120" src="'+storage_url+str(profile.get('PICTURE'))+'" alt="No Image"> <br /> '+
                '  <input type="file" id="file" name="file"> '+
                '  <input type="submit" formenctype="multipart/form-data" formmethod="POST" formaction="/api/uploadImage" value="Upload"> </td> '+
                '<td> <input type="text" id = "id" name = "id" value = "' + str(profile.get('ID')) + '" readonly = "readonly" /> </td>'+
                '<td> <input type="text" id = "name" name = "name" value="' + profile.get('NAME') + '" ></td>'+
                '<td> <input type="text" id = "salary" name = "salary" value="' + str(profile.get('SALARY')) + '" ></td>'+
                '<td> <input type="text" id = "room" name = "room" value="' + str(profile.get('ROOM')) + '" ></td>'+
                '<td> <input type="text" id = "keywords" name = "keywords" value="' + profile.get('KEYWORDS') + '" ></td>'+
                '<td> <input type="text" id = "telnum" name = "telnum" value="' + str(profile.get('TELNUM')) + '" ></td>'+
                '<td> <input type="submit" value="Update" formaction="/api/updateData"/>'+
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

def multi_part_upload(bucket_name, item_name, file_path):
    try:
        print("Starting file transfer for {0} to bucket: {1}\n".format(item_name, bucket_name))
        # set 5 MB chunks
        part_size = 1024 * 1024 * 5

        # set threadhold to 15 MB
        file_threshold = 1024 * 1024 * 15

        # set the transfer threshold and chunk size
        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )

        # the upload_fileobj method will automatically execute a multi-part upload
        # in 5 MB chunks for all files over 15 MB
        with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data,
                Config=transfer_config
            )

        print("Transfer for {0} Complete!\n".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to complete multi-part upload: {0}".format(e))

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

def updateProfile(id_, name, salary, keywords, telnum, room, picture):
    try:
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
            if str(picture) != "None":
                query += ", picture = '" + str(picture) + "' "
            query += " WHERE id = " + str(id_)
            statement = ibm_db.prepare(db2conn, query)
            result = ibm_db.execute(statement)
            ibm_db.close(db2conn)
            return result
    except:
        print("Connection to Database failed")
        return False

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
    flag = updateProfile(id_, name, salary, keywords, telnum, room, None)
    return dispUpdateView(flag)

@app.route('/api/deleteData', methods=['GET'])
def deleteData():
    id_ = request.args.get('id')
    flag = deleteProfile(id_)
    return dispDeleteView(flag)

@app.route('/api/uploadImage', methods=['POST'])
def uploadImage():
    id_ = request.form.get("id")
    name = request.form.get("name")
    if 'file' not in request.files:
        flash('No file part')
        return dispUpdateView(False)
    file_ = request.files['file']
    if file_.filename == '':
            flash('No selected file')
            return dispUpdateView(False)
    if file_:
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%dT%H-%M-%SZ')
        filename = "App_"+date_time+(file_.filename)
        file_.save(os.path.join('files/', filename))
        output = multi_part_upload(storage_details['bucket_name'], filename, os.path.join('files/', filename))
        flag = updateProfile(id_, name, None, None, None, None, filename)
        os.remove('files/'+filename)
        return dispUpdateView(flag)
    return dispUpdateView(False)

@atexit.register
def shutdown():
    return app.send_static_file('index.html') 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
