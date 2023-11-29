from flask import Flask, url_for, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_mail import Message, Mail
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import TimestampSigner, TimedSerializer
from flask_bcrypt import Bcrypt
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'textsummarizer'

 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "thismyfirstproject"
db = SQLAlchemy(app)
app.app_context().push()


# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Port (587 for TLS)
app.config['MAIL_USERNAME'] = 'rajakshat7985@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('SMTP')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    
    def get_token(self, expires_sec=300):
       
        serial = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return serial.dumps({'user_id': self.id})
        
    
    
    @staticmethod
    def verify_token(token):
        serial = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            user_id = serial.loads(token)['user_id']
        except Exception as e:
            return e
        return User.query.get(user_id)
        
        
        
def send_mail(user):
    token = user.get_token()
    msg = Message('Password Reset Request', recipients= [user.email], sender='rajakshat7985@gmail.com')
    print("Token", token)
    print("Receipent Mail : ", user.email)
    msg.body = f""" To reset your password. Please follow the link below.
    
    
    {url_for('reset_token', token=token, _external =True)}
    
    If you didn't send a password reset request. Please ignore this message.
    
    """
    mail.send(msg)

@app.route('/reset_request', methods = ['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            user = User.query.filter_by(email = email).first()
            if user:
                send_mail(user=user)
                flash("Reset request sent. Please Check your mail.", 'success')
                return redirect(url_for('login'))
            else:
                flash("Email not found. Please give use the right email.", 'error')
                return redirect(url_for('reset_request'))
            
    return render_template('reset_request.html')




@app.route('/reset_request/<token>')
def reset_token(token):
    user = User.verify_token(token)
    if user is None:
        flash("That is an invalid token or it has expired. Please try again.", 'warning')
        return redirect(url_for('reset_request'))
    else:
        return redirect(url_for('reset_password'))




@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if request.method == 'POST':
        pwd = request.form['password']
        re_pwd = request.form['re_password']
        print("pwd", pwd)
        print("Re_pwd", re_pwd)
        if pwd != re_pwd:
            flash("Passwords do not match. Please retype the password properly.", "danger")
            return render_template('reset_password.html')
        else:
            hashed_password = bcrypt.generate_password_hash(pwd).decode('utf-8')
            print("Saved Password : ", user.password)
            print("Input Password : ", pwd)
            user.password = hashed_password
            db.session.commit()
            flash("Password changed! Please login", "success")
            return redirect(url_for('login'))
    return render_template('reset_password.html')

