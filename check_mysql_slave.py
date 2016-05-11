import MySQLdb
import logging
import os
import time
import smtplib
from email.mime.text import MIMEText
#import _mysql

# date : 2016-05-11
# environment : by python3.4.4
# description: mysql slave Automatic detection slave error and Automatic repair
# author : 张玉坡(yupozhang@gmail.com)
# note: rely on mysqlclient and pip install mysqlclient


#发送邮件
class Servermail():
    def __init__(self):
        self.Server_user = "zhangyupo@xx.com"
        self.Server_pwd = "ttt88"
        self.Servers = "smtp.exmail.qq.com"

    def send_user_mail(self,title,connect,tomail):
        self.connect = connect
        self.title = title
        self.tomail = tomail

        msg = MIMEText(self.connect)
        msg["Subject"] = self.title
        msg["From"]    = self.Server_user
        msg["To"]      = ";".join(self.tomail)
        try:
            with smtplib.SMTP(self.Servers, timeout=30) as s:
                s.login(self.Server_user, self.Server_pwd)#登陆服务器
                s.sendmail(self.Server_user,self.tomail, msg.as_string())#发送邮件
                print("发送成功")
        except Exception as e:
            print(e)
            print("发送失败")


#连接mysql服务器,执行sql
def mysql_con(sql):
    try:
        conn=MySQLdb.connect(host='10.88.88.7',user='admin',port=3307,passwd='admin)',unix_socket='/tmp/mysql3.sock')
        cur=conn.cursor()
        cur.execute(sql)
        data = cur.fetchone()
        cur.close()
        conn.close()
        return data
    except Exception as e:
        save_check_logs('数据连接错误',e)



#保存日志
def save_check_logs(title,connect):
    dspath = '/data/backup'
    logname = "{0}/check_slavedb.log".format(dspath)
    logformat = ('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
    logging.basicConfig(level=logging.DEBUG,format=logformat,filename=logname,filemode='a')
    logging.info('数据库状态：{0} 内容： {1}' .format(title,connect))
    s = Servermail()
    mailuser = ["zhangyupo@yunjiazheng.com"]
    s.send_user_mail(title,connect,mailuser)


#检查主从是否同步
def check_slave(num=0):
    sql = 'show slave status'
    if num >= 5:
        title = '修复错误'
        connect = '超过修复最大次数，请登录服务器查看详情'
        save_check_logs(title,connect)
        return False
    slave_info = mysql_con(sql)
    #print(slave_info)
    if slave_info[10] == 'Yes' and slave_info[11] == 'Yes' :
        return True
    else:
        #145是表损坏，1062是主键冲突。
        if slave_info[18] == 144 or slave_info[18] == 145:
            r_table = slave_info[19].split(' ')
            repair_tables(r_table[2],num)
        elif slave_info[18] == 1062 :
            skip_primary_id()
        elif slave_info[18] == 126 :
            restart_slave3()
        else:
            title = '错误'
            connect = '未知的错误类型，请登录服务器手动修复'
            save_check_logs(title,connect)




#修复损坏的表
def repair_tables(tables,num):
    if tables:
        command = 'cd /data/mysql/ && /usr/local/bin/myisamchk -r -q {0}.MYI' .format(tables)
        print(command)
        status = os.system(command)
        if status == 0:
            restart_slave3()
            num += 1
            new_status = check_slave(num)
            if new_status :
                title = '修复成功'
                connect = '数据修复成功，表名:{0}'.format(tables)
                save_check_logs(title,connect)
        else:
            title = '修复失败'
            connect = '数据修复失败，表名:{0}'.format(tables)
            save_check_logs(title,connect)



#跳过主键冲突的id
def skip_primary_id():
    sql ='stop slave;SET GLOBAL SQL_SLAVE_SKIP_COUNTER = 1;start slave;'
    sts = mysql_con(sql)
    print(sts)



#重启数据库实例
def restart_slave3():
    os.system('/usr/local/bin/mysqld_multi stop 3')
    time.sleep(2)
    os.system('/usr/local/bin/mysqld_multi start 3')
    time.sleep(3)




if __name__ == '__main__':
    check_slave()