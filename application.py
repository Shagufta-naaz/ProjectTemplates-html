from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_mysqldb import MySQL
from flask_mail import Mail,Message
import requests

url = "https://www.fast2sms.com/dev/bulk"

application=Flask(__name__)
application.secret_key="mp3"
application.config['MYSQL_USER']='root'
application.config['MYSQL_PASSWORD']='password'
application.config['MYSQL_HOST']='localhost'
application.config['MYSQL_DB']='mp3'
mysql=MySQL(application)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'meghana180799@gmail.com',
    "MAIL_PASSWORD": 'meghana07!'
}
application.config.update(mail_settings)
mail = Mail(application)

application.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@application.route('/register',methods=["GET","POST"])
def mp3_register():
    if request.method == "POST":
        details=request.form
        uname=str(details['username'])
        aadharno=details['aadharno']
        conno=int(details['contactno'])
        emailid=str(details['emailid'])
        password=str(details['password'])
        cur = mysql.connection.cursor()
        cur.execute('''SELECT * FROM users''')
        results = cur.fetchall()
        session['username']=uname
        for i in results:
            if(str(i[0])==uname):
                return "Try a different user name"
        cur.execute("insert into users(username,aadharno,contactno,emailid,password) values(%s,%s,%s,%s,%s)",(uname,aadharno,conno,emailid,password))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@application.route('/',methods=["GET","POST"])
def mp3_login():
    if 'username' in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        details=request.form
        uname=str(details['U-name'])
        password=str(details['password'])
        cur = mysql.connection.cursor()
        cur.execute('''SELECT * FROM users''')
        results = cur.fetchall()
        for i in results:
            if(str(i[0])==uname):
                if(str(i[4])==password):
                    session['username']=uname
                    #flash('You are successfully logged in')
                    return redirect(url_for('login'))    #logged in
        return "<h3>Incorrect username or password<h3>" #incorrect password
        #error="Incorrect username or password"
        mysql.connection.commit()
        cur.close()
    return render_template('login.html')
@application.route('/login',methods=['POST','GET'])
def login():
    if ('username' not in session):
        return redirect(url_for('mp3_login'))
    #response.headers['Cache-Control'] = 'no-cache'
    x=[]
    y=[]
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM problems''')
    results=cur.fetchall()
    for i in results:
        x.append(i[0])
        y.append(i[1])
    colors = ["rgba(151,187,205,0.2)","rgba(151,187,205,0.2)","blue","red","red","red"]
    return render_template('mainpage.html',uname=session['username'],x=x,y=y,colors=colors)
@application.route('/back',methods=['GET'])
def back():
    return redirect(url_for('login'))
@application.route('/problem',methods=['GET','POST'])
def mp3_problem():
    if ('username' not in session):
        return redirect(url_for('mp3_login'))
    cur = mysql.connection.cursor()
    su=session['username']
    cur.execute('''SELECT * from users where username=%s''',(su,))
    resu=cur.fetchone()
    if(resu[5]==1):
        return redirect(url_for('login'))
    if request.method=="POST":
        z=request.form['problem']
        cur.execute('''SELECT * FROM problems''')
        results = cur.fetchall()
        cur.execute('''SELECT * from users where username=%s''',(su,))
        res=cur.fetchone()
        print(results)
        if(res[5]==1):
            return render_template("alreadyVoted.html")
        for i in results:
            if(i[0]==z and res[5]==0):
                cur.execute("update users set voted=%s where username=%s",(1,su))
                cur.execute("update users set problem=%s where username=%s",(z,su))
                v=i[1]+1
                cur.execute("update problems set vote=%s where problem=%s",(v,z))
                cur.execute("SELECT * from problems")
                res=cur.fetchall()
                for j in res:
                    n=j[1]
                    if(n==10):
                        p=j[0]
                        msg = Message('Municipality Related Issue', sender = 'meghana180799@gmail.com', recipients = ['meghana180799@gmail.com'])
                        msg.body = "The problem "+p+" requires immediate attention"
                        mail.send(msg)
                
                        payload = "sender_id=FSTSMS&message=The problem frequent power cuts requires immediate attention&language=english&route=p&numbers=9963865299"
                        headers = { 'authorization': "9YgRBZ6bcvA0jN3tMQSwipDFCoXJhm8I7uGE5nlfrd2ez1OPKxi5zH3tDLeS6nK87J9R0uVcqwTdNkX4", 
                                    'Content-Type': "application/x-www-form-urlencoded",
                                    'Cache-Control': "no-cache",
                                  }
                        response = requests.request("POST", url, data=payload, headers=headers)
                        print(response.text)
                        cur.execute("update problems set vote=%s where problem=%s",(0,p))
                        cur.execute("update users set voted=%s and problem=%s where problem=%s",(0,'NULL',p))
            
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('login'))
                #return render_template("VoteSuccess.html")
        return render_template("alreadyVoted.html")
    return render_template('mp3_problem.html')
@application.route('/about')
def about():
    return render_template('about.html')
@application.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username',None)
        return redirect(url_for('mp3_login'))
        response.headers['Cache-Control'] = 'no-cache'
    return redirect(url_for('mp3_login'))
@application.route('/already',methods=["GET","POST"])
def already():
    cur = mysql.connection.cursor()
    su=session['username']
    cur.execute("update users set voted=%s where username=%s",(0,su))
    #cur.execute("update users set problem=%s where username=%s",(N,su))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('login'))
#host= '0.0.0.0'
if __name__ == '__main__':
    application.run(debug=True)
    #application.run(host = '192.168.203.1',port=5000)
