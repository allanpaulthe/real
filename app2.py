from flask import Flask, session, redirect, url_for, escape, request, render_template,flash,send_from_directory
import sqlite3 as sql
import sys
import cgi, os
import cgitb; cgitb.enable()
from werkzeug import secure_filename
import datetime
from flask_mail import Mail, Message
app = Flask(__name__)
mail=Mail(app)


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'alanpaul472@gmail.com'
app.config['MAIL_PASSWORD'] = '********'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route('/')
def userhome():
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	cur.execute("select * from journal order by jno desc limit 3 ")
	var=cur.fetchall()
	cur.execute("select * from tips order by no desc limit 3 ")
	tips=cur.fetchall()
	if 'username' in session:
		username_session = escape(session['username']).capitalize()
		return render_template('userhome.html', session_user_name=username_session,var=var,tips=tips)
	else:
		return render_template("userhome.html",var=var,tips=tips)

@app.route("/userlogin")
def userlogin():
 	return render_template("userlogin.html")

@app.route("/go")
def go():
	if 'username' in session:
		username_session = escape(session['username']).capitalize()
		return render_template("user.html",session_user_name=username_session)
	else:
		return render_template("userhome.html",)


@app.route("/usersignup")
def usersignup():
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	cur.execute("select * from users ")
	var=cur.fetchall()
	return render_template("usersignup.html",var=var)

@app.route("/user",methods=['GET', 'POST'])
def user():
	global userid
	con = sql.connect("database.db")
	cur = con.cursor()



	error = None
	if 'username' in session:
		username_session = escape(session['username'])
		cur.execute("select category from users where username = ?", (username_session,))
		cat=cur.fetchone()[0]
		if cat == 'user':
			return redirect(url_for('userhome'))
		elif cat == 'admin':
			return render_template('adminhome.html', session_user_name=username_session)
		elif cat == 'doctor':
			return render_template('search.html', session_user_name=username_session)
		elif cat == 'expert':
			return render_template('expert.html', session_user_name=username_session)
		elif cat == 'hospital':
			return render_template('hospitalhome.html', session_user_name=username_session)
	elif request.method == 'POST':
		username_form  = request.form['username']
		password_form  = request.form['password']
		if username_form=="":
			return render_template('userlogin.html', error=error)
		else:
			try:
				cur.execute("select password from users where username = ?", (username_form,))
				password1=cur.fetchone()[0]
				if password1 == password_form:
					cur.execute("select userid from users where username = ?", (username_form,))
					userid1=cur.fetchone()[0]
					userid=str(userid1)
					session['username'] = request.form['username']
					username_session = escape(session['username']).capitalize()
					cur.execute("select category from users where userid = ?", (userid,))
					category=cur.fetchone()[0]
					if category == "user":
						return redirect(url_for('userhome'))
					elif category == "doctor":
						return render_template('search.html', session_user_name=username_session)
					elif category == "expert":
						return render_template('expert.html', session_user_name=username_session)
					elif category == "admin":
						return render_template('adminhome.html', session_user_name=username_session)
					elif category == "hospital":
						cur.execute("select * from request where hospitalid=?",(userid,))
						var=cur.fetchall()
						for x in var:
							if x[10] == "active" :
								today=datetime.datetime.now()
								subday=datetime.datetime.strptime(x[9], "%Y-%m-%d")
								diff=(today-subday).days
								if diff>10:
									cur.execute("update request set status=? where requestno=?",("expired",x[3],))
									con.commit()

						return render_template('hospitalhome.html', session_user_name=username_session)


				else:
					error = "password is not correct"
					return render_template('userlogin.html', error=error)
			except:
				error = "try to signup using other parameters!!"
				return render_template('userlogin.html', error=error)

	else:
		return render_template('userlogin.html', error=error)


@app.route('/logout')
def logout():
	global userid
	userid=0
	session.pop('username', None)
	return redirect(url_for('userhome'))

@app.route('/newuser',methods=['GET', 'POST'])
def newuser():
	con = sql.connect("database.db")
	cur = con.cursor()
	error1=None
	if request.method == 'POST':
		password1  = request.form['password1']
		password2  = request.form['password2']
		if password2==password1:
				try:


					username1  = request.form['username']
					name  = request.form['name']
					email  = request.form['email']
					phno  = request.form['phno']
					category="user"
					cur.execute("insert into users (name,username,phno,email,password,category) VALUES (?,?,?,?,?,?)",(name,username1,phno,email,password1,category,) )
					con.commit()
					return render_template('userlogin.html')

				except:

					con.rollback()
					error1="invalid cerdinals!! try again"
					return render_template('usersignup.html',error=error1)
		else:
			error1="passwords do not match"
			return render_template('usersignup.html',error=error1)





@app.route("/userdonate")
def userdonate():
	username_session = escape(session['username']).capitalize()
	return render_template("donorreg.html",session_user_name=username_session)

app.config['UPLOAD_FOLDER'] = 'static/img/'

@app.route("/edit",methods=['GET', 'POST'])
def edit():
	global userid
	upload='static/img/'
	error2=None
	con = sql.connect("database.db")
	cur = con.cursor()
	if request.method == 'POST':
		if 'username' in session:

				#try:

					fname  = request.form['first_name']
					sname  = request.form['last_name']
					email  = request.form['email']
					pphno  = request.form['primary_phone']
					ephno1  = request.form['ephone2']
					ephno2  = request.form['ephone1']
					email = request.form['email']
					dob = request.form['dob']
					blood = request.form['blood']
					sex = request.form['gender']
					house = request.form['house']
					city = request.form['city']
					pincode = request.form['pincode']
					'''file= request.files['pic']
					filename = secure_filename(file.filename)
					#The image is stored in static folder
					file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
					#renaming image file
					source=upload+filename
					destination=upload+'_'+userid+'.jpg'
					os.remove(destination)
					os.rename(source,destination)'''
					liver=kidney=heart=pancreas=lungs="no"
					liver=request.form.get('liver')
					kidney=request.form.get('kidney')
					heart=request.form.get('heart')
					pancreas=request.form.get('pancreas')
					lungs=request.form.get('lungs')
					cur.execute("update donors set  pphno=?,ephno1=?,ephno2=?,email=?,dob=?,sex=?,blood=?,house=?,city=?,pincode=?,fname=?,sname=? where userid=?",(pphno,ephno1,ephno2,email,dob,sex,blood,house,city,pincode,fname,sname,userid,) )
					cur.execute("update organs set heart=?,lungs=?,liver=?,pancreas=?,kidney=? where userid=?",(heart,lungs,liver,pancreas,kidney,userid,))
					con.commit()
					username_session = escape(session['username']).capitalize()
					return render_template('success.html', session_user_name=username_session)

				#except:

					#error2="you are not registerd"
					#con.rollback()
					#username_session = escape(session['username']).capitalize()
					#return render_template('donorreg.html', session_user_name=username_session,error=error2)

@app.route("/userdonate1")
def userdonate1():
	global userid
	error="you are not registered!!!register now"
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	username_session = escape(session['username']).capitalize()
	cur.execute("select * from donors where userid=?",(userid,) )
	if not cur.fetchone():
		return render_template('donorreg.html', session_user_name=username_session,error=error)
	else:
		cur.execute("select * from donors where userid=?",(userid,) )
		rows = cur.fetchall();
		return render_template("bad.html",rows=rows, session_user_name=username_session)




@app.route("/doctorsearch")
def doctorsearch():
	con = sql.connect("database.db")
	cur = con.cursor()
	category="doctor"
	cur.execute("select distinct locality from doctors where categoryy=?",("doctor",))
	loc=cur.fetchall()
	print (loc)
	cur.execute("select distinct hospital from doctors")
	hos=cur.fetchall()
	return render_template("doctorsearch.html" ,session_user_name = escape(session['username']).capitalize(),loc=loc,hos=hos)

@app.route("/searchbyspeciality",methods=['GET', 'POST'])
def searchbyspeciality():
	speciality=request.form.get('specialist')
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	cur.execute("select * from doctors where categoryy=? and category=?",("doctor",speciality,))
	rows=cur.fetchall()
	now=datetime.datetime.now().date()
	return render_template("book1.html",rows=rows,session_user_name = escape(session['username']).capitalize(),now=now)

@app.route("/searchbylocality",methods=['GET', 'POST'])
def searchbylocality():
	location=request.form['location']
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	cur.execute("select * from doctors where categoryy=? and locality=?",("doctor",location,))
	rows=cur.fetchall()
	now=datetime.datetime.now().date()
	return render_template("book1.html",rows=rows,session_user_name = escape(session['username']).capitalize(),now=now)

@app.route("/searchbyhospital",methods=['GET', 'POST'])
def searchbyhospital():
	hospital=request.form['hospitals']
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	cur.execute("select * from doctors where categoryy=? and hospital=?",("doctor",hospital,))
	rows=cur.fetchall()
	now=datetime.datetime.now().date()
	return render_template("book1.html",rows=rows,session_user_name = escape(session['username']).capitalize(),now=now)


@app.route("/bookover")
def bookover():
	error="Sorry booking is over for this date!!!"
	return render_template("book1.html",error=error,session_user_name = escape(session['username']).capitalize())

@app.route("/bookalready")
def bookalready():
	error="This time is already booked by someone else!!!"
	return render_template("book1.html",error=error,session_user_name = escape(session['username']).capitalize())

@app.route("/booked/<doctorid>",methods=['GET', 'POST'])
def booked(doctorid):
	flag=0
	global userid
	if request.method == 'POST':
		con = sql.connect("database.db")
		cur = con.cursor()
		date1=request.form['date']
		time1=request.form['time']
		cur.execute("select count(1) from  doctorbooked where datee=? and docid=?",(date1,doctorid,))
		count=cur.fetchone()[0]
		if count>30:

			return redirect(url_for('bookover'))

		else:
			cur.execute("select  timeeq from doctorbooked where datee=? and docid=?",(date1,doctorid,))
			info=cur.fetchall()
			for x in info:
				times=datetime.datetime.strptime(x[0],"%H:%M")
				times2=datetime.datetime.strptime(time1,"%H:%M")
				diff=(times-times2).seconds
				print (diff)
				if (diff/60) <= 10:
					flag=1

			if flag == 1:
				return redirect(url_for('bookalready'))
			else:
				cur.execute("insert into doctorbooked (docid,userid,datee,timeeq) VALUES (?,?,?,?)",(doctorid,userid,date1,time1,) )
				con.commit()
				con.close()
				return redirect(url_for('success1'))

@app.route("/success1",methods=['GET', 'POST'])
def success1():
	if 'username' in session:
		username_session = escape(session['username']).capitalize()
		return render_template("success.html",session_user_name=username_session)

@app.route("/success",methods=['GET', 'POST'])
def success():
	global userid
	error2=None
	upload='static/img/'
	con = sql.connect("database.db")
	cur = con.cursor()
	if request.method == 'POST':
		if 'username' in session:

				#try:
					fname  = request.form['fname']
					sname  = request.form['sname']
					email  = request.form['email']
					pphno  = request.form['primary_phone']
					ephno1  = request.form['ephone2']
					ephno2  = request.form['ephone1']
					email = request.form['email']
					dob = request.form['dob']
					blood = request.form['blood']
					sex = request.form['gender']
					house = request.form['house']
					city = request.form['city']
					pincode = request.form['pincode']
					file= request.files['filename']
					filename = secure_filename(file.filename)
					#The image is stored in static folder
					file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
					#renaming image file
					source=upload+filename
					destination=upload+userid+'.jpg'
					os.rename(source,destination)
					liver=kidney=heart=pancreas=lungs="no"
					liver=request.form.get('liver')
					kidney=request.form.get('kidney')
					heart=request.form.get('heart')
					pancreas=request.form.get('pancreas')
					#alll=request.form['all']
					lungs=request.form.get('lungs')
					cur.execute("insert into donors (userid,pphno,ephno1,ephno2,email,dob,sex,blood,donorpic,house,city,pincode,fname,sname,status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(userid,pphno,ephno1,ephno2,email,dob,sex,blood,userid+'.jpg',house,city,pincode,fname,sname,"active",))
					con.commit()
					con.close()
					con = sql.connect("database.db")
					cur = con.cursor()
					cur.execute("insert into organs (heart,lungs,liver,pancreas,kidney,userid) VALUES (?,?,?,?,?,?)",(heart,lungs,liver,pancreas,kidney,userid,))
					con.commit()
					username_session = escape(session['username']).capitalize()
					return render_template("success.html",session_user_name=username_session)

				#except:

					#error2="data already exist"
					#con.rollback()
					#username_session = escape(session['username']).capitalize()
					#return render_template('donorreg.html', session_user_name=username_session,error=error2)

@app.route("/ask")
def ask():
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	category="expert"
	cur.execute("select * from doctors where categoryy=?",(category,))
	var=cur.fetchall()
	cur.execute("select * from users where category=?",(category,))
	rows=cur.fetchall()
	info = zip(var, rows)
	username_session = escape(session['username']).capitalize()
	return render_template("ask.html",info=info,session_user_name=username_session)

@app.route("/<expertid>/ask",methods=['GET', 'POST'])
def postques(expertid):
	global userid
	con = sql.connect("database.db")
	cur = con.cursor()
	ques=request.form['question']
	ans="empty"
	cur.execute("insert into question (expertid,userid,question,answers) VALUES (?,?,?,?)",(expertid,userid,ques,ans,))
	con.commit()
	return redirect(url_for('success1'))

@app.route("/reply")
def reply():
	global userid
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	cur.execute("select * from question where userid=?",(userid,))
	ans=cur.fetchall()
	count=0
	return render_template("reply.html",ans=ans,session_user_name= escape(session['username']).capitalize(),count=count)



@app.route("/contact")
def contact():
 	return render_template("contact.html")


@app.route('/enter',methods=['GET', 'POST'])
def table23():
	con = sql.connect("database.db")
	con.row_factory=sql.Row
	cur = con.cursor()
	if request.method == 'POST':
		nm=request.form['name']
		cur.execute("select * from donors where fname like ?  and status=?",('%'+nm+'%',"active",))
		rows=cur.fetchall()
		return render_template('tablee.html',rows=rows)


@app.route("/removedonor/<usid>",methods=['GET', 'POST'])
def removedonor(usid):
	con = sql.connect("database.db")
	cur = con.cursor()
	cur.execute("select * from donors where userid=?",(usid,))
	var=cur.fetchone()
	#cur.execute("delete from donors where userid=?",(usid,))
	con.commit()
	heart=kidney=liver=pancreas=lungs="no"
	heart=request.form.get('heart')
	kidney=request.form.get('kidney')
	liver=request.form.get('liver')
	pancreas=request.form.get('pancreas')
	lungs=request.form.get('lungs')
	blood=var[6]
	nos=1
	if heart=="yes":
		cur.execute("select * from request where blood=? and organ=? and status=?",(blood,"heart","active",))
		var=cur.fetchall()
		cur.execute("select heart from avai where nos=?",( nos,))
		heart=cur.fetchone()[0]
		heart=heart+1
		cur.execute("update avai set heart=?  where nos=?",( heart,nos,))
		con.commit()
		for x in var:
			msg = Message('Ayush.co notification', sender = 'alanpaul472@gmail.com', recipients = [x[7]])
			cur.execute("select * from users where userid=?",( x[0],))
			k=cur.fetchone()
			cur.execute("update avai set heart=heart+1  where nos=?",(nos,))
			#msg.body = "a match for your request no %s is avialable at %s contact them %s" %(x[3],k[4],k[5])
			msg.html=render_template('email.html',requestno=x[3],hospital=x[0],donor=usid,hosname=k[4],contact=k[5])
			mail.send(msg)

	if kidney=="yes":
		cur.execute("select * from request where blood=? and organ=? and status=?",(blood,"kidney","active",))
		var=cur.fetchall()
		cur.execute("select kidney from avai where nos=?",( nos,))
		heart=cur.fetchone()[0]
		heart+=1
		print (heart)
		cur.execute("update avai set kidney=?  where nos=?",( heart,nos,))
		con.commit()
		for x in var:
			msg = Message('Ayush.co notification', sender = 'alanpaul472@gmail.com', recipients = [x[7]])
			cur.execute("select * from users where userid=?",( x[0],))
			k=cur.fetchone()
			cur.execute("update avai set kidney=kidney+1  where nos=?",(nos,))
			#msg.body = "a match for your request no %s is avialable at %s contact them %s" %(x[3],k[4],k[5])
			msg.html=render_template('email.html',requestno=x[3],hospital=x[0],donor=usid,hosname=k[4],contact=k[5])
			mail.send(msg)

	if liver=="yes":
		cur.execute("select * from request where blood=? and organ=? and status=?",(blood,"liver","active",))
		var=cur.fetchall()
		cur.execute("select liver from avai where nos=?",( nos,))
		heart=cur.fetchone()[0]
		heart+=1
		cur.execute("update avai set liver=?  where nos=?",( heart,nos,))
		con.commit()
		for x in var:
			msg = Message('Ayush.co notification', sender = 'alanpaul472@gmail.com', recipients = [x[7]])
			cur.execute("select * from users where userid=?",( x[0],))
			k=cur.fetchone()
			cur.execute("update avai set liver=liver+1  where nos=?",(nos,))
			#msg.body = "a match for your request no %s is avialable at %s contact them %s" %(x[3],k[4],k[5])
			msg.html=render_template('email.html',requestno=x[3],hospital=x[0],donor=usid,hosname=k[4],contact=k[5])
			mail.send(msg)

	if pancreas=="yes":
		cur.execute("select * from request where blood=? and organ=? and status=?",(blood,"pancreas","active",))
		var=cur.fetchall()
		cur.execute("select pancreas from avai where nos=?",( nos,))
		heart=cur.fetchone()[0]
		heart+=1
		cur.execute("update avai set pancreas=?  where nos=?",( heart,nos,))
		con.commit()
		for x in var:
			msg = Message('Ayush.co notification', sender = 'alanpaul472@gmail.com', recipients = [x[7]])
			cur.execute("select * from users where userid=?",( x[0],))
			k=cur.fetchone()
			cur.execute("update avai set pancreas=pancreas+1  where nos=?",(nos,))
			#msg.body = "a match for your request no %s is avialable at %s contact them %s" %(x[3],k[4],k[5])
			msg.html=render_template('email.html',requestno=x[3],hospital=x[0],donor=usid,hosname=k[4],contact=k[5])
			mail.send(msg)

	if lungs=="yes":
		cur.execute("select * from request where blood=? and organ=? and status=?",(blood,"lungs","active",))
		var=cur.fetchall()
		cur.execute("select lungs from avai where nos=?",( nos,))
		heart=cur.fetchone()[0]
		heart+=1
		cur.execute("update avai set lungs=?  where nos=?",( heart,nos,))
		con.commit()
		for x in var:
			msg = Message('Ayush.co notification', sender = 'alanpaul472@gmail.com', recipients = [x[7]])
			cur.execute("select * from users where userid=?",( x[0],))
			k=cur.fetchone()
			cur.execute("update avai set lungs=lungs+1  where nos=?",(nos,))
			#msg.body = "a match for your request no %s is avialable at %s contact them %s" %(x[3],k[4],k[5])
			msg.html=render_template('email.html',requestno=x[3],hospital=x[0],donor=usid,hosname=k[4],contact=k[5])
			mail.send(msg)

	cur.execute("insert into notifications(donorid,requestno) values(?,?) ",( usid,"000"))
	con.commit()

	return redirect(url_for('notification'))


@app.route("/experthome")
def experthome():
	global userid
	con = sql.connect("database.db")
	cur = con.cursor()
	cur.execute("select name from users where userid=? ",(userid,))	
	name=cur.fetchone()[0]
	print (name)
	return render_template("expert.html",name=name)

@app.route("/doctorhome")
def doctorhome():
 	return render_template("search.html")

@app.route("/accept/<reqno>/<hosname>/<donorid>")
def accept(reqno,hosname,donorid):
	con = sql.connect("database.db")
	con.row_factory=sql.Row
	cur = con.cursor()
	cur.execute("select requestno from notifications where donorid=? ",( donorid,))
	if cur.fetchone()[0] == 000 :
		cur.execute("update  notifications set requestno=? ",( reqno,))
		cur.execute("update request set status=? where requestno=?",("expired",reqno,))
		cur.execute("update donors set status=? where userid=?",("expired",donorid,))
		cur.execute("select organ from request where requestno=?",(reqno,))
		organ=cur.fetchone()[0]
		nos=1
		if organ=="heart":
			cur.execute("update avai set heart=heart-1  where nos=?",(nos,))
		if organ=="kidney":
			cur.execute("update avai set kidney=kidney-1  where nos=?",(nos,))
		if organ=="pancreas":
			cur.execute("update avai set pancreas=pancreas-1  where nos=?",(nos,))
		if organ=="liver":
			cur.execute("update avai set liver=liver-1  where nos=?",(nos,))
		if organ=="lungs":
			cur.execute("update avai set lungs=lungs-1  where nos=?",(nos,))
		print(hosname)
		cur.execute("select email from users where userid=?",(hosname,))
		email=cur.fetchone()[0]
		print(email)
		cur.execute("select hospitalid from request where requestno=?",(reqno,))
		hos=cur.fetchone()[0]
		cur.execute("select name from users where userid=?",(hos,))
		hosname=cur.fetchone()[0]
		cur.execute("select name from users where userid=?",(donorid,))
		donorname=cur.fetchone()[0]
		msg = Message('Ayush.co notification', sender = 'alanpaul472@gmail.com', recipients = [email])
		msg.html=render_template('hosnot.html',hosname=hosname,donorname=donorname,reqno=reqno)
		mail.send(msg)
		con.commit()

		return redirect(url_for('acception'))

	else:
		return redirect(url_for('rejection'))



@app.route("/accept")
def acception():
 	return render_template("acception.html")

@app.route("/forgot")
def forgot():
	con = sql.connect("database.db")
	con.row_factory=sql.Row
	cur = con.cursor()
	cur.execute("select * from users")
	emails=cur.fetchall()
	return render_template("forgot-password.html",var=emails)


@app.route("/recover",methods = ['POST', 'GET'])
def recover():
	email=request.form['email']
	con = sql.connect("database.db")
	cur = con.cursor()
	cur.execute("select password from users where email=?",(email,))
	password=cur.fetchone()[0]
	msg = Message('Ayush.co notification', sender = 'alanpaul472@gmail.com', recipients = [email])	
	msg.html=render_template("recovery.html",email=email,password=password)
	mail.send(msg)
	return redirect(url_for('userhome'))

@app.route("/reject")
def rejection():
 	return render_template("rejection.html")

@app.route("/blog")
def blog():
 	return render_template("blog.html")

@app.route("/about")
def about():
 	return render_template("about.html")


@app.route("/index")
def hello11():
    return render_template("index.html")

@app.route("/blog")
def hello2():
    return render_template("blog.html")

@app.route("/login")
def hello3():
    return render_template("login.html")

@app.route('/registerpatient',methods = ['POST', 'GET'])
def addrec():
   	msg=None
   	upload='static/img/'
   	global userid
   	nm = request.form['name']
   	addr = request.form['ADDRESS']
   	city = request.form['CITY']
   	pin = request.form['PIN']
   	mail = request.form['EMAIL']
   	datee = datetime.date.today()
   	bldgrp = request.form['blood']
   	gender = request.form['gender']
   	organ = request.form['organ']
   	with sql.connect("database.db") as con:
   		cur = con.cursor()
   		cur.execute("select name from users where userid=?",(userid,))
   		hosname=cur.fetchone()
   		cur.execute("INSERT INTO request (hospitalid,name,house,city,pin,email,subdate,blood,gender,organ,status,hosname) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(userid,nm,addr,city,pin,mail,datee,bldgrp,gender,organ,"active",hosname[0]),)
   		#cur.execute("INSERT INTO organ (patientid,patient,heart,liver,kidney,pancreas) VALUES (?,?,?,?,?,?)",(nm,addr,city,pin) )
   		con.commit()
   		cur.execute("SELECT requestno FROM request WHERE email=? and organ=?",(mail,organ,))
   		requestno=cur.fetchone()[0]
   		requestno=str(requestno)
   		file= request.files['filename']
   		filename = secure_filename(file.filename)
   		#The image is stored in static folder
   		file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
   		#r7aming image file
   		source=upload+filename
   		destination=upload+'patient'+(requestno)+'.jpg'
   		os.rename(source,destination)	
   		cur.execute("update request set patientpic=? where requestno=?",('patient'+requestno+'.jpg',requestno,))
   		con.commit
   		msg = "Record successfully added"
   		return render_template('registersuccses.html',uid=requestno) 
      #except:
         
         #return render_template("login.html")
@app.route("/hospitalhome")
def hello5():
    return render_template("hospitalhome.html")

@app.route("/searchuser")
def hello6():
    return render_template("searchuser.html")

@app.route("/profile")
def hello7():
    return render_template("profile.html")

@app.route("/match")
def hello8():
    return render_template("match.html")

@app.route("/noti")
def hello9():
    return render_template("noti.html")

@app.route("/card")
def hello10():
	con = sql.connect("database.db")
	con.row_factory=sql.Row
	cur = con.cursor()
	nos=1
	cur.execute("select * from avai where nos=?",(nos,))
	var=cur.fetchone()
	return render_template("card.html",var=var)


@app.route('/reg')
def reg():
   return render_template('transreg.html')


@app.route("/regtransaction",methods=['GET', 'POST'])
def regtransaction():
	global userid
	error2=None
	con = sql.connect("database.db")
	cur = con.cursor()
	if request.method == 'POST':
		if 'username' in session:
				
				try:	
			
					fromhos  = request.form['first_name']
					tohos  = request.form['last_name']
					pname  = request.form['patient_name']
					gender  = request.form['gender']
					hname  = request.form['house']
					city  = request.form['city']
					pincode = request.form['pincode']
					donorname = request.form['donor_name']
					gender1 = request.form['gender1']
					house1 = request.form['house1']
					city1 = request.form['city1']
					pincode1 = request.form['pincode1']
					blood= request.form['blood']
					date= request.form['dob']
					organ= request.form['organ']
					cur.execute("insert into trans (first_name,last_name,patient_name,gender,house,city,pincode,donor_name,gender1,house1,city1,pincode1,blood,dob,organ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(fromhos,tohos,pname,gender,hname,city,pincode,donorname,gender1,house1,city1,pincode1,blood,date,organ,) )
					con.commit()
					username_session = escape(session['username']).capitalize()
					

				except:

					error2="data already exist"
					con.rollback()
					username_session = escape(session['username']).capitalize()
					return render_template('transactionreg.html', session_user_name=username_session,error=error2)
		return render_template("hospitalhome.html") 

@app.route('/add')
def add():
	return render_template('add.html')

@app.route('/removerequest/<reqid>')
def removerequest(reqid):
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	cur.execute("delete from request where requestno=?",(reqid,))
	con.commit()
	return redirect(url_for('hello5'))

@app.route('/renewrequest/<reqid>')
def renewrequest(reqid):
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	ss = datetime.date.today()
	cur.execute("update request set subdate=? where requestno=?",(ss,reqid,))
	con.commit()
	return redirect(url_for('hello5'))

@app.route('/addorremove',methods=['GET','POST'])
def addorremove():
	global userid
	if request.method=='POST':
		name = request.form['name']
		con = sql.connect("database.db")
		con.row_factory = sql.Row
		cur = con.cursor()
		cur.execute("select * from request where name=? and hospitalid=? and status=?",(name,userid,"active",))
		var=cur.fetchall()
		return render_template('addorremove.html',var=var)

@app.route('/table',methods=['GET', 'POST'])
def table():
	global userid
	if request.method=='POST':
		ids = request.form['id']
		con = sql.connect("database.db")
		con.row_factory = sql.Row
		cur = con.cursor()
		cur.execute("select * from request where requestno=? and status=?",(ids,"active",))
		var=cur.fetchall()
		return render_template('table1.html',var=var)

@app.route('/searchbyblood',methods=['GET', 'POST'])
def searchbyblood():
	if request.method=='POST':
		blood = request.form.get('blood')
		con = sql.connect("database.db")
		con.row_factory = sql.Row
		cur = con.cursor()
		cur.execute("select * from request where blood=? and status=?",(blood,"active",))
		var=cur.fetchall()
		return render_template('table1.html',var=var)


@app.route('/searchbyorgan',methods=['GET', 'POST'])
def searchbyorgan():
	if request.method=='POST':
		organ = request.form.get('organ')
		con = sql.connect("database.db")
		con.row_factory = sql.Row
		cur = con.cursor()
		cur.execute("select * from request where organ=? and status =?",(organ,"active",))
		var=cur.fetchall()
		return render_template('table1.html',var=var)


@app.route('/searchpatient',methods=['GET', 'POST'])
def searchpatient():
	global userid
	if request.method=='POST':
		name = request.form.get('name')
		con = sql.connect("database.db")
		con.row_factory = sql.Row
		cur = con.cursor()
		cur.execute("select * from request where name=? and hospitalid=?",(name,userid,))
		var=cur.fetchall()
		return render_template('donorprofile.html',var=var)

@app.route('/searchunique',methods=['GET', 'POST'])
def searchunique():
	global userid
	if request.method=='POST':
		uid = request.form.get('uid')
		con = sql.connect("database.db")
		con.row_factory = sql.Row
		cur = con.cursor()
		cur.execute("select * from request where requestno=? and hospitalid=?",(uid,userid,))
		var=cur.fetchall()
		return render_template('donorprofile.html',var=var)



@app.route('/userprofile/<usid>')
def userprofile(usid):
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	cur.execute("select * from users where userid=?",(usid,))
	var=cur.fetchall()	
	return render_template('userprofile.html',var=var)


@app.route('/table2')
def table2():
   return render_template('table2.html')

@app.route('/doctorbydate',methods=['POST'])
def doctorbydate():
	global userid
	datee=request.form['date']
	con = sql.connect("database.db")
	cur = con.cursor()
	cur.execute("select * from doctorbooked where datee=? and docid=?",(datee,userid,))
	var=cur.fetchall()
	count=0
	return render_template('viewbydoc.html',var=var,count=count,date=datee)

@app.route('/book')
def book():
   return render_template('book.html')

@app.route('/readtip/<tipno>')
def readtip(tipno):
	con = sql.connect("database.db")
	cur = con.cursor()
	cur.execute("select * from tips where no=?",(tipno,))
	var=cur.fetchone()[0]
	return render_template('viewtips.html',var=var)

@app.route('/search')
def search():
   return render_template('search.html')

@app.route('/donor')
def donor():
   return render_template('donor.html')

@app.route('/view')
def view():
   return render_template('view.html')

@app.route('/chakka')
def chakka():
   return render_template('chakka.html')

@app.route("/expert")
def expert():
    return render_template("expert.html")


@app.route("/tip")
def tip():
    return render_template("tip.html")

@app.route("/dout")
def dout():
		global userid;
		count=0
		con = sql.connect("database.db")
		con.row_factory = sql.Row
		cur = con.cursor()
		ans="empty"
		cur.execute("select * from question where  answers=? and expertid=?",(ans,userid,) )
		var=cur.fetchall()
		return render_template('viewdout.html',var=var,count=count)

@app.route("/answer/<quesid>",methods=['GET', 'POST'])
def answer(quesid):
	con = sql.connect("database.db")
	cur = con.cursor()
	ans=request.form['answer']
	cur.execute("update question set answers=? where questionid=?", (ans,quesid,) )
	con.commit()
	return redirect(url_for('expert'))





@app.route("/doubt")
def doubt():
    count=1
    return render_template("doubt.html",count=count)

@app.route('/admin')
def admin():
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	cur.execute("select * from users ")
	var=cur.fetchall()
	return render_template("admin.html",var=var)

@app.route("/addadmin",methods=['GET', 'POST'])
def addadmin():
	if request.method == 'POST':
		con = sql.connect("database.db")
		cur = con.cursor()
		nam=request.form['name']
		userid=request.form['username']
		pswd=request.form['password']
		email=request.form['email']
		phone=request.form['phone']
		category="admin"
		cur.execute("insert into users (username,password,name,email,phno,category) VALUES (?,?,?,?,?,?)",(userid,pswd,nam,email,phone,category) )
		con.commit()
		con.close()
		return render_template("adminhome.html",var="admin")

@app.route("/adddoctor",methods=['GET', 'POST'])
def adddoc():
	upload='static/img/'
	if request.method == 'POST':
		con = sql.connect("database.db")
		cur = con.cursor()
		name=request.form['name']
		username=request.form['username']
		pswd=request.form['password']
		email=request.form['email']
		locality=request.form['locality']
		phone=request.form['phone']
		speciality=request.form['speciality']
		hospital=request.form['hospital']
		file= request.files['filename']
		filename = secure_filename(file.filename)
		#The image is stored in static folder
		file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
		#renaming image file
		source=upload+filename
		destination=upload+username+'.jpg'
		os.rename(source,destination)
		category="doctor"
		cur.execute("insert into users (username,password,name,email,phno,category) VALUES (?,?,?,?,?,?)",(username,pswd,name,email,phone,category,) )
		con.commit()
		cur.execute("select userid from users where username=?",(username,))
		userid3=cur.fetchone()[0]
		cur.execute("insert into doctors (userid,hospital,category,locality,categoryy,pic,name) VALUES (?,?,?,?,?,?,?)",(userid3,hospital,speciality,locality,category,username+'.jpg',name,) )
		con.commit()
		con.close()
		return render_template("adminhome.html",var="doctor")

@app.route("/addexpert",methods=['GET', 'POST'])
def addex():
	upload='static/img/'
	if request.method == 'POST':
		con = sql.connect("database.db")
		cur = con.cursor()
		name=request.form['name']
		username=request.form['username']
		pswd=request.form['password']
		email=request.form['email']
		locality=request.form['locality']
		phone=request.form['phone']
		hospital=request.form['hospital']
		speciality=request.form['speciality']
		file= request.files['filename']
		filename = secure_filename(file.filename)
		#The image is stored in static folder
		file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
		#renaming image file
		source=upload+filename
		destination=upload+username+'.jpg'
		os.rename(source,destination)
		category="expert"
		cur.execute("insert into users (username,password,name,email,phno,category) VALUES (?,?,?,?,?,?)",(username,pswd,name,email,phone,category,) )
		con.commit()
		cur.execute("select userid from users where username=?",(username,))
		userid3=cur.fetchone()[0]
		cur.execute("insert into doctors (userid,hospital,locality,categoryy,pic,name,category) VALUES (?,?,?,?,?,?,?)",(userid3,hospital,locality,category,username+'.jpg',name,speciality,) )
		con.commit()
		con.close()
		return render_template("adminhome.html",var="expert")		

@app.route("/addhospital",methods=['GET', 'POST'])
def addhosp():
	upload='static/img/'
	if request.method == 'POST':
		con = sql.connect("database.db")
		cur = con.cursor()
		name=request.form['name']
		username=request.form['username']
		pswd=request.form['password']
		email=request.form['email']
		phone=request.form['phone']
		category="hospital"
		cur.execute("insert into users (username,password,name,email,phno,category) VALUES (?,?,?,?,?,?)",(username,pswd,name,email,phone,category,) )
		con.commit()
		con.close()
		return render_template("adminhome.html",var="hospital")

@app.route('/doctor')
def doctor():
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	cur.execute("select * from users ")
	var=cur.fetchall()
	return render_template("doctor.html",var=var)


@app.route('/viewjournal/<jno>')
def viewjornal(jno):
	con = sql.connect("database.db")
	cur = con.cursor()
	con.row_factory = sql.Row
	cur.execute("select * from journal where jno=?",(jno,))
	var=cur.fetchall()	
	return render_template("viewjournal.html",var=var)

@app.route('/expert1')
def expert1():
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	cur.execute("select * from users ")
	var=cur.fetchall()
	return render_template("expert1.html",var=var)

@app.route('/hospital')
def hospital():
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	cur.execute("select * from users ")
	var=cur.fetchall()
	return render_template("hospital.html",var=var)

@app.route("/hospital1")
def notification():
 	return render_template("hospitalhome.html",aa="aa")

@app.route('/search1')
def search1():
   return render_template("search1.html")

@app.route('/transaction')
def transaction():
	con=sql.connect("database.db")
	cur = con.cursor()
	cur.execute("select * from trans ")
	var=cur.fetchall()
	print(var)
	return render_template("transaction.html",var=var)

@app.route('/adminsearchuser')
def searchuser():
	return render_template("usersearch.html")

@app.route('/removeuser',methods=['GET','POST'])
def removeuser():
	name=request.form['name']
	con=sql.connect("database.db")
	cur = con.cursor()
	cur.execute("select * from users where name like ? ",('%'+name+'%',))
	var=cur.fetchall()
	return render_template("userlist.html",var=var)

@app.route('/removeuser2/<usid>')
def removeuser2(usid):
	con=sql.connect("database.db")
	cur = con.cursor()
	cur.execute(" delete from users where userid=?",(usid,))
	cur.execute(" delete from doctors where userid=?",(usid,))
	cur.execute(" delete from  request where hospitalid=?",(usid,))
	cur.execute(" delete from question where userid=?",(usid,))
	cur.execute(" delete from donors where userid=?",(usid,))
	cur.execute(" delete from doctorbooked where userid=?",(usid,))
	cur.execute(" delete from organs where userid=?",(usid,))
	con.commit()
	return redirect(url_for('transaction3'))


@app.route('/adminhome')
def transaction3():
   return render_template("adminhome.html")

@app.route('/journalpage')
def journalpage():
   return render_template("postjournal.html")


@app.route('/readmore')
def readmore():
	con=sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()	
	cur.execute("select * from journal")
	var=cur.fetchall()
	return render_template("readmore.html",var=var)

@app.route('/addtip',methods=['GET', 'POST'])
def addtip():
	con=sql.connect("database.db")
	cur = con.cursor()
	content = request.form['content']
	cur.execute("insert into tips(content) values(?) ",(content,))
	con.commit()
	return render_template("expert.html")

app.config['UPLOAD_FOLDER'] = 'static/img/'

@app.route('/postjournal',methods=['GET', 'POST'])
def postjournal():
	msg=None
	upload='static/img/'
	con=sql.connect("database.db")
	cur = con.cursor()
	if request.method == 'POST':
		#try:
			heading = request.form['heading']
			content = request.form['content']
			file= request.files['filename']
			filename = secure_filename(file.filename)
			#The image is stored in static folder
			file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			#renaming image file
			source=upload+filename
			destination=upload+heading+'.jpg'
			os.rename(source,destination)
			now = datetime.date.today()
			cur.execute("INSERT INTO journal (heading,content,expertid,pic,datee) VALUES (?,?,?,?,?)",(heading,content,userid,heading+'.jpg',now) )
			con.commit()
			return render_template("expert.html")
		#except:
			#return render_template("postjournal.html")


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


if __name__ == '__main__':
	global userid
	app.run(debug = True)
