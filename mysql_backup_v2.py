import os
import time
import logging
import threading
import sendmail


# mysql db many thread backup script and please use python3 run 
# date: 2016-04-27
# author: [yupozhang@gmail.com]

#װ����������¼���ݺķѵ�ʱ��
def save_time(fn):
    def warp(*args,**kwargs):
        start = time.time()
        ret = fn(*args,**kwargs)
        dbtime = time.time() - start
        logging.info('db backup is take time {0}' .format(dbtime))
        return ret
    return warp

@save_time
def backupdb(dpath,db):
    dbtime = time.strftime('%Y%m%d%H%M%S')
    if os.path.exists(dpath) or os.mkdir(dpath):
            status = os.system("/usr/local/mysql/bin/mysqldump -R  --opt {0} > {1}/{2}_{3}.sql && /usr/bin/gzip {1}/{2}_{3}.sql " .format(db,dpath,db,dbtime))
            if status == 0:
                save_db_logs(1,db)
            else:
                save_db_logs(2,db)
				
#������־
def save_db_logs(status,dbname):
    if status == 1:
        logging.info('{0}_backup succeed' .format(dbname))
    else:
        logging.info('{0}_backup failed' .format(dbname))
        mailuser = ["xx@qq.com"]	#Ҫ֪ͨ�����䣬֧�ֶ�������ַ��
        s = sendmail.Servermail()
        s.send_user_mail('���ݿⱸ��ʧ��','���ݿ�_{0}����ʧ��'.format(dbname),mailuser)


#ɾ������50��ı���ѹ���ļ�
def del_past_file(day,dpath='/data/backup'):
    if day:
        status = os.system('''/usr/bin/find {0}  -type f \( -name "*.gz" \) -mtime +{1} -delete''' .format(dpath,day))



def main(dbname):
    dspath = '/data/backup'
    logname = "{0}/dbbackup.log".format(dspath)
    logformat = ('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
    logging.basicConfig(level=logging.DEBUG,format=logformat,filename=logname,filemode='a')

    threads = []
    for db in dbname:
        threads.append(threading.Thread(target=backupdb,args=(dspath, db)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    

if __name__ == '__main__':
    dbname = (('ayi','base',))     #Ҫ���ݵ����ݿ�
    main(dbname)
	del_past_file(day='50',dpath='/data/backup')
