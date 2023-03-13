import os
import pathlib
import requests
from flask import  Flask,flash, request, redirect, url_for, render_template, send_from_directory,session,abort, jsonify
from werkzeug.utils import secure_filename
import replicate
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from firebase_admin import credentials, firestore, initialize_app,storage
from Functions import *
from datetime import datetime as dt

monthyear=str(dt.now())[:7]+"/"
# print(monthyear)
global Bloburl
Bloburl=""

# REPLICATE_API_TOKEN=["37facb33e6e503bbedd695face8c2d29174f98db"]
client=replicate.Client(api_token="37facb33e6e503bbedd695face8c2d29174f98db")

model = client.models.get("microsoft/bringing-old-photos-back-to-life")
version = model.versions.get("c75db81db6cbd809d93cc3b7e7a088a351a3349c9fa02b6d393e35e0d51ba799")

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = 'static/uploads/'
DOWNLOAD_FOLDER="static/download/"
filelist = [ f for f in os.listdir(UPLOAD_FOLDER)  ]
for f in filelist:
    os.remove(os.path.join(UPLOAD_FOLDER, f))
filelist = [ f for f in os.listdir(DOWNLOAD_FOLDER) ]
for f in filelist:
    os.remove(os.path.join(DOWNLOAD_FOLDER, f))

app = Flask(__name__,
            static_url_path='/static', 
            
            static_folder='static',
            template_folder='static/templates')
app.secret_key = "Repixelizor.com"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
GOOGLE_CLIENT_ID = "861117944977-e4cljnjj2l2b6kf393itjj4bkopj1ont.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred,{'storageBucket': 'repixelizor-380005.appspot.com'})
db = firestore.client()
users = db.collection('users')
bucket=storage.bucket()


flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

def login_is_required(function):
     def wrapper(*args,**kwargs):
          if "google_id" not in session:
               return abort(401)
          else:
               return function()
     return wrapper
     

@app.route("/login")
def login():
    # print("heylogin")
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    # print("heylogin")
    return redirect(authorization_url)


@app.route("/logout")
def logout():
    session.clear()
    
    return redirect("/")


@app.route("/callback")
def callback():
    print("hey")
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!
    print("hey")
    credentials = flow.credentials
    print(credentials)
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    session["picture"] = id_info.get("picture")
    print(id_info.get("picture"))
    users.document(session["google_id"]).set({"name":session["name"],"email":session["email"],"picture":session["picture"]})
    
    print(session["google_id"] ,session["name"] )
    return redirect("/home")


@app.route("/")
def index():
     return render_template("Login.html")

@app.route("/About")
def about():
     return render_template("aboutus.html")
@app.route("/Contact")
def Contact():
     return render_template("Contactus.html")

@app.route('/photos')
def photos():
    # bloburl=session["google_id"]+"/upload/"+monthyear
    # bloburl=session["google_id"]+"/upload/"+monthyear
    listblob=bucket.list_blobs( prefix=str(session["google_id"]))
    listblobs=[]
    for blob in listblob:
            # if str() in str(blob.name):
            listblobs.append(str(blob.public_url))
    
    # return listblobs
    return render_template("photos.html",blobs=listblobs)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/static/<filename>',strict_slashes=False)
def display_image(filename):
    print('display_image filename: ' + filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
    # return redirect(url_for('static', filename= "upload/" + filename), code=301)

@app.route('/process',methods=["GET","POST"],strict_slashes=False)
def process():
        uid=str(dt.now())
        print(request.form.get("colour"))
        print("yes")
        bsharpurl=os.path.join(app.config['DOWNLOAD_FOLDER'], "bshrap.jpg")
        sharpurl=os.path.join(app.config['DOWNLOAD_FOLDER'], "ssharp.jpg")
        if request.form.get("colour")=="colour":
             
             sharp_scratch(img1=filename,bsharpurl=bsharpurl,sharpurl=sharpurl)
             blob_file1=session["google_id"] + "/download/"+uid+ "bsharp.jpg"
             blob1 = bucket.blob(blob_file1)
             blob1.upload_from_filename(bsharpurl)
             blob1.make_public()
             blob_file2=session["google_id"] + "/download/"+uid+ "ssharp.jpg"
             blob2 = bucket.blob(blob_file2)
             blob2.upload_from_filename(sharpurl)
             blob2.make_public()
             print("your file url", blob1.public_url)
             return render_template('process.html', filename=filenames,filename2=blob1.public_url )
        if request.form.get("deoldify")=="deoldify":
             file=deoldify(Bloburl)
             blob_file=session["google_id"] + "/download/"+uid+ "deoldify.jpg"
             blob = bucket.blob(blob_file)
             blob.upload_from_filename(file)
             blob.make_public()
             print("your file url", blob.public_url)
             return render_template('process.html', filename=filenames,filename2=blob.public_url )
 
@app.route('/process', methods=['POST'])
def download():
    return send_from_directory(
                               session["google_id"] + "/download/"+ "deoldify.jpg", as_attachment=True)   



@app.route('/home')
@login_is_required
def home():
    # filename="../../static/uploads/Bubu_child.jpg"
    return render_template('upload.html',name=session["name"])

@app.route('/index')
def homeindex():
    # filename="../../static/uploads/Bubu_child.jpg"
    files=os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('upload.html',name=session["name"],upfiles=files)
 
@app.route('/home', methods=['POST'])
def upload_image():
    
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            global filename
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #print('upload_image filename: ' + filename)
            flash('Image successfully uploaded and displayed below')
            flash(url_for('static', filename= filename))
            
            global filenames
            filenames="uploads/" +filename
            
            blob_file=session["google_id"] + "/upload/"+monthyear+ filename
            
            blob = bucket.blob(blob_file)
            global Bloburl
            Bloburl=blob.public_url
            blob.upload_from_filename(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            blob.make_public()
            print("your file url", blob.public_url)
            # return redirect(url_for('homeindex'))
            return render_template('upload.html',name=session["name"])
        else:
            flash('Allowed image types are - png, jpg, jpeg, gif')
            return redirect(request.url)






if __name__ == "__main__":
    app.run(debug=True)
