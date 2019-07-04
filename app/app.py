from flask import Flask, render_template, request, session, redirect,url_for,flash
import MySQLdb
import HTML
import re
import sys
from bcrypt import hashpw, gensalt


app = Flask(__name__)
app.secret_key = "nishantchaudhary" #security key for session handling

db = MySQLdb.connect(host="localhost",  # your host, usually localhost
                             user="root",  # your username
                             passwd="rkuktkkk",  # your password
                             db="secure")   #name database
cur = db.cursor()


#homepage
@app.route('/')
@app.route('/home')
def mainPage():
    return render_template('mainPage.html')


#login page
@app.route('/login')
def login():
    return render_template('login.html')



@app.route('/loginUser',methods = ['POST'])
def loginUser():
    if request.method == 'POST':
        result = request.form
        if result['uname'] == 'admin' and result['psw'] == 'admin':   #admin
            session['username'] = result['uname']
            session['name'] = result['uname']
            return render_template('adminHome.html')
        else:
            sql = "SELECT * from users WHERE Uname = %s and Pass = %s;"   #user
            val = (result['uname'], result['psw'])
            cur.execute(sql, val)
            myresult = cur.fetchone()
            if myresult:
                session['username'] = result['uname'];
                session['name'] = result['uname'];
                #if user is not blocked
                if not myresult[8]=='blocked':
                    return render_template('userHome.html')
                else:
                    return "You are blocked, Please consult your admin!"
            else:
                return render_template('login.html')        #wrong credentials


#registration
@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/makeAccount', methods = ['POST'])
def makeAccount():
    if request.method == 'POST':
        result = request.form
        r_name = re.compile ('^[A-Za-z]\'?[A-Za-z]?[a-z]*\,?\s?[A-Z]?\'?[A-Z]?[a-z]*\-?\s?[A-Z]?[a-z]*\.?$')
        r_phone = re.compile ('^\+?\d{0,3}\s?\(?\d{0,5}(\)?[-.\s]?\d{3}[-.\s]?\d{4})?$')
        r_username = re.compile('^[A-Z]?[a-z]*?[\d]{0,4}?$')
        m_name1 = re.search(r_name,result['First'])
        m_name2 = re.search(r_name,result['Last'])
        m_phone = re.search(r_phone,result['phone'])
        m_username = re.search(r_username,result['username'])
        if((m_name1 and m_name2) and (m_phone and m_username)):
            
            sql = "INSERT INTO users (Fname, Lname, Gender, Age, Phone, Email, Uname, Pass) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val1 = result['psw'].encode('utf-8')
            hashed = hashpw(val1,gensalt())
            val = (result['First'], result['Last'], result['gender'], result['Age'], result['phone'], result['email'], result['username'], hashed)
            cur.execute(sql, val)

            db.commit()
        else:
            flash('Incorrect input')
            return redirect(url_for('register'))
    
             

        return render_template('login.html')


#admin homepage
@app.route('/adminHome')
def adminHome():
    return render_template('adminHome.html')


#update profile admin
@app.route('/updateProfileAdmin')
def updateProfileAdmin():
    sql = "SELECT * from users WHERE Uname = '"+session['username']+"';"
    cur.execute(sql)
    myresult = cur.fetchall()

    return render_template('updateProfileAdmin.html',data = myresult[0])


@app.route('/updateAdmin', methods=['POST'])
def updateAdmin():
    # write update query here
    if request.method == 'POST':
        result = request.form
        print(result)
        sql = "UPDATE users SET Fname = '{}', Lname = '{}', Gender = '{}', Age = '{}', Phone = '{}', Email = '{}', Pass = '{}'  \
              WHERE Uname = '{}'".format(result['First'], result['Last'], result['gender'], result['Age'], result['phone'], \
                                         result['email'], result['psw'], result['username'])

        cur.execute(sql)

        db.commit()

    return render_template('adminHome.html')


#view users list(admin)
@app.route('/usersListAdmin')
def usersListAdmin():
    sql = "SELECT Uname from users"
    cur.execute(sql)

    my_result = cur.fetchall()
    my_list = [each[0] for each in my_result]

    #print(my_list)

    return render_template('usersListAdmin.html', data=my_list)


@app.route('/getuserList')
def getuserList():
    sql = "SELECT Uname from users"
    cur.execute(sql)
    my_result = cur.fetchall()
    my_list = [each[0] for each in my_result]
    #print(my_list )
    return my_list


#update user profile (admin)
@app.route('/updateProfileUserAdmin', methods=['POST'])
def updateProfileUserAdmin():
    if request.method == 'POST':
        result = request.form
        sql = "UPDATE users SET Fname = '{}', Lname = '{}', Gender = '{}', Age = '{}', Phone = '{}', Email = '{}'  \
              WHERE Uname = '{}'".format(result['First'], result['Last'], result['gender'], result['Age'], result['phone'], \
                                         result['email'], result['username'])

        cur.execute(sql)

        db.commit()

    return render_template('adminHome.html')

@app.route('/blockuser')
def block():
    return render_template('blockuser.html')
    
@app.route('/blockuseradmin', methods=['POST'])
def blockuser():
    
    if request.method == 'POST':
        result = request.form
        sql = "UPDATE users SET status='blocked' WHERE Uname='{}'".format(result['username'])
        cur.execute(sql)

        db.commit()

    return render_template('adminHome.html')

@app.route('/usertransactions')
def viewusert():
    return render_template('usertransactions.html')


@app.route('/updateProfileUser', methods=['POST'])
def updateProfileUser():

    username = request.form['user_list']

    sql = "SELECT * from users WHERE Uname = '{}'".format(username)
    cur.execute(sql)
    my_data = cur.fetchall()

    data = [each for each in my_data[0]]

    return render_template('userProfileAdmin.html', data=data)


#user home
@app.route('/userHome')
def userHome():
    return render_template('userHome.html')


#update profile(user)
@app.route('/updateProfile')
def updateProfile():

    sql = "SELECT * from users WHERE Uname = '" + session['username'] + "';"
    cur.execute(sql)
    my_result = cur.fetchall()

    return render_template('updateProfileUser.html', data=my_result[0])


@app.route('/updateUser', methods=['POST'])
def updateUser():
    if request.method == 'POST':
        result = request.form

        sql = "UPDATE users SET Fname = '{}', Lname = '{}', Gender = '{}', Age = '{}', Phone = '{}', Email = '{}', Pass = '{}'  \
              WHERE Uname = '{}'".format(result['First'], result['Last'], result['gender'], result['Age'], result['phone'], \
                                         result['email'], result['psw'], result['username'])

        cur.execute(sql)

        db.commit()

    return render_template('userHome.html')


#wallet
@app.route('/wallet')
def wallet():
    
    uname = session['username']
    query = "SELECT Amount FROM addmoney WHERE username='{}'".format(uname)
    cur.execute(query)
    records = cur.fetchall()
    html = HTML.table(records, header_row=['Amount'])
    
        
    return render_template('walletUser.html')    


#add money
@app.route('/addmoney')
def addmoney():
    return render_template('transactionUser.html')


@app.route('/moneyadd', methods=['POST'])
def moneyadd():
    uname = session['username']
    result = request.form
    val2 = int(result['amount'])
    if request.method =='POST':
        result = request.form
        sql = "INSERT INTO addmoney (Cardname, Cardno, Amount, username) VALUES (%s, %s, %s,%s)"
        val = (result['Name'], result['First'], result['amount'],uname)
        cur.execute(sql, val)
        db.commit()
        
    return render_template('userHome.html')
    
    


#send money
@app.route('/sendmoney')
def sendmoney():
    return render_template('sendMoneyUser.html')

#change the url path according to the webpage invokation
@app.route("/viewusertransactions", methods=['POST'])
def getTransactions():
    if request.method == 'POST':
        result = request.form
        query = "SELECT *FROM TRANSACTIONS WHERE SENDER= '{}'".format(result['username'])
        cur.execute(query)
        records = cur.fetchall()
        html = HTML.table(records, header_row=['Transaction ID', 'Sender', 'Recipient', 'Amount', 'Transaction Date & Time'])
        return html

@app.route('/searchuser', methods=['POST'])
def searchuser():
    if request.method == 'POST':
        result = request.form
        print(result['username'])
        username = result['username']
        sql = "SELECT Fname, Lname from users WHERE Uname = '{}'".format(username)
        cur.execute(sql)
        my_result = cur.fetchall()

        my_list = [my_result[0][0], my_result[0][1]]

        return render_template('searchResultUser.html', data=my_list)


@app.route('/moneysend', methods=['POST'])
def moneysend():
    uname = session['username']
    
    if request.method =='POST':
        result = request.form
        val1 = result['sender']
        val2 = int(result['amount'])
        query = "SELECT Amount FROM addmoney WHERE username='{}'".format(uname)
        val3 = cur.execute(query)
        my_result =cur.fetchone()
        val4 = int(("".join(my_result)))
        val6 = result['my_list']
        if ((uname==val1)and(val4>=val2)):
            
            sql = "INSERT INTO TRANSACTIONS (SENDER, RECIPIENT, AMOUNT) VALUES (%s, %s, %s)"
            val = (result['sender'], result['my_list'], result['amount'])
            cur.execute(sql, val)
            sql2 = "UPDATE TRANSACTIONS INNER JOIN users ON TRANSACTIONS.RECIPIENT=users.Fname SET TRANSACTIONS.username=users.Uname "
            cur.execute(sql2)
            sql3 = "SELECT username FROM TRANSACTIONS WHERE RECIPIENT='{}'".format(val6)
            val7 = cur.execute(sql3)
            my_result1 = cur.fetchone()
            val8 = ("".join(my_result1))# add money to recipient in wallet
            val5=str(val4-val2)
            args = [val5, ]
            sql1 = "UPDATE addmoney SET Amount=%s WHERE username='{}'".format(uname)
            cur.execute(sql1,args)
            sql4 = "SELECT Amount FROM addmoney WHERE username='{}'".format(val8)
            val9 = cur.execute(sql4)
            my_result2 =cur.fetchone()
            val10 = int(("".join(my_result2)))
            val11 = str(val10+val2)
            args1 = [val11, ]
            sql5 = "UPDATE addmoney SET Amount=%s WHERE username='{}'".format(val8)
            cur.execute(sql5,args1)
            db.commit()
            
        else:
            flash('Sender should be equal to Username and Enough money should be present in wallet')
            return redirect(url_for('sendmoney'))
    return render_template('userHome.html')


@app.route('/transfertobank')
def transfertobank():
    return render_template('transferBankUser.html')

@app.route('/transfertobankamount', methods=['POST'])
def transferbank():
    uname = session['username']
    if request.method =='POST':
        result = request.form
        val1 = result['sender']
        val2 = int(result['amount'])
        query = "SELECT Amount FROM addmoney WHERE username='{}'".format(uname)
        val3 = cur.execute(query)
        my_result =cur.fetchone()
        val4 = int(("".join(my_result)))
        if ((uname==val1)and(val4>=val2)):
            sql = "INSERT INTO TRANSACTIONS (SENDER, RECIPIENT, AMOUNT) VALUES (%s, %s, %s)"
            val = (result['sender'], "Bank", result['amount'])
            cur.execute(sql, val)
            sql2 = "UPDATE TRANSACTIONS INNER JOIN users ON TRANSACTIONS.SENDER=users.Fname SET TRANSACTIONS.username=users.Uname "
            cur.execute(sql2)
            val5=str(val4-val2)
            args = [val5, ]
            sql1 = "UPDATE addmoney SET Amount=%s WHERE username='{}'".format(uname)#subtract money from addmoney table
            cur.execute(sql1,args)
            db.commit()
    return render_template('userHome.html')      
    
    


#logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)  #debug mode