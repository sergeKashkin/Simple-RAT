from ctypes import WinDLL
user32 = WinDLL('user32', use_last_error=True)


key_dict = 	{ 
					# English
					"0x409":{
								"q":"q","w":"w","e":"e","r":"r","t":"t","y":"y","u":"u","i":"i","o":"o","p":"p","[":"[","]":"]",
								"a":"a","s":"s","d":"d","f":"f","g":"g","h":"h","j":"j","k":"k","l":"l",";":";","'":"'","\\":"\\",
								"z":"z","x":"x","c":"c","v":"v","b":"b","n":"n","m":"m",",":",",".":".","/":"/",
								# Specials
								"Oem_3":"`", "Oem_1":";", "Oem_2":"/", "Oem_4":"[", "Oem_5":"\\", "Oem_6":"]", "Oem_7":"'",
								"Oem_Period":".", "Oem_Comma":",","Numpad1":"1", "Numpad2":"2", "Numpad3":"3", "Numpad4":"4",
								"Numpad5":"5", "Numpad6":"6", "Numpad7":"7", "Numpad8":"8","Numpad9":"9", "Numpad0":"1","Oem_102":"\\"
							},
					# Russian
					"0x419":{
								"q":"й","w":"ц","e":"у","r":"к","t":"е","y":"н","u":"г","i":"ш","o":"щ","p":"з","[":"х","]":"ъ",
								"a":"ф","s":"ы","d":"в","f":"а","g":"п","h":"р","j":"о","k":"л","l":"д",";":"ж","'":"э","\\":"\\",
								"z":"я","x":"ч","c":"с","v":"м","b":"и","n":"т","m":"ь",",":"б",".":"ю","/":".",
								# Specials
								"Oem_3":"`", "Oem_1":"ж", "Oem_2":".", "Oem_4":"х", "Oem_5":"\\", "Oem_6":"ъ", "Oem_7":"э",
								"Oem_Period":"ю", "Oem_Comma":"б","Numpad1":"1", "Numpad2":"2", "Numpad3":"3", "Numpad4":"4",
								"Numpad5":"5", "Numpad6":"6", "Numpad7":"7", "Numpad8":"8","Numpad9":"9", "Numpad0":"1", "Oem_102":"\\"
							},
					# Hebrew
					"0x40d":{
								"q":"/","w":"'","e":"ק","r":"ר","t":"א","y":"ט","u":"ו","i":"ן","o":"ם","p":"פ","[":"]","]":"[",
								"a":"ש","s":"ד","d":"ג","f":"כ","g":"ע","h":"י","j":"ח","k":"ל","l":"ך",";":"ף","'":",","\\":"\\",
								"z":"ז","x":"ס","c":"ב","v":"ה","b":"נ","n":"מ","m":"צ",",":"ת",".":"ץ","/":".",
								# Specials
								"Oem_3":";", "Oem_1":"ף", "Oem_2":".", "Oem_4":"х", "Oem_5":"\\", "Oem_6":"]", "Oem_7":",",
								"Oem_Period":"ץ", "Oem_Comma":"ת","Numpad1":"1", "Numpad2":"2", "Numpad3":"3", "Numpad4":"4",
								"Numpad5":"5", "Numpad6":"6", "Numpad7":"7", "Numpad8":"8","Numpad9":"9", "Numpad0":"1","Oem_102":"\\"
							}
			}
			
			
def get_keyboard_language():
	
	handle = user32.GetForegroundWindow()
	
	threadid = user32.GetWindowThreadProcessId(handle, 0)
	
	layout_id = user32.GetKeyboardLayout(threadid)
	
	language_id = layout_id & (2 ** 16 -1)
	
	language_id_hex = hex(language_id)
	
	
	return str(language_id_hex)

	
def translate_key(key):
	try:
		return key_dict[get_keyboard_language()][key.lower()]
	except:
		return key
	
