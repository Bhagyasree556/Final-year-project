from flask import Flask, render_template, request, session, redirect, url_for, flash,send_file,jsonify
import hashlib
import pandas as pd
from flask_mail import *
import secrets
import os
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import secrets
from werkzeug.utils import secure_filename
from blockchain import *
import mysql.connector

import qrcode # type: ignore
import os
from flask import send_file
import mysql.connector

MAX_RETRIES = 3

mydb = mysql.connector.connect(host="localhost",user="root",passwd="",database="directmarketingagriculture",charset='utf8',port=3306)
mycursor = mydb.cursor()

# def mydb():
#     mydb = mysql.connector.connect(host="localhost",user="root",passwd="",database="directmarketingagriculture",charset='utf8',port=3307)
#     mycursor = mydb.cursor()
#     return mycursor,mydb

UPLOAD_FOLDER = '/path/to/the/uploads'


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


#Index Page or home page
@app.route('/')
def index():
    return render_template('index.html')


#Admin Page
@app.route('/admin')
def admin():
    return render_template('admin.html')


#Admin Login page
@app.route("/adminlog", methods=["POST", "GET"])
def adminlog():
    if request.method == "POST":
        username = request.form['email']
        password = request.form['password']
        if username == 'admin@gmail.com' and password == 'admin':
            return render_template('adminhome.html', msg="Login successfull")
        else:
            return render_template('admin.html', msg="Login Failed!!")
    return render_template('admin.html')



#admin home page.
@app.route("/adminhome")
def adminhome():
    return render_template('adminhome.html')



#add crop price by admin
@app.route("/addcropinfo", methods=["POST", "GET"])
def addcropinfo():
    if request.method == "POST":
        cropname = request.form['subcategory']
        category = request.form['category']
        Minimumcost = request.form['Minimumcost']
        myfile = request.files['myfile']
        filename = myfile.filename
        path=os.path.join("static/profiles/", filename)
        myfile.save(path)
        profilepath = "static/profiles/"+filename
        sql = "insert into cropinfo (cropname, category, Minimumcost,myfile) values (%s, %s, %s, %s)"
        val = (cropname, category, Minimumcost,profilepath)
        mycursor.execute(sql, val)
        mydb.commit()
        return redirect(url_for('addcropinfo'))
    return render_template('addcropinfo.html', msg="Crop Details added successfully")



#View sellers by admin
@app.route("/viewseller")
def viewseller():
    sql = "select * from sellers"
    data = pd.read_sql_query(sql, mydb)
    print(data)
    return render_template('viewseller.html', cols=data.columns.values, rows=data.values.tolist())



#View buyers  by admin
@app.route("/viewbuyer")
def viewbuyer():
    sql = "select * from buyers"
    data = pd.read_sql_query(sql, mydb)
    print(data)
    return render_template('viewsbuyer.html', cols=data.columns.values, rows=data.values.tolist())



#===========   Login sellers  ======================
@app.route("/sellerslog", methods=["POST", "GET"])
def sellerslog():
    if request.method == "POST":
        semail = request.form['semail']
        password = request.form['password']
        sname = request.form['sname']
        
        import json

        blockchain_data = retrieveData()

# ✅ SIMPLE SAFE FIX
        if not blockchain_data:
            blockchain_data = []
        else:
            if isinstance(blockchain_data, str):
                try:
                    blockchain_data = json.loads(blockchain_data)
                except:
                    blockchain_data = []
        safe_data = []
        for item in blockchain_data:
            if isinstance(item, str):
                try:
                    safe_data.append(json.loads(item))
                except:
                    continue
            else:
                safe_data.append(item)

        blockchain_data = safe_data

        seller_in_blockchain = next(
            (item for item in blockchain_data if item.get('seller_email') == semail),
            None
        )    
      # ✅ FIX END
        
        seller_in_blockchain = next((item for item in blockchain_data if item.get('seller_email') == semail), None)
        
        if seller_in_blockchain:
            if seller_in_blockchain.get('is_blocked', 'unblock') == 'blocked':
                flash("Your account has been blocked by admin. Please contact support.", "danger")
                return render_template('sellerslog.html')
            
        hashedpassword = hashlib.md5(password.encode()).hexdigest()
        
        sql = "SELECT * FROM sellers WHERE semail = %s AND password = %s"
        mycursor.execute(sql, (semail, hashedpassword))
        results = mycursor.fetchall()
        
        if results:
            seller = results[0]
            session['sellername'] = sname
            session['sellersemail'] = semail
            flash("Login Successful, Agriculture Marketing", "success")
            return render_template('sellershome.html', data=results)
        else:
            flash("Credentials don't exist", "warning")
            return render_template('sellerslog.html')
        
    return render_template('sellerslog.html')


@app.route("/Sellers", methods=["POST", "GET"])
def Sellers():
    if request.method == "POST":
        sname = request.form['sname']
        semail = request.form['semail']
        password = request.form['password']
        password1 = request.form['Con_Password']
        contact = request.form['mobile']
        address = request.form['address']
        myfile = request.files['myfile']
        filename = myfile.filename
        hashedpassword = hashlib.md5(password.encode())
        hashpassword = hashedpassword.hexdigest()
        if password == password1:
            print(password)
            sql="select * from sellers where semail='%s' and password='%s'"%(semail,hashpassword)
            mycursor.execute(sql)
            data=mycursor.fetchall()
            print(data)
            if data==[]:
                path=os.path.join("static/profiles/", filename)
                myfile.save(path)
                profilepath = "static/profiles/"+filename
            print(sname, semail, password, address)
            sql = "insert into sellers(sname,semail,password,contact,address,profile)values(%s,%s,%s,%s,%s,%s)"
            val = (sname, semail, hashpassword , contact, address,profilepath)
            mycursor.execute(sql, val)
            mydb.commit()
            return render_template('sellerslog.html')
        else:
                flash('Details already Exist',"warning")
                return render_template('sellers.html')
    return render_template('sellers.html')


#=======================   Forgot password for sellers   =======================
@app.route("/forgotpassword",methods=['POST','GET'])
def forgotpassword():
    if request.method=="POST":
        semail = request.form['semail']
        sql = "select * from sellers where semail='%s'"%(semail)
        mycursor.execute(sql)
        data = mycursor.fetchall()
        mydb.commit()
        if data !=[]:
            msg ='valid'
            session['sforgotemail'] = semail
            return render_template('forgotpassword.html',msg=msg)
        else:
            msg="notvalid"
            flash("Provide Valid Email","warning")
            return render_template('sellerslog.html',msg=msg)
    return render_template('forgotpassword.html',msg='check')


@app.route("/updatepassword",methods=['POST','GET'])
def updatepassword():
    if request.method=="POST":
        form = request.form
        semail = session['sforgotemail']
        password = form['password']
        confirmpassword =  form['confirmpassword']
        if password == confirmpassword:
            hashedpassword = hashlib.md5(password.encode())
            hashpassword = hashedpassword.hexdigest()
            sql = "select * from sellers where semail='%s'"%(semail)
            mycursor.execute(sql)
            data = mycursor.fetchall()
            mydb.commit()
            if data:
                sql= "update sellers set password='%s' where semail='%s'"%(hashpassword,session['sforgotemail'])
                mycursor.execute(sql)
                mydb.commit()
                flash("Password Updated Successfully","success")
                return redirect(url_for("sellerslog"))
        else:
                return render_template("sellerslog.html")


#==============    Sellers Home page   =====================
@app.route("/sellershome")
def sellershome():
    return render_template('sellershome.html')


#===================   View sellers profile   ==========================
@app.route("/sellerprofile")
def sellerprofile():
    sql = "select * from sellers where semail='%s'"%(session['sellersemail'])
    data = pd.read_sql_query(sql, mydb)
    print(data)
    return render_template('sellerprofile.html', cols=data.columns.values, rows=data.values.tolist())


#==========================   View crop details  =========================
@app.route("/viewcropprice")
def viewcropprice():
    sql = "select * from cropinfo"
    data = pd.read_sql_query(sql, mydb)
    print(data)
    return render_template('viewcropprice.html', cols=data.columns.values, rows=data.values.tolist())



# ==================== Define the maximum number of retries  ==============
MAX_RETRIES = 3
@app.route("/updatecrop/<int:id>", methods=["POST", "GET"])
def updatecrop(id=0):
    sql = "SELECT * FROM cropinfo WHERE id=%s" % (id)
    mycursor.execute(sql)
    data = mycursor.fetchall()
    return render_template('updatecrop.html', loanid=data[0][0], data=data)


# =========Update crop details, generate QR code, save path in DB, and download QR code
@app.route('/updatecropdetails', methods=["POST", "GET"])
def updatecropdetails():
    sql = "SELECT * FROM sellers WHERE semail='%s'" % (session['sellersemail'])
    mycursor.execute(sql)
    data = mycursor.fetchall()
    address = data[0][5]
    
    if request.method == "POST":
        cropname = request.form['cropname']
        category = request.form['category']
        mincost = request.form['mincost']
        semail = session['sellersemail']
        quantity = request.form['quantity']
        Yieldtime = request.form['Yieldtime']
        myfile = request.files['myfile']
        filename = myfile.filename
        totalquantity = quantity
        
        check_sql = "SELECT * FROM cropprice WHERE cropname = %s AND category = %s AND semail = %s"
        mycursor.execute(check_sql, (cropname, category, semail))
        existing_crop = mycursor.fetchone()
        
        if existing_crop:
            return "Crop details already exist. Please update the existing entry."
        
        path = os.path.join("static/profiles/", filename)
        myfile.save(path)
        profilepath = "static/profiles/" + filename
        
        qr_data = f"Crop: {cropname}\nCategory: {category}\nMin Cost: {mincost}\nQuantity: {quantity}\nYield Time: {Yieldtime}\nSeller Email: {semail}\nAddress: {address}"
        
        qr = qrcode.make(qr_data)
        qr_filename = f"{cropname}_qr.png"
        qr_path = os.path.join("static/qr/", qr_filename)
        qr.save(qr_path)
        
        qr_db_path = "static/qr/" + qr_filename
        for attempt in range(MAX_RETRIES):
            try:
                sql = """INSERT INTO cropprice (cropname, category, mincost, quantity, Yieldtime, myfile, semail, address, totalquantity, qr_path)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                val = (cropname, category, mincost, quantity, Yieldtime, profilepath, session['sellersemail'], address, totalquantity, qr_db_path)
                mycursor.execute(sql, val)
                mydb.commit()
                break
            
            except mysql.connector.errors.DatabaseError as e:
                if e.errno == 1412:
                    print(f"Retry {attempt + 1}/{MAX_RETRIES} due to DatabaseError: {e}")
                    if attempt == MAX_RETRIES - 1:
                        return "Failed to update crop details. Please try again later."
                else:
                    raise e
                
        return send_file(qr_path, as_attachment=True, download_name=qr_filename)
    
    return redirect(url_for('viewcropprice'))


@app.route("/viewcrop")
def viewcrop():
    sql = "SELECT * FROM cropprice WHERE semail='%s'" % (session['sellersemail'])
    data = pd.read_sql_query(sql, mydb)
    print(data)
    return render_template('viewcrop.html', cols=data.columns.values, rows=data.values.tolist())


@app.route("/buyerlog", methods=["POST", "GET"])
def buyerlog():
    if request.method == "POST":
        bemail = request.form['bemail']
        password = request.form['password']
        hashedpassword = hashlib.md5(password.encode())
        hashpassword = hashedpassword.hexdigest()
        sql = "select * from buyers where bemail='%s' and password='%s'" % (bemail, hashpassword)
        mycursor.execute(sql)
        results = mycursor.fetchall()
        if results != []:
            session['buyersemail'] = bemail
            session['buyeraddress'] = results[0][5]
            flash("Login Successfull, Agricultaure Markiting","Success")
            return render_template('buyerhome.html',data=results)
        else:
            flash("Credential's Doesn't Exist","warning")
            return render_template('buyerslog.html')        
    return render_template('buyerslog.html')



@app.route("/Buyers", methods=["POST", "GET"])
def Buyers():
    if request.method == "POST":
        bname = request.form['bname']
        bemail = request.form['bemail']
        password = request.form['password']
        password1 = request.form['Con_Password']
        contact = request.form['mobile']
        address = request.form['address']
        myfile = request.files['myfile']
        filename = myfile.filename
        if password == password1:
            hashedpassword = hashlib.md5(password.encode())
            hashpassword = hashedpassword.hexdigest()
            sql="select * from buyers where bemail='%s' and password='%s'"%(bemail,hashpassword)
            mycursor.execute(sql)
            data=mycursor.fetchall()
            print(data)
            if data==[]:
                path=os.path.join("static/profiles/", filename)
                myfile.save(path)
                profilepath = "static/profiles/"+filename
                print(bname, bemail, password, address)
                sql = "insert into buyers(bname,bemail,password,contact,address,profile)values(%s,%s,%s,%s,%s,%s)"
                val = (bname, bemail, hashpassword, contact, address,profilepath)
                mycursor.execute(sql, val)
                mydb.commit()
                return render_template('buyerslog.html')
            else:
                flash('Details already Exist',"warning")
                return render_template('buyres.html')
        else:
            flash('password not matched')
            return render_template('buyres.html')
    return render_template('buyres.html')



@app.route("/bforgotpassword",methods=['POST','GET'])
def bforgotpassword():
    if request.method=="POST":
        bemail = request.form['bemail']
        sql = "select * from buyers where bemail='%s'"%(bemail)
        mycursor.execute(sql)
        data = mycursor.fetchall()
        mydb.commit()
        if data !=[]:
            msg ='valid'
            session['bforgotemail'] = bemail
            return render_template('bforgotpassword.html',msg=msg)
        else:
            msg="notvalid"
            flash("Provide Valid Email","warning")
            return render_template('buyerslog.html',msg=msg)
    return render_template('bforgotpassword.html',msg='check')



@app.route("/bupdatepassword",methods=['POST','GET'])
def bupdatepassword():
    if request.method=="POST":
        form = request.form
        bemail = session['bforgotemail']
        password = form['password']
        confirmpassword =  form['confirmpassword']
        if password == confirmpassword:
            hashedpassword = hashlib.md5(password.encode())
            hashpassword = hashedpassword.hexdigest()
            sql = "select * from buyers where bemail='%s'"%(bemail)
            mycursor.execute(sql)
            data = mycursor.fetchall()
            mydb.commit()
            if data:
                sql= "update buyers set password='%s' where bemail='%s'"%(hashpassword,session['bforgotemail'])
                mycursor.execute(sql)
                mydb.commit()
                flash("Password Updated Successfully","success")
                return redirect(url_for("buyerlog"))
        else:
            return render_template("buyerslog.html")
    return render_template("buyerslog.html")



@app.route("/buyerhome")
def buyerhome():
    return render_template('buyerhome.html')



@app.route("/buyerprofile")
def buyerprofile():
    
    sql = "select * from buyers where bemail='%s'"%(session['buyersemail'])
    mycursor.execute(sql)
    data = mycursor.fetchall()
    return render_template("buyerprofile.html",rows=data)


@app.route('/noti')
def noti():
    return render_template('noti.html')


@app.route("/viewsellerprofile")
def viewsellerprofile():
    sql = "select * from sellers where semail='%s'"%(session['sellersemail'])
    data = pd.read_sql_query(sql, mydb)
    print(data)
    return render_template('sellershome.html', cols=data.columns.values, rows=data.values.tolist())


@app.route("/aspr/<id>")
def aspr(id=0):
    print(id)
    sql = "select * from sellers where status='pending'"
    mycursor.execute(sql)
    dc = mycursor.fetchall()
    print(dc)
    print("**********")
    semail = dc[0][2]
    password = dc[0][3]
    print(semail, password)
    
    status='Accepted'
    otp="Your File accepted and this is your secret Key :"
    skey = secrets.token_hex(4)
    print("secret key", skey)
    mail_content ='Your request is accepted by Admin and email is :'+ semail + ' ' 
    sender_address = 'appcloud887@gmail.com'
    sender_pass = 'uihywuzqiutvfofo'
    receiver_address = semail
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Decentralized Traceability and Direct Marketing of Agriculture Supply Chains'
    message.attach(MIMEText(mail_content, 'plain'))
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    
    sql = "update sellers set status='Accepted' where id='%s'" % (id)
    mycursor.execute(sql)
    mydb.commit()
    flash('Admin given the authontication for lender', 'success')
    return redirect(url_for('viewseller'))



@app.route("/rejectseller/<id>")
def rejectseller(id=0):
    print(id)
    sql = "select * from sellers where status='pending'"
    mycursor.execute(sql)
    dc = mycursor.fetchall()
    print(dc)
    print("**********")
    semail = dc[0][2]
    password = dc[0][3]
    print(semail, password)
    
    otp="Your File accepted and this is your secret Key :"
    skey = secrets.token_hex(4)
    print("secret key", skey)
    mail_content ='Your request is Rejected by Admin and email is :'+ semail + ' ' 
    sender_address = 'appcloud887@gmail.com'
    sender_pass = 'uihywuzqiutvfofo'
    receiver_address = semail
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Decentralized Traceability and Direct Marketing of Agriculture Supply Chains'
    message.attach(MIMEText(mail_content, 'plain'))
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    
    sql = "update sellers set status='Rejected' where id='%s'" % (id)
    mycursor.execute(sql)
    mydb.commit()
    return redirect(url_for('viewseller'))



@app.route("/baspr/<id>")
def baspr(id=0):
    print(id)
    sql = "select * from buyers where status='pending'"
    mycursor.execute(sql)
    dc = mycursor.fetchall()
    print(dc)
    print("**********")
    bemail = dc[0][2]
    password = dc[0][3]
    print(bemail, password)
    
    status='Accepted'
    otp="Your File accepted and this is your secret Key :"
    skey = secrets.token_hex(4)
    print("secret key", skey)
    mail_content ='Your request is accepted by Admin and email is :'+ bemail + ' ' 
    sender_address = 'appcloud887@gmail.com'
    sender_pass = 'uihywuzqiutvfofo'
    receiver_address = bemail
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Decentralized Traceability and Direct Marketing of Agriculture Supply Chains'
    message.attach(MIMEText(mail_content, 'plain'))
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    
    sql = "update buyers set status='Accepted' where id='%s'" % (id)
    mycursor.execute(sql)
    mydb.commit()
    flash('Admin given the authontication for lender', 'success')
    return redirect(url_for('viewbuyer'))



@app.route("/rejectbuyer/<id>")
def rejectbuyer(id=0):
    print(id)
    sql = "select * from buyers where status='pending'"
    mycursor.execute(sql)
    dc = mycursor.fetchall()
    print(dc)
    print("**********")
    bemail = dc[0][2]
    password = dc[0][3]
    print(bemail, password)
    
    otp="Your File accepted and this is your secret Key :"
    skey = secrets.token_hex(4)
    print("secret key", skey)
    mail_content ='Your request is Rejected by Admin and email is :'+ bemail + ' ' 
    sender_address = 'appcloud887@gmail.com'
    sender_pass = 'uihywuzqiutvfofo'
    receiver_address = bemail
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Decentralized Traceability and Direct Marketing of Agriculture Supply Chains'
    message.attach(MIMEText(mail_content, 'plain'))
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    
    sql = "update buyers set status='Rejected' where id='%s'" % (id)
    mycursor.execute(sql)
    mydb.commit()
    return redirect(url_for('viewbuyer'))


@app.route("/viewupdates")
def viewupdates():
    sql = "select * from cropprice"
    data = pd.read_sql_query(sql, mydb)
    print(data)
    return render_template('viewupdates.html', cols=data.columns.values, rows=data.values.tolist())


@app.route('/delete/<id>')
def delete(id=0):
    sql = "delete from cropprice where id='%s' " % (id)
    mycursor.execute(sql)
    mydb.commit()
    return redirect(url_for('viewcropprice'))



@app.route("/viewcropinfo")
def viewcropinfo():
    sql = "select * from cropprice"
    data = pd.read_sql_query(sql, mydb)
    print(data)
    return render_template('viewcropinfo.html', cols=data.columns.values, rows=data.values.tolist())


@app.route("/farmerproducts/<category>")
def farmerproducts(category):
    print(category)
    sql=""
    return render_template()


@app.route('/updatecropinfodetails', methods=["POST"])
def updatecropinfodetails():
    if request.method == "POST":
        id = request.form['id']
        cropname = request.form['subcategory']
        category = request.form['category']
        Minimumcost = request.form['Minimumcost']
        myfile = request.files['myfile']
        filename = myfile.filename
        
        path=os.path.join("static/profiles/", filename)
        myfile.save(path)
        profilepath = "static/profiles/"+filename
        
        sql = "UPDATE cropinfo SET cropname=%s, category=%s, Minimumcost=%s, myfile=%s  WHERE id=%s"
        val = (cropname, category, Minimumcost, profilepath, id)
        
        mycursor.execute(sql, val)
        mydb.commit()
        
        return redirect(url_for('viewcropinfo'))



@app.route("/adminsearchproduct",methods=["POST","GET"])
def adminsearchproduct():
    if request.method=="POST":
        
        try:
            searchproduct = request.form['search']    
            sql = "SELECT count(distinct semail),SUM(quantity) FROM cropprice WHERE cropname='%s' OR category='%s'" % (searchproduct, searchproduct)
            data = pd.read_sql_query(sql,mydb)      
            farmer_count = data.values[0][0]
            quantity_count = data.values[0][1]
            newsql = "SELECT * FROM cropprice WHERE cropname='%s' OR category='%s'" % (searchproduct, searchproduct)
            data = pd.read_sql_query(newsql,mydb)
            
        except:
            searchproduct = request.form['address']
            sql = "SELECT count(distinct semail),SUM(quantity) FROM cropprice WHERE address='%s'"%(searchproduct)
            data = pd.read_sql_query(sql,mydb)      
            farmer_count = data.values[0][0]
            quantity_count = data.values[0][1]
            newsql = "SELECT * FROM cropprice WHERE address='%s'" % (searchproduct)
            data = pd.read_sql_query(newsql,mydb)
        return render_template('viewcropinfo.html', cols=data.columns.values, rows=data.values.tolist(),farmercount=farmer_count,quantity_count=quantity_count)
    return redirect("viewcropinfo")



@app.route("/searchproduct",methods=["POST","GET"])
def searchproduct():
    if request.method=="POST":
        try:
            searchproduct = request.form['search']
            sql = "SELECT count(distinct semail),SUM(quantity) FROM cropprice WHERE cropname='%s' OR category='%s'" % (searchproduct, searchproduct)
            data = pd.read_sql_query(sql,mydb)      
            farmer_count = data.values[0][0]
            quantity_count = data.values[0][1]
            newsql = "SELECT * FROM cropprice WHERE cropname='%s' OR category='%s'" % (searchproduct, searchproduct)
            data = pd.read_sql_query(newsql,mydb)
        except:
            searchproduct = request.form['address']
            sql = "SELECT count(distinct semail),SUM(quantity) FROM cropprice WHERE address='%s'" %( searchproduct)
            data = pd.read_sql_query(sql,mydb)      
            farmer_count = data.values[0][0]
            quantity_count = data.values[0][1]
            newsql = "SELECT * FROM cropprice WHERE address='%s'" %(searchproduct)
            data = pd.read_sql_query(newsql,mydb)
        return render_template('viewallcrop.html', cols=data.columns.values, rows=data.values.tolist(),farmer_count=farmer_count,quantity_count=quantity_count)
    return redirect("viewallcrop")


@app.route("/scanqr")
def scanqr():
    sql = "select * from cropprice "
    mycursor.execute(sql)
    data1 = mycursor.fetchall()
    print(data1)
    cropname = data1[0][1]
    address = data1[0][8]
    print(cropname,address)
    sql = "select * from buyers where bemail='%s'"%(session['buyersemail'])
    mycursor.execute(sql)
    all_buyers = mycursor.fetchall()
    address_all = "select * from sellers where address='%s'"%(all_buyers[0][5])
    mycursor.execute(address_all)
    mydata = mycursor.fetchall()
    print(mydata)
    sql = "select * from cropprice"
    data = pd.read_sql_query(sql, mydb)
    print(data)
    return render_template('scanqr.html',data1=data1,cols=data.columns.values, rows=data.values.tolist())



@app.route("/update_status/<int:crop_id>", methods=["POST"])
def update_status(crop_id):
    sql = "UPDATE cropprice SET status='scanned' WHERE id=%s"
    val = (crop_id,)
    mycursor.execute(sql, val)
    mydb.commit()
    
    return jsonify({"status": "success", "message": "Status updated to scanned"})


@app.route("/viewscannedcrop")
def viewscannedcrop():
    sql = "select * from cropprice where status='scanned'"
    mycursor.execute(sql)
    data1 = mycursor.fetchall()
    print(data1)
    cropname = data1[0][1]
    address = data1[0][8]
    print(cropname,address)
    sql = "select * from buyers where bemail='%s'"%(session['buyersemail'])
    mycursor.execute(sql)
    all_buyers = mycursor.fetchall()
    address_all = "select * from sellers where address='%s'"%(all_buyers[0][5])
    mycursor.execute(address_all)
    mydata = mycursor.fetchall()
    print(mydata)
    sql = "select * from cropprice where status='scanned'"
    data = pd.read_sql_query(sql, mydb)
    print(data)
    return render_template('viewallcrop.html',data1=data1,cols=data.columns.values, rows=data.values.tolist())



@app.route("/viewallcrop")
def viewallcrop():
    sql = "select * from cropprice "
    mycursor.execute(sql)
    data1 = mycursor.fetchall()
    print(data1)
    cropname = data1[0][1]
    address = data1[0][8]
    print(cropname,address)
    sql = "select * from buyers where bemail='%s'"%(session['buyersemail'])
    mycursor.execute(sql)
    all_buyers = mycursor.fetchall()
    address_all = "select * from sellers where address='%s'"%(all_buyers[0][5])
    mycursor.execute(address_all)
    mydata = mycursor.fetchall()
    print(mydata)
    sql = "select * from cropprice"
    data = pd.read_sql_query(sql, mydb)
    print(data)
    return render_template('viewallcrop.html',data1=data1,cols=data.columns.values, rows=data.values.tolist())



@app.route("/sendrequest/<int:id>", methods=["GET", "POST"])
def sendrequest(id):
    print("Crop ID:", id)
    print("Buyer:", session.get('buyersemail'))
    
    sql = "SELECT * FROM cropprice WHERE id=%s"
    mycursor.execute(sql, (id,))
    data = mycursor.fetchall()
    
    if not data:
        return "Crop not found"
    
    return render_template(
        'sendcroprequest.html',
        loanid=data[0][0],
        data=data
    )



# @app.route('/ordercrop', methods=["POST"])
# def ordercrop():
#     print("=== ORDERCROP DEBUG ===")
#     print("Form data:", request.form)
    
#     bemail = session.get('buyersemail')
#     if not bemail:
#         return redirect(url_for('buyerlogin'))
    
#     imgfile = request.form['imgfile']
#     cropname = request.form['cropname']
#     category = request.form['category']
#     mincost = request.form['mincost']
#     quantity = request.form['quantity']
#     Order = request.form['Order']
#     season = request.form['season']
    
#     sql = "SELECT semail FROM cropprice WHERE cropname=%s AND category=%s"
#     mycursor.execute(sql, (cropname, category))
#     crop = mycursor.fetchone()
    
#     if not crop:
#         flash("Crop not found", "error")
#         return redirect(url_for('viewallcrop'))
    
#     semail = crop[0]
#     mincost = float(mincost)
#     quantity = int(quantity)
#     Order = int(Order)
    
#     sql = """SELECT discount_percentage 
#                 FROM cropprice 
#                 WHERE cropname=%s AND category=%s AND semail=%s
#                 AND discount_percentage > 0
#                 AND (offer_end_date IS NULL OR offer_end_date >= CURDATE())"""
#     mycursor.execute(sql, (cropname, category, semail))
#     offer = mycursor.fetchone()
    
#     discount_percentage = offer[0] if offer else 0
#     final_price = mincost * (1 - discount_percentage / 100)
#     discount_amount = (mincost - final_price) * Order
    
#     totalquantity = quantity - Order
#     amount = mincost * Order
#     final_amount = final_price * Order
    
#     sql = """INSERT INTO croporder
#     (cropname, category, mincost, quantity, myorder, season,
#         totalquantity, semail, bemail, amount, imgfile,
#         discount_amount, final_amount, applied_discount)
#     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    
#     values = (
#         cropname, category, mincost, quantity, Order, season,
#         totalquantity, semail, bemail, amount, imgfile,
#         discount_amount, final_amount, discount_percentage
#     )

#     mycursor.execute(sql, values)
#     mydb.commit()

#     sql = """UPDATE cropprice 
#                 SET totalquantity=%s 
#                 WHERE cropname=%s AND category=%s AND semail=%s"""
#     mycursor.execute(sql, (totalquantity, cropname, category, semail))
#     mydb.commit()
    
#     flash("Order placed successfully!", "success")
#     return redirect(url_for('viewallcrop'))


from decimal import Decimal

@app.route('/ordercrop', methods=["POST"])
def ordercrop():
    print("=== ORDERCROP DEBUG ===")
    print("Form data:", request.form)

    bemail = session.get('buyersemail')
    if not bemail:
        return redirect(url_for('buyerlogin'))

    imgfile = request.form['imgfile']
    cropname = request.form['cropname']
    category = request.form['category']
    mincost = request.form['mincost']
    quantity = request.form['quantity']
    Order = request.form['Order']
    season = request.form['season']
    
    # First query to get crop information
    sql = "SELECT semail FROM cropprice WHERE cropname=%s AND category=%s"
    mycursor.execute(sql, (cropname, category))
    crop = mycursor.fetchone()

    if not crop:
        flash("Crop not found", "error")
        return redirect(url_for('viewallcrop'))

    semail = crop[0]
    mincost = float(mincost)  # Ensure mincost is a float
    quantity = int(quantity)
    Order = int(Order)

    # Clear any unread results before the next query
    mycursor.fetchall()

    # Second query to get discount information
    sql = """SELECT discount_percentage 
                FROM cropprice 
                WHERE cropname=%s AND category=%s AND semail=%s
                AND discount_percentage > 0
                AND (offer_end_date IS NULL OR offer_end_date >= CURDATE())"""
    mycursor.execute(sql, (cropname, category, semail))
    offer = mycursor.fetchone()

    discount_percentage = offer[0] if offer else 0

    # Convert Decimal to float before using it in calculations
    discount_percentage = float(discount_percentage) 

    final_price = mincost * (1 - discount_percentage / 100)
    discount_amount = (mincost - final_price) * Order

    totalquantity = quantity - Order
    amount = mincost * Order
    final_amount = final_price * Order

    sql = """INSERT INTO croporder
    (cropname, category, mincost, quantity, myorder, season,
        totalquantity, semail, bemail, amount, imgfile,
        discount_amount, final_amount, applied_discount)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    values = (
        cropname, category, mincost, quantity, Order, season,
        totalquantity, semail, bemail, amount, imgfile,
        discount_amount, final_amount, discount_percentage
    )

    mycursor.execute(sql, values)
    mydb.commit()

    sql = """UPDATE cropprice 
                SET totalquantity=%s 
                WHERE cropname=%s AND category=%s AND semail=%s"""
    mycursor.execute(sql, (totalquantity, cropname, category, semail))
    mydb.commit()

    flash("Order placed successfully!", "success")
    return redirect(url_for('viewallcrop'))

@app.route("/cleanup_expired_offers")
def cleanup_expired_offers():
    """Clean up expired offers automatically"""
    try:
        sql = """UPDATE cropprice 
                    SET mincost = COALESCE(original_price, mincost),
                        discount_percentage = 0,
                        original_price = NULL,
                        offer_start_date = NULL,
                        offer_end_date = NULL
                    WHERE discount_percentage > 0 
                    AND offer_end_date IS NOT NULL 
                    AND offer_end_date < CURDATE()"""
        mycursor.execute(sql)
        mydb.commit()
        return "Expired offers cleaned up successfully!"
    except Exception as e:
        return f"Error cleaning up offers: {str(e)}"



@app.route("/Viewbuyerrequest")
def Viewbuyerrequest():
    sql = "select * from croporder where semail='" + session['sellersemail'] + "' and status='pending'"
    data = pd.read_sql_query(sql, mydb)
    print(data)
    return render_template('Viewbuyerrequest.html', cols=data.columns.values, rows=data.values.tolist())



@app.route("/acceptresponse/<id>", methods=["POST", "GET"])
def acceptresponse(id=0):
    print(id)
    sql = "select * from croporder where id='%s'" % (id)
    mycursor.execute(sql)
    dc = mycursor.fetchall()
    print(dc)

    amount = dc[0][10]
    cropname = dc[0][1]
    actualprice = dc[0][3]
    byuedquantity = dc[0][5]
    seller = dc[0][8]
    buyer = dc[0][9]
    print(amount, cropname, actualprice, byuedquantity, seller, buyer)
    
    sql = "update croporder set status='Accepted' where id='%s'" % (id)
    mycursor.execute(sql)
    mydb.commit()
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr_data = (
        f"Order ID: {id}\n"
        f"Amount: {amount}\n"
        f"Crop Name: {cropname}\n"
        f"Actual Price: {actualprice}\n"
        f"Purchased Quantity: {byuedquantity}\n"
        f"Seller: {seller}\n"
        f"Buyer: {buyer}\n"
        f"Status: Accepted"
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    qr_filename = f"{cropname}_paymentqr.png"
    qr_filepath = os.path.join("static/paymentqr/", qr_filename)
    os.makedirs(os.path.dirname(qr_filepath), exist_ok=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(qr_filepath)
    print(f"QR code saved at: {qr_filepath}")
    try:
        sql = "update croporder set qr_code_path='%s' where id='%s'" % (qr_filepath, id)
        print(f"Executing SQL: {sql}") 
        mycursor.execute(sql)
        mydb.commit()
    except Exception as e:
        print(f"Error updating QR code path in database: {e}")
    
    return send_file(qr_filepath, as_attachment=True, download_name=f'{cropname}_qr.png', mimetype='image/png')


@app.route("/rejectresponse/<id>", methods=["POST", "GET"])
def rejectresponse(id=0):
    print(id)
    sql = "select  * from croporder where id='%s'" % (id)
    mycursor.execute(sql)
    dc = mycursor.fetchall()
    print(dc)
    sql ="update croporder set status='Rejected' where id='%s'"%(id)
    mycursor.execute(sql)
    mydb.commit() 
    
    return redirect(url_for('Viewbuyerrequest'))

@app.route("/farmeraccepteddata")
def farmeraccepteddata():
    sql = "select * from croporder where status='Accepted' and  semail='" + session['sellersemail'] + "' and status='Accepted'"
    data = pd.read_sql_query(sql, mydb)
    print(data)
    return render_template("farmeraccepteddata.html", cols=data.columns.values, rows=data.values.tolist())


@app.route('/accepteddata')
def accepteddata():
    sql = "SELECT * FROM croporder WHERE status='Accepted' AND bemail='" + session['buyersemail'] + "'"
    data = pd.read_sql_query(sql, mydb)
    print(data)
    return render_template('accepteddata.html', cols=data.columns.values, rows=data.values.tolist())


from datetime import datetime
from logic import *

@app.route('/payment/<int:id>', methods=['POST', 'GET'])
def payment(id=0):
    print(f"Payment for order ID: {id}")
    
    # Fetch order with discount information
    sql = """SELECT *, 
             COALESCE(final_amount, amount) as payable_amount 
             FROM croporder 
             WHERE id=%s AND bemail=%s"""
    mycursor.execute(sql, (id, session['buyersemail']))
    data = mycursor.fetchall()

    if len(data) == 0:
        flash("No order found for this ID", "error")
        return redirect(url_for('accepteddata'))

    # DEBUG: Print column information to understand the structure
    print("=== ORDER DATA DEBUG ===")
    order_data = data[0]
    for i, value in enumerate(order_data):
        print(f"Index {i}: {value} (Type: {type(value)})")
    print("=========================")

    # Extract order details based on column index
    cropname = order_data[1]  # Index 1 for cropname
    amount = float(order_data[15]) if order_data[15] is not None else float(order_data[10])  # final_amount or amount
    discount_amount = float(order_data[14]) if order_data[14] is not None else 0  # discount_amount
    applied_discount = float(order_data[16]) if order_data[16] is not None else 0  # applied_discount
    original_amount = float(order_data[10])  # Original amount without discount

    if request.method == 'POST':
        bemail = session['buyersemail']
        Amount = request.form['amount']
        Cardname = request.form['cardname']
        Cardnumber = request.form['cardnumber']
        expmonth = request.form['expmonth']
        cvv = request.form['cvv']
        status = "Completed"
        semail = order_data[8]  # seller email from order
        
        # Insert payment information into database
        sql = """INSERT INTO payment(Email, Amount, Cardname, Cardnumber, expmonth, cvv, semail, status) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        val = (bemail, Amount, Cardname, Cardnumber, expmonth, cvv, semail, status)
        mycursor.execute(sql, val)
        mydb.commit()

        # Update order status to paid
        sql = "UPDATE croporder SET status='paid' WHERE id=%s"
        mycursor.execute(sql, (id,))
        mydb.commit()
        
        # Blockchain Integration: Add payment data with cropname
        blockchain = addNewData({
            'Type': 'Payment',
            'cropname': cropname,  # Added cropname to blockchain data
            'bemail': bemail,
            'Amount': Amount,
            'Cardname': Cardname,
            'Cardnumber': Cardnumber,
            'expmonth': expmonth,
            'cvv': cvv,
            'status': status,
            'semail': semail,
        })
        print('blockchain:', blockchain)

        flash("Payment successful! Thank you for your purchase.", "success")
        return redirect(url_for('accepteddata'))

    return render_template("payment.html", id=id, data=data, 
                            amount=amount, discount_amount=discount_amount, 
                            applied_discount=applied_discount, original_amount=original_amount, 
                            cropname=cropname)  # Passing cropname to the template


@app.route("/updatescan_status/<int:crop_id>", methods=["POST"])
def updatescan_status(crop_id):
    sql = "UPDATE croporder SET status='scanned' WHERE id=%s and bemail='" + session['buyersemail'] + "' "
    val = (crop_id,)
    mycursor.execute(sql, val)
    mydb.commit()
    return jsonify({"status": "success", "message": "Status updated to scanned"})



@app.route("/viewpayment")
def viewpayment():
    bmail = session['buyersemail']
    blockchain_data = retrieveData()
    list = [i for i in blockchain_data if i.get('bemail') == bmail]
    
    return render_template('viewpayment.html', rows=list)


@app.route("/viewframerpayment")
def viewframerpayment():
    sql = "SELECT id, amount, email, cardname, Cardnumber, expmonth, cvv,status FROM payment"
    data = pd.read_sql_query(sql, mydb)
    
    print(data)
    return render_template('viewframerpayment.html', cols=data.columns.values, rows=data.values.tolist())


@app.route("/submit_report/<int:order_id>", methods=["GET", "POST"])
def submit_report(order_id):
    blockchain_data = retrieveData()
    
    order = next(
        (item for item in blockchain_data
            if item.get('sumID') == order_id),
        None
    )
    
    if not order:
        return "Invalid order ID", 404
    
    cropname = order.get('cropname')
    order_amount = order.get('Amount')
    semail = order.get('semail')
    bemail = order.get('bemail')
    
    payment_data = next(
        (item for item in blockchain_data
            if item.get('Type') == 'Payment'
            and item.get('semail') == semail
            and item.get('bemail') == bemail
            and item.get('Amount') == order_amount),
        None
    )
    amount = payment_data.get('Amount') if payment_data else order_amount
    msg = None
    if request.method == "POST":
        description = request.form['description']
        report_data = {
            'Type': 'Report',
            'seller_email': semail,
            'buyer_email': bemail,
            'product_name': cropname,
            'amount_paid': amount,
            'description': description,
            'order_id': order_id,
            'status': 'pending',
            'is_blocked': 'unblock'
        }
        blockchain_response = addNewData(report_data)
        
        if blockchain_response == "Success":
            msg = "Report submitted successfully!"
        else:
            msg = f"Failed to submit report: {blockchain_response}"
            
    return render_template(
        "submit_report.html",
        seller_email=semail,
        buyer_email=bemail,
        product=cropname,
        amount=amount,
        msg=msg
    )


# @app.route('/view_reports')
# def view_reports():
#     blockchain_data = retrieveData()
#     print(blockchain_data, 'fghsdh')
    
#     reports = []
#     print(entry.get('Type'))
#     for entry in blockchain_data:
#         if entry.get('Type') == 'Report':
#             report = {
#                 'id': entry.get('order_id', None),
#                 'seller_email': entry.get('seller_email', None),
#                 'buyer_email': entry.get('buyer_email', None),
#                 'product_name': entry.get('product_name', None),
#                 'amount_paid': entry.get('amount_paid', None),
#                 'description': entry.get('description', None),
#                 'report_date': entry.get('report_date', 'Not Available'),  # Default to 'Not Available' if missing
#                 'status': entry.get('status', 'Not Available'),  # Default to 'Not Available' if missing
#                 'is_blocked': entry.get('is_blocked', 'Unknown'),  # Default to 'Unknown' if missing
#             }
#             reports.append(report)
            
#     return render_template('view_reports.html', rows=reports)

@app.route('/view_reports')
def view_reports():
    blockchain_data = retrieveData()
    print(blockchain_data, 'fghsdh')

    reports = []
    
    # Loop over blockchain_data and print 'Type' for each entry
    for entry in blockchain_data:
        print(entry.get('Type'))  # Now 'entry' is defined inside the loop
        if entry.get('Type') == 'Report':
            report = {
                'id': entry.get('order_id', None),
                'seller_email': entry.get('seller_email', None),
                'buyer_email': entry.get('buyer_email', None),
                'product_name': entry.get('product_name', None),
                'amount_paid': entry.get('amount_paid', None),
                'description': entry.get('description', None),
                'report_date': entry.get('report_date', 'Not Available'),  # Default to 'Not Available' if missing
                'status': entry.get('status', 'Not Available'),  # Default to 'Not Available' if missing
                'is_blocked': entry.get('is_blocked', 'Unknown'),  # Default to 'Unknown' if missing
            }
            reports.append(report)
            
    return render_template('view_reports.html', rows=reports)


@app.route('/mark_report_resolved/<int:report_id>', methods=['GET'])
def mark_report_resolved(report_id):
    blockchain_data = retrieveData()
    
    report = next((item for item in blockchain_data if item.get('order_id') == report_id), None)
    
    if not report:
        flash("Report not found.", "error")
        return redirect(url_for('view_reports'))
    
    report['status'] = 'resolved'
    
    blockchain_response = updateData(report['sumID'], report)
    
    if blockchain_response == "Success":
        flash("Report marked as resolved successfully!", "success")
    else:
        flash(f"Failed to update report: {blockchain_response}", "error")
        
    return redirect(url_for('view_reports'))


@app.route('/unblock_seller/<string:seller_email>', methods=['GET'])
def unblock_seller(seller_email):
    blockchain_data = retrieveData()
    
    seller = next((item for item in blockchain_data if item.get('seller_email') == seller_email), None)
    
    if not seller:
        flash("Seller not found.", "error")
        return redirect(url_for('view_reports'))
    
    seller['is_blocked'] = 'unblock'
    blockchain_response = updateData(seller['sumID'], seller)
    
    if blockchain_response == "Success":
        flash(f"Seller {seller_email} has been unblocked.", "success")
    else:
        flash(f"Failed to unblock seller: {blockchain_response}", "error")
    return redirect(url_for('view_reports'))


@app.route('/block_seller/<string:seller_email>', methods=['GET'])
def block_seller(seller_email):
    blockchain_data = retrieveData()
    print("Blockchain Data: ", blockchain_data)
    
    seller = next((item for item in blockchain_data if item.get('seller_email') == seller_email), None)
    
    if seller:
        print("Seller Found: ", seller)
    else:
        print(f"Seller with email {seller_email} not found in blockchain data.")
        
    if not seller:
        flash("Seller not found.", "error")
        return redirect(url_for('view_reports'))
    
    seller['is_blocked'] = 'blocked'
    print("Updated Seller Data: ", seller)
    
    blockchain_response = updateData(seller['sumID'], seller)
    print("Blockchain Response: ", blockchain_response)
    
    if blockchain_response == "Success":
        flash(f"Seller {seller_email} has been blocked.", "danger")
    else:
        flash(f"Failed to block seller: {blockchain_response}", "error")
        
    return redirect(url_for('view_reports'))



@app.route("/add_offer/<int:crop_id>", methods=["POST", "GET"])
def add_offer(crop_id):
    if request.method == "POST":
        discount_percentage = float(request.form['discount_percentage'])
        offer_end_date = request.form['offer_end_date']
        
        sql = "SELECT mincost FROM cropprice WHERE id=%s AND semail=%s"
        mycursor.execute(sql, (crop_id, session['sellersemail']))
        crop = mycursor.fetchone()
        
        if crop:
            original_price = float(crop[0])
            discounted_price = original_price * (1 - discount_percentage/100)
            offer_start_date = datetime.now().date()
            
            sql = """UPDATE cropprice 
                    SET discount_percentage=%s, offer_start_date=%s, offer_end_date=%s, 
                        original_price=%s, mincost=%s 
                    WHERE id=%s AND semail=%s"""
                    
            val = (discount_percentage, offer_start_date, offer_end_date, 
                    original_price, discounted_price, crop_id, session['sellersemail'])
            mycursor.execute(sql, val)
            mydb.commit()
            
            flash(f"🎉 Offer of {discount_percentage}% added successfully! Price updated from ₹{original_price} to ₹{discounted_price:.2f}", "success")
            return redirect(url_for('viewcrop'))
        else:
            flash("Crop not found!", "error")
            return redirect(url_for('viewcrop'))
    
    sql = "SELECT * FROM cropprice WHERE id=%s AND semail=%s"
    mycursor.execute(sql, (crop_id, session['sellersemail']))
    crop = mycursor.fetchone()
    
    today = datetime.now().date()
    return render_template('add_offer.html', crop_id=crop_id, crop=crop, today=today)




@app.route("/remove_offer/<int:crop_id>")
def remove_offer(crop_id):
    sql = """UPDATE cropprice 
                SET mincost = COALESCE(original_price, mincost),
                    discount_percentage = 0,
                    original_price = NULL,
                    offer_start_date = NULL,
                    offer_end_date = NULL
                WHERE id=%s AND semail=%s"""
    mycursor.execute(sql, (crop_id, session['sellersemail']))
    mydb.commit()
    
    flash("Offer removed successfully! Price restored to original.", "success")
    return redirect(url_for('viewcrop'))



@app.route("/view_offers")
def view_offers():
    sql = """SELECT *, 
                CASE 
                    WHEN discount_percentage > 0 AND (offer_end_date IS NULL OR offer_end_date >= CURDATE()) 
                    THEN 'Active' 
                    ELSE 'Inactive' 
                END as offer_status,
                original_price,
                mincost as current_price
                FROM cropprice 
                WHERE discount_percentage > 0 
                ORDER BY discount_percentage DESC"""
    data = pd.read_sql_query(sql, mydb)
    return render_template('view_offers.html', cols=data.columns.values, rows=data.values.tolist())


@app.route("/active_offers")
def active_offers():
    sql = """SELECT * FROM cropprice 
                WHERE discount_percentage > 0 
                AND (offer_start_date IS NULL OR offer_start_date <= CURDATE()) 
                AND (offer_end_date IS NULL OR offer_end_date >= CURDATE())
                ORDER BY discount_percentage DESC"""
    data = pd.read_sql_query(sql, mydb)
    return render_template('active_offers.html', cols=data.columns.values, rows=data.values.tolist())


@app.route("/manage_offers")
def manage_offers():
    sql = """SELECT *, 
                CASE 
                    WHEN discount_percentage > 0 AND offer_end_date >= CURDATE() 
                    THEN 'Active' 
                    ELSE 'Inactive' 
                END as offer_status
                FROM cropprice 
                WHERE semail=%s 
                ORDER BY discount_percentage DESC"""
    mycursor.execute(sql, (session['sellersemail'],))
    crops = mycursor.fetchall()
    
    return render_template('manage_offers.html', crops=crops)



@app.route("/debug_offers")
def debug_offers():
    """Debug route to check offer data types"""
    sql = "SELECT id, cropname, discount_percentage, offer_start_date, offer_end_date, original_price FROM cropprice WHERE semail=%s"
    mycursor.execute(sql, (session['sellersemail'],))
    offers = mycursor.fetchall()
    
    debug_info = []
    for offer in offers:
        debug_info.append({
            'id': offer[0],
            'cropname': offer[1],
            'discount_percentage': offer[2],
            'discount_type': type(offer[2]),
            'offer_start_date': offer[3],
            'start_date_type': type(offer[3]),
            'offer_end_date': offer[4],
            'end_date_type': type(offer[4]),
            'original_price': offer[5],
            'original_price_type': type(offer[5])
        })
    
    return jsonify(debug_info)




if __name__=="__main__":
    app.run(debug=True)