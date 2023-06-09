import cv2
import os
from flask import Flask,request,render_template
from datetime import date
from datetime import datetime
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import joblib
#### Defining Flask App
app = Flask(_name_)
#### Saving Date today in 2 different formats
datetoday = date.today().strftime("%m_%d_%y")
datetoday2 = date.today().strftime("%d-%B-%Y")
#### Initializing VideoCapture object to access WebCam
face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
try:
 cap = cv2.VideoCapture(1)
except:
 cap = cv2.VideoCapture(0)
#### If these directories don't exist, create them
if not os.path.isdir('Attendance'):
 os.makedirs('Attendance')
if not os.path.isdir('static'):
 os.makedirs('static')
if not os.path.isdir('static/faces'):
 os.makedirs('static/faces')
if f'Attendance-{datetoday}.csv' not in os.listdir('Attendance'):

 with open(f'Attendance/Attendance-{datetoday}.csv','w') as f:

 f.write('Name,Roll,Time')
#### get a number of total registered users
def totalreg():
 return len(os.listdir('static/faces'))
#### extract the face from an image
def extract_faces(img):
 if img!=[]:
 gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
 face_points = face_detector.detectMultiScale(gray, 1.3, 5)
 return face_points
 else:
 return []
#### Identify face using ML model
def identify_face(facearray):
 model = joblib.load('static/face_recognition_model.pkl')
 return model.predict(facearray)
#### A function which trains the model on all the faces available in faces folder
def train_model():
 faces = []
 labels = []
 userlist = os.listdir('static/faces')
 for user in userlist:
 for imgname in os.listdir(f'static/faces/{user}'):
 img = cv2.imread(f'static/faces/{user}/{imgname}')
 resized_face = cv2.resize(img, (50, 50))
 faces.append(resized_face.ravel())
 labels.append(user)
 faces = np.array(faces)
 knn = KNeighborsClassifier(n_neighbors=5)
 knn.fit(faces,labels)
 joblib.dump(knn,'static/face_recognition_model.pkl')
27
#### Extract info from today's attendance file in attendance folder
def extract_attendance():
 df = pd.read_csv(f'Attendance/Attendance-{datetoday}.csv')
 names = df['Name']
 rolls = df['Roll']
 times = df['Time']
 l = len(df)
 return names,rolls,times,l
#### Add Attendance of a specific user
def add_attendance(name):
 username = name.split('_')[0]
 userid = name.split('_')[1]
 current_time = datetime.now().strftime("%H:%M:%S")

 df = pd.read_csv(f'Attendance/Attendance-{datetoday}.csv')
 if int(userid) not in list(df['Roll']):
 with open(f'Attendance/Attendance-{datetoday}.csv','a') as f:
 f.write(f'\n{username},{userid},{current_time}')
################## ROUTING FUNCTIONS #########################
#### Our main page
@app.route('/')
def home():
 names,rolls,times,l = extract_attendance()
 return
render_template('home.html',names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=dat
etoday2)
#### This function will run when we click on Take Attendance Button
@app.route('/start',methods=['GET'])
def start():
 if 'face_recognition_model.pkl' not in os.listdir('static'):
 return render_template('home.html',totalreg=totalreg(),datetoday2=datetoday2,mess='There is no
trained model in the static folder. Please add a new face to continue.')
 cap = cv2.VideoCapture(0)
 ret = True
 while ret:
 ret,frame = cap.read()
 if extract_faces(frame)!=():
 (x,y,w,h) = extract_faces(frame)[0]
 cv2.rectangle(frame,(x, y), (x+w, y+h), (255, 0, 20), 2)
 face = cv2.resize(frame[y:y+h,x:x+w], (50, 50))
 identified_person = identify_face(face.reshape(1,-1))[0]
 add_attendance(identified_person)
 cv2.putText(frame,f'{identified_person}',(30,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 0,
20),2,cv2.LINE_AA)
 cv2.imshow('Attendance',frame)
 if cv2.waitKey(1)==27:
 break
 cap.release()
 cv2.destroyAllWindows()
 names,rolls,times,l = extract_attendance()
 return
render_template('home.html',names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=dat
etoday2)
#### This function will run when we add a new user
@app.route('/add',methods=['GET','POST'])
def add():
 newusername = request.form['newusername']
 newuserid = request.form['newuserid']
 userimagefolder = 'static/faces/'+newusername+'_'+str(newuserid)
 if not os.path.isdir(userimagefolder):
 os.makedirs(userimagefolder)
 cap = cv2.VideoCapture(0)
 i,j = 0,0
 while 1:
 _,frame = cap.read()
 faces = extract_faces(frame)
 for (x,y,w,h) in faces:
 cv2.rectangle(frame,(x, y), (x+w, y+h), (255, 0, 20), 2)
 cv2.putText(frame,f'Images Captured: {i}/50',(30,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,
0, 20),2,cv2.LINE_AA)
 if j%10==0:
 name = newusername+'_'+str(i)+'.jpg'
 cv2.imwrite(userimagefolder+'/'+name,frame[y:y+h,x:x+w])
 i+=1
 j+=1

if j==500:
 break
 cv2.imshow('Adding new User',frame)
 if cv2.waitKey(1)==27:
 break
 cap.release()
 cv2.destroyAllWindows()
 print('Training Model')
 train_model()
 names,rolls,times,l = extract_attendance()
 return
render_template('home.html',names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=dat
etoday2)
#### Our main function which runs the Flask App
if _name_ == '_main_':
 app.run(debug=True)
<!doctype html>
<html lang="en">
<style type='text/css'>
 * {
 padding: 0;
 margin: 0;
 font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
 }
 body {
 background-image: url('https://cutewallpaper.org/21/1920-x-1080-gif/1920x1080-WallpapercartoonWallpapers-Driverlayer-Search-.gif');
 background-size: cover;
 font-family: sans-serif;
 margin-top: 40px;
 height: 100vh;
 padding: 0;
 margin: 0;
 }
 table {
30
 border: 1px;
 font-family: arial, sans-serif;
 border-collapse: collapse;
 width: 86%;
 margin: auto;
 }
 td,
 th {
 border: 1px solid black !important;
 padding: 5px;
 }
 tr:nth-child(even) {
 background-color: #dddddd;
 }
</style>
<head>
 <!-- Required meta tags -->
 <meta charset="utf-8">
 <meta name="viewport" content="width=device-width, initial-scale=1">
 <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
 <!-- Bootstrap CSS -->
 <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css"
rel="stylesheet"
 integrity="sha384-
eOJMYsd53ii+scO/bJGFsiCZc+5NDVN2yr8+0RDqr0Ql0h+rP48ckxlpbzKgwra6"
crossorigin="anonymous">
 <title>Face Recognition Based Attendance System</title>
</head>
<body>
 <div class='mt-3 text-center'>
 <h1 style="width: auto;margin: auto;color: white;padding: 11px;font-size: 44px;">Face Recognition
Based
 Attendance System</h1>
 </div>

{% if mess%}
 <p class="text-center" style="color: red;font-size: 20px;">{{ mess }}</p>
 {% endif %}
 <div class="row text-center" style="padding: 20px;margin: 20px;">
 <div class="col"
 style="border-radius: 20px;padding: 0px;background-color:rgb(211,211,211,0.5);margin:0px 10px
10px 10px;min-height: 400px;">
 <h2 style="border-radius: 20px 20px 0px 0px;background-color: #0b4c61;color: white;padding:
10px;">Today's
 Attendance <i class="material-icons">assignment</i></h2>
 <a style="text-decoration: none;max-width: 300px;" href="/start">
 <button
 style="font-size: 24px;font-weight: bold;border-radius: 10px;width:490px;padding:
10px;margin-top: 30px;margin-bottom: 30px;"
 type='submit' class='btn btn-primary'>Take Attendance <i
 class="material-icons">beenhere</i></button>
 </a>
 <table style="background-color: white;">
 <tr>
 <td><b>S No</b></td>
 <td><b>Name</b></td>
 <td><b>ID</b></td>
 <td><b>Time</b></td>
 </tr>
 {% if l %}
 {% for i in range(l) %}
 <tr>
 <td>{{ i+1 }}</td>
 <td>{{ names[i] }}</td>
 <td>{{ rolls[i] }}</td>
 <td>{{ times[i] }}</td>
 </tr>
 {% endfor %}
 {% endif %}
 </table>
 </div>
 <div class="col"
 32
style="border-radius: 20px;padding: 0px;background-color:rgb(211,211,211,0.5);margin:0px 10px 10px
10px;height: 400px;">
 <form action='/add' method="POST" enctype="multipart/form-data">
 <h2 style="border-radius: 20px 20px 0px 0px;background-color: #0b4c61;color: white;padding:
10px;">Add
 New User <i class="material-icons">control_point_duplicate</i></h2>
 <label style="font-size: 20px;"><b>Enter New User Name*</b></label>
 <br>
 <input type="text" id="newusername" name='newusername'
 style="font-size: 20px;margin-top:10px;margin-bottom:10px;" required>
 <br>
 <label style="font-size: 20px;"><b>Enter New User Id*</b></label>
 <br>
 <input type="number" id="newusereid" name='newuserid'
 style="font-size: 20px;margin-top:10px;margin-bottom:10px;" required>
 <br>
 <button style="width: 232px;margin-top: 20px;font-size: 20px;" type='submit' class='btn btndark'>Add
 New User
 </button>
 <br>
 <h5 style="padding: 25px;"><i>Total Users in Database: {{totalreg}}</i></h5>
 </form>
 </div>
 </div>
</body>
</html>
