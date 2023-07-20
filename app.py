# Store this code in 'app.py' file

from flask import Flask, render_template, request, redirect, url_for, session
import re
import csv
import cv2
import numpy as np
import pickle


app = Flask(__name__)


app.secret_key = 'your secret key'

@app.route('/')
def index():
	return render_template('index.html')
@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		account = False
		username = request.form['username']
		password = request.form['password']
		with open ('register.csv', 'r') as file:
			reader = csv.reader(file)
			j = 0
			while j == 0:
				try:
					csv_row = ' '.join(next(reader))
				except StopIteration:
					j = 1
					break
				s = csv_row.split(" ")
				mail = s[2]
				ps = s[1]
				n = s[0]
				if username==mail and password ==ps:
					account = True
					break
		if account:
			session['loggedin'] = True
			msg = 'Logged in successfully !'+n
			return render_template('vid.html', msg = msg)
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		#check
		# if account:
		# 	msg = 'Account already exists !'
		if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			row_list = [[username, password, email]]

			with open('register.csv', 'a', newline='') as file:
			    writer = csv.writer(file)
			    writer.writerows(row_list) 
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('login.html', msg = msg)

@app.route('/video')
def video():
	rectW,rectH=107,48

	cap=cv2.VideoCapture('./data/carParkingInput.mp4')

	with open('./data/parkingSlotPosition','rb') as f:
		posList=pickle.load(f)
	frame_counter = 0
	def check(imgPro):
		spaceCount=0
		for pos in posList:
			x,y=pos
			crop=imgPro[y:y+rectH,x:x+rectW]
			count=cv2.countNonZero(crop)
			if count<900:
				spaceCount+=1
				color=(0,255,0)
				thick=5
			else:
				color=(0,0,255)
				thick=2

			cv2.rectangle(img,pos,(x+rectW,y+rectH),color,thick)
		cv2.rectangle(img,(45,30),(250,75),(180,0,180),-1)
		cv2.putText(img,f'Free: {spaceCount}/{len(posList)}',(50,60),cv2.FONT_HERSHEY_SIMPLEX,0.9,(255,255,255),2)

	while True:
		_,img=cap.read()
		if frame_counter == cap.get(cv2.CAP_PROP_FRAME_COUNT):
			frame_counter = 0 #Or whatever as long as it is the same as next line
			cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0)
		gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		blur=cv2.GaussianBlur(gray,(3,3),1)
		Thre=cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,25,16)
		blur=cv2.medianBlur(Thre,5)
		kernel=np.ones((3,3),np.uint8)
		dilate=cv2.dilate(blur,kernel,iterations=1)
		check(dilate)

		cv2.imshow("Image",img)
		cv2.waitKey(10)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=500, debug=False, threaded=False)