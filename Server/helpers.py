'''different functions for proper workflow'''
import linecache
import sys
import json
from flask import redirect, request, session
from functools import wraps
from cryptography.fernet import Fernet
import sqlite3
from sqlite3 import Error
from werkzeug.security import generate_password_hash


KEY = b'ikex6DgCDdVjfwoyNrea9wJcj87bZNSVe6YZkDQQMDU='
F = Fernet(KEY)



# Printing Exception Info
def PrintException():
    '''Show Info about the exception'''
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('Exception in ({}, LINE {} "{}"): {}'.format(filename,lineno,line.strip(),exc_obj))


def send_recv(cons,client,msg):
    '''Func. to send and recieve messages over socket'''
    cons[client][0].sendall(F.encrypt(bytes(msg, encoding="utf-8")))
    data = b''
    length = F.decrypt(cons[client][0].recv(4096))
    length = int(json.loads(length, encoding="utf-8")["len"])
    while len(data) < length:
        buf = cons[client][0].recv(4096)
        data += buf
    return json.loads(F.decrypt(data), encoding="utf-8")

def login_required(f):
    '''decorate routes to require login'''
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if session.get('username') is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_func


def check_init_db(conn):
    CREATE_ADMINS = """CREATE TABLE 'admins' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'user_name' TEXT NOT NULL, 'hash' TEXT NOT NULL)"""
    CREATE_USERS = """CREATE TABLE 'clients' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'user_name' TEXT NOT NULL, 'os' TEXT NOT NULL, 'location' TEXT NOT NULL, 'date_added' TIMESTAMP, 'last_seen' TIMESTAMP);"""
    
    try:
        status = None
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE name=?",('admins',))
        a = c.fetchone()
        c.execute("SELECT name FROM sqlite_master WHERE name=?",('clients',))
        u = c.fetchone()
        if not a:
           c.execute(CREATE_ADMINS)
        if not u:
            c.execute(CREATE_USERS)
    except Error as e:
        print(e)
        status = e
    finally:
        c.close()
        return status

def sqlite_connection():
    db = 'app_data.db'
    conn = None
    try:
        conn = sqlite3.connect(db,check_same_thread=False)
        status = check_init_db(conn)
        if status:
            print(status)
            #sys.exit(0)
    except Error as e:
        print(e)
        #sys.exit(0)
    finally:
        return conn


def db_user_check(conn):
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM admins")
        r = c.fetchone()
        username = ''
        password = ''
        if not r:
            print("Please register in order to run the server.\nRemember your creds.")
            status = False
            while not status:
                username = str(input('Enter username(at least 6 chars long):'))
                password = str(input('Enter password(at least 8 chars long):'))
                if (len(username) >= 6 and len(password) >= 8 ):
                    status = True
            hashed = generate_password_hash(password)
            c.execute("INSERT INTO admins(user_name,hash) VALUES(?,?);",(username,hashed))
            conn.commit()
            print("Youre in!")
    except Error as e:
        print(e)
        return False
    finally:
        c.close()
        return True

def sql_to_json_list(query):
    sql_json = []
    for client in query:
        sql_json.append(sql_to_json_one([client]))
    return sql_json


def sql_to_json_one(query):
    '''convert sql query to dict. format.
       because originally nosql db was used.'''
    client = query[0]
    client_json = {}
    client_json['user_name'] = client[1]
    client_json['os'] = client[2]
    client_json['location'] = client[3]
    client_json['date_added'] = client[4]
    client_json['last_seen'] = client[5]
    return client_json



