from flask import Flask,render_template,request
from flask_mysqldb import MySQL
import os
import time
import torch
import torchaudio
import torch.nn.functional as F
from tinyec import registry
import hashlib
import binascii
from passlib.hash import pbkdf2_sha256

words=['six', 'cat', 'stop', 'house', 'dog', 'no', 'tree', 'up', 'two', 'zero', 'one', 'sheila', 'on', 'wow', 'nine', 'left', 'go', 'four', 'happy','off','bed', 'eight', 'five', 'seven', 'bird','right', 'three','yes', 'marvin', 'down']

def ECC(name,password,dob):
    #curve: "secp192r1" => y^2 = x^3 + 6277101735386680763835789423207666416083908700390324961276x + 2455155546008943817740293915197451784769108058161191238065 (mod 6277101735386680763835789423207666416083908700390324961279)
    curve = registry.get_curve('secp192r1')
    privKey=0
    #private key is sum of ascii values of username and password
    for character in name:
        privKey+=ord(character)
    for character in password:
        privKey+=ord(character)    
    #get public key by multiplying private key and generating point
    pubKey = privKey * curve.g
    #multiplying x coordinate of public key with date of birth of user
    store=pubKey.x*int(dob[:2])
    #converting into hexadecimal 
    store=hex(store)
    return store
    
    
def hash_password(password):
    hash = pbkdf2_sha256.hash(password, rounds=20000, salt_size=16)
    return hash


class SpeechRNN(torch.nn.Module):
  
  def __init__(self):
    super(SpeechRNN, self).__init__()
    
    self.rnn = torch.nn.GRU(input_size = 12,
                              hidden_size= 256, 
                              num_layers = 2, 
                              batch_first=True)
    
    self.out_layer = torch.nn.Linear(256, 30) 
    
    self.softmax = torch.nn.LogSoftmax(dim=1) 
    
  def forward(self, x): 
    
    out, _ = self.rnn(x)
    
    x = self.out_layer(out[:,-1,:]) 
    
    return self.softmax(x)


PATH="model.pth"
network=torch.load(PATH,map_location=torch.device('cpu'))
username=""

app=Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']= ''
app.config['MYSQL_DB'] = 'ecaf'
mysql = MySQL(app)

@app.route('/login',methods=['GET'])
def index():
    return render_template('index.html')


    
@app.route('/register',methods=['GET'])
def register():
    return render_template('register.html') 



@app.route('/',methods=['GET'])
def home():
	return render_template('Speech recognition.html')


@app.route('/login_status',methods=['POST'])
def predict():
    global username
    username=request.form['username']
    password=request.form['password']
    if(username=="" or password==""):
        fetchdata="PLEASE FILL ALL THE DETAILS...."
        return render_template('index.html',data=fetchdata)
    else:      
        cur = mysql.connection.cursor()
        cur.execute('SELECT dob FROM users WHERE username = % s', [username])
        t = cur.fetchone()
        if not t:
            fetchdata="INVALID DATA, PLEASE TRY AGAIN...."
            return render_template('index.html',data=fetchdata)   
            
        dob=str(t[0])  
        cur = mysql.connection.cursor()
        cur.execute('SELECT password FROM users WHERE username = % s', [username])
        account = cur.fetchone()
        cur.close()
        if account:
            password_from_db=str(account[0])
            password=ECC(username,password,dob)
            if(pbkdf2_sha256.verify(password,password_from_db)):
                capital_name=username.upper()
                fetchdata="Welcome "+capital_name
                return render_template('Speech Recognition.html',data=fetchdata)
            else:
                fetchdata="INVALID DATA, PLEASE TRY AGAIN...."
        else:   
            #fetchdata="INVALID DATA, PLEASE TRY AGAIN...."
            fetchdata=username+password+dob
    return render_template('index.html',data=fetchdata)

    
@app.route('/register_status',methods=['POST'])
def predict_status():
    username=request.form['username']
    password=request.form['password']
    cpassword=request.form['cpassword']
    dob=request.form['dob']
    if(username=="" or password=="" or cpassword=="" or dob==""):
        fetchdata="PLEASE FILL ALL THE DETAILS...."
        return render_template('register.html',data=fetchdata)
    elif(len(password)<6):
        fetchdata="PASSWORD SHOULD HAVE ATLEAST 6 CHARACTERS"
        return render_template('register.html',data=fetchdata)
    elif(password!=cpassword):
        fetchdata="PASSWORDS DO NOT MATCH, PLEASE TRY AGAIN...."
        return render_template('register.html',data=fetchdata)
    elif(dob[2]!='/' or dob[5]!='/'):
        fetchdata="Please enter date in dd/mm/yyyy format"
        return render_template('register.html',data=fetchdata)
    else:
        username=request.form['username']
        password=request.form['password']
        cpassword=request.form['cpassword']
        dob=request.form['dob']
        
        password=ECC(username,password,dob)
        password=hash_password(password)
        
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE username = % s', [username])
        account = cur.fetchone()
        if account:
            fetchdata="USER ALREADY EXISTS.."
            return render_template('register.html',data=fetchdata)
        cur.execute("""INSERT INTO users (username,password,dob) VALUES(%s,%s,%s)""",(username,password,dob))
        mysql.connection.commit()
        cur.close()
        fetchdata="REGISTERED SUCCESSFULLY...."
    return render_template('register.html',data=fetchdata)


@app.route('/',methods=['POST'])
def predict_model():
    file=request.files['file']
    #name=request.form['name']
    name=username
    audio_path="./static/audios/"+name 
    if not os.path.exists(audio_path):
        os.makedirs(audio_path)
    count = len([name for name in os.listdir(audio_path)])
    audio_path=os.path.join("./static/audios",name,file.filename)
    file.save(audio_path)
    count_files= name.upper()+" ,your total uploadings are "+str(count+1)
    waveform, sample_rate = torchaudio.load(audio_path)
    if waveform.shape[1] < 16000: 
        waveform = F.pad(input=waveform, pad=(0, 16000 - waveform.shape[1]), mode='constant', value=0)
    mfcc = torchaudio.transforms.MFCC(n_mfcc=12, log_mels=True)(waveform).squeeze(0).transpose(0,1)
    mfcc=torch.reshape(mfcc,(1,81,12))
    #net = SpeechRNN().cuda()
    with torch.no_grad():
      k=network(mfcc) #k is a tensor and not word
    #print(k)
    ans=words[torch.argmax(k)]
    #os.remove("./static/"+file.filename)
    return render_template('Speech recognition.html',transcript=ans,data=count_files,path=audio_path)


@app.route('/myfiles',methods=['GET','POST'])
def printfiles():
    name=username.upper()
    audio_path="./static/audios/"
    audio_path+=username
    files=[]
    times=[]
    for file in os.listdir(audio_path):
        file_name=audio_path+"/"+file
        files.append(file_name)
        times.append(time.ctime(os.path.getmtime(file_name)))
    count=len(files)
    return render_template('myfiles.html',data=name,count=count,files=files,times=times)

if __name__ == "__main__":
	app.run(debug=True)