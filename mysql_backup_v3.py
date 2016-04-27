
import os
import time
import logging
import threading
import smtplib
from email.mime.text import MIMEText

# mysql db many thread backup script and please use python3 run 
# date: 2016-04-27
# author: [yupozhang@gmail.com]


class Dbbackup():


    @staticmethod
    def backup(dpath,db):
        dbtime = time.strftime('%Y%m%d%H%M%S')
        if os.path.exists(dpath) or os.mkdir(dpath):
            start = time.time()
            status = os.system("/usr/local/mysql/bin/mysqldump -R  --opt {0} > {1}/{2}_{3}.sql && /usr/bin/gzip {1}/{2}_{3}.sql " .format(db,dpath,db,dbtime))
            endtime = time.time() - start
            if status == 0:
                Dbbackup.save_db_logs(1,db,endtime,dbtime)
            else:
                Dbbackup.save_db_logs(2,db,endtime,dbtime)

    @staticmethod
    def save_db_logs(status,dbname,taketime,dbtime):
        dspath = '/data/backup'
        logname = "{0}/dbbackup.log".format(dspath)
        logformat = ('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
        logging.basicConfig(level=logging.DEBUG,format=logformat,filename=logname,filemode='a')
        if status == 1:
            logging.info('{0} at {1} backup succeed and totle take time {2} ' .format(dbname,dbtime,taketime))
        else:
             logging.info('{0} at {1} backup failed' .format(dbname,dbtime))
             s = Servermail()
             mailuser = ["zo@y.com"]				   #Ҫ֪ͨ�����䣬����֧�ֶ����
             s.send_user_mail('���ݿⱸ��ʧ��','���ݿ�_{0}����ʧ��'.format(dbname),mailuser)

    @staticmethod
    def del_past_files(day,dpath='/data/backup'):
        if day:
            status = os.system('''/usr/bin/find {0}  -type f \( -name "*.gz" \) -mtime +{1} -delete''' .format(dpath,day))


#�����ʼ���
class Servermail():
    def __init__(self):
        self.Server_user = "xx@qq.com"					#Ҫʹ�÷����ʼ�������
        self.Server_pwd = "Rxx8"						#��������
        self.Servers = "smtp.exmail.qq.com"				#Ҫʹ�õ��ʼ���������ַ

    def send_user_mail(self,title,connect,tomail):
        self.connect = connect
        self.title = title
        self.tomail = tomail

        msg = MIMEText(self.connect)
        msg["Subject"] = self.title						#�ʼ�����
        msg["From"]    = self.Server_user				#�ʼ����Ե��û�
        msg["To"]      = ";".join(self.tomail)			#Ҫ���͵������ַ
        try:
            with smtplib.SMTP(self.Servers, timeout=30) as s:
                s.login(self.Server_user, self.Server_pwd)	#��½������
                s.sendmail(self.Server_user,self.tomail, msg.as_string())#�����ʼ�
                print("���ͳɹ�")
        except Exception as e:
             print("����ʧ��")




if __name__ == '__main__':
    dbname = (('company_inner','base'))		#Ҫ���ݵ����ݿ�����
    dspath = '/data/backup'
    threads = []
    for db in dbname:
        threads.append(threading.Thread(target=Dbbackup.backup,args=(dspath, db)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    Dbbackup.del_past_files(day='50')
