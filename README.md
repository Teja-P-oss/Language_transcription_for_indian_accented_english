# Language_transcription_for_indian_accented_english
This is a full stack web based application that prints the transcription for indian accented english. We take the help of model.pth file which contains the pretrained model for speech recognition The technologies used for this are Python, HTML, CSS, Flask, MySQL, Elliptic curve cryptography

steps to run this application:-

prerequisites: anaconda, pytorch, flask,flask_mysqldb,tinyec, hashlib,binascii,passlib.hash, xampp. 
install all the above packages 

after installing,
step-1: open xampp and start apache, Mysql server

step-2: create a database with name 'ecaf'

step-3: create a table 'users' with attributes 'username' (VARCHAR with size 200), 'password' (VARCHAR with size 200) , dob (VARCHAR with size 200)

step-4: open anaconda prompt and go to the project directory

step-5: enter python server.py.

step-6: Now open web browser and enter 127.0.0.1:5000/login. This will redirect to the login page. User needs to be registered before logging in .

![image](https://user-images.githubusercontent.com/57107143/137547293-167c98d4-7eb0-4326-acde-786f56ffea60.png)


step-7: Once the user is logged he can use the benefit of this application. Here is the picture of stored password which is encrypted using elliptic curve cryptography

![image](https://user-images.githubusercontent.com/57107143/137548413-21ed43a1-2b54-421c-999d-2e9eff20866f.png)

step-8: after logging in, user will be redirected to the home page where he can upload a wav file and get the transcripts for the uploaded file

![Speech-Recognizer](https://user-images.githubusercontent.com/57107143/137547554-49717b40-a800-4b91-8dfb-058de60844ed.png)

step-9: once if you click Myfiles option, we can see the history of previous uploadings of the user

![image](https://user-images.githubusercontent.com/57107143/137547736-1248b8ef-6306-4f4d-bb8e-b98cf002120c.png)

