import ibm_db

if os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        conn_str = 'DATABASE='+creds['database']+';HOSTNAME='+creds['host']+';PORT='+str(creds['port'])+';PROTOCOL='+creds['protocol']+';UID='+creds['username']+';PWD='+creds['password']


    # cd /usr/local/lib/python3.5/site-packages
# install_name_tool -change libdb2.dylib `pwd`/libdb2.dylib ibm_db.cpython-35m-darwin.so

# export DYLD_LIBRARY_PATH=/usr/local/lib/python2.7/site-packages/clidriver/lib
# export DYLD_LIBRARY_PATH=/usr/local/lib/python2.7/site-packages/clidriver/lib/icc:$DYLD_LIBRARY_PATH