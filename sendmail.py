import smtplib
from email.mime.text import MIMEText

# send mails script and please use python3 run  
# date: 2016-04-27
# author: [yupozhang@gmail.com]



# _user = "z@y.com"
# _pwd  = "Rxxxx"
# _to   = "yug@qq.com"
#
# #使用MIMEText构造符合smtp协议的header及body
# msg = MIMEText("店铺备份成功。。。")
# msg["Subject"] = "线上数据库备份成功"
# msg["From"]    = _user
# msg["To"]      = _to
#
# s = smtplib.SMTP("smtp.exmail.qq.com", timeout=30)#连接smtp邮件服务器,端口默认是25
# s.login(_user, _pwd)#登陆服务器
# s.sendmail(_user, _to, msg.as_string())#发送邮件
# s.close()

class Servermail():
    def __init__(self):
        self.Server_user = "zp@y.com"
        self.Server_pwd = "xxxxx"
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
                s.login(self.Server_user, self.Server_pwd)					#登陆服务器
                s.sendmail(self.Server_user,self.tomail, msg.as_string())	#发送邮件
                print("发送成功")
        except Exception as e:
             print("发送失败")


			 
#mails = Servermail()
#mailuser = ["zpo@yu.com","yupozhang@gmail.com"]
#mails.send_user_mail('来自python标题3','测试发送多个用户的邮件3',mailuser)