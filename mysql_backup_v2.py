import os
import time
import logging
import threading
import sendmail


# mysql db many thread backup script and please use python3 run 
# date: 2016-04-27
# author: [yupozhang@gmail.com]

#装饰器用来记录备份耗费的时间
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
				
#保存日志
def save_db_logs(status,dbname):
    if status == 1:
        logging.info('{0}_backup succeed' .format(dbname))
    else:
        logging.info('{0}_backup failed' .format(dbname))
        mailuser = ["xx@qq.com"]	#要通知的邮箱，支持多个邮箱地址。
        s = sendmail.Servermail()
        s.send_user_mail('数据库备份失败','数据库_{0}备份失败'.format(dbname),mailuser)


#删除超过50天的备份压缩文件
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
    dbname = (('ayi','base',))     #要备份的数据库
    main(dbname)
	del_past_file(day='50',dpath='/data/backup')
