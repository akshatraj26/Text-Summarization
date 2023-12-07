from flask import Flask, url_for, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_mail import Message, Mail
from datetime import datetime
import spacy
from string import punctuation
from heapq import nlargest
from spacy.lang.en.stop_words import STOP_WORDS
import re
import random
import os
from itsdangerous import URLSafeTimedSerializer
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import pytz

app = Flask(__name__)

 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "thismyfirstproject"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    __tablename__ = "client_update"
    
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    indian_time = pytz.timezone('Asia/Kolkata')
    date_created = db.Column(db.DateTime, default = datetime.now(indian_time))
    
    
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
        
    
    
    def __repr__(self):
        return f"User: {self.name} - {self.email}"
    
  
class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.Text(), nullable=False)
    summary_text = db.Column(db.Text(), nullable=False)
    indian_time = pytz.timezone('Asia/Kolkata')
    date_created = db.Column(db.DateTime, default = datetime.now(indian_time))
    
    
    def __repr__(self):
        return f"User: {self.user_input} - {self.summary_text}"
    
class UserQuery(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    fname = db.Column(db.String(80), nullable = False)
    message = db.Column(db.Text, nullable =False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    subject = db.Column(db.String(100), nullable=False)
    indian_time = pytz.timezone('Asia/Kolkata')
    date = db.Column(db.DateTime, default = datetime.now(indian_time))
      
    
    
    def __repr_(self):
        return f"UserQuery: {self.fname} - {self.message}"
  
  
  
  

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/index')
def index():
    if 'logged_in' in session and session['logged_in']:
        flash("Login succesfully", 'success')
        
    return render_template('index.html')


@app.route('/contact')
def contact():
    return render_template('contacts.html')

@app.route('/signup')
def signup():
    
    return render_template('register.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signin')
def signin():
    return render_template('login.html')

       
"""
Create your account and get registered.

"""           



@app.route('/Register', methods = ['GET', 'POST'])
def Register():
    if request.method == "POST":
        name = request.form['name']
        uname = request.form['uname']
        email = request.form['email']
        pwd = request.form['password']
        re_pwd = request.form['re_password']
        
        if pwd != re_pwd:
            flash("Passwords do not match. Please type the same password in both field.", "danger")
            return redirect(url_for('signup'))
        # print(name, uname, email, pwd)
        
        existing_user = User.query.filter_by(username=uname).first()
        existing_email = User.query.filter_by(email = email).first()
        
        if existing_user:
            flash("This username already exists. please choose another one.", 'danger')
            return redirect(url_for('Register'))
        
        if existing_email:
            flash("This email is already registered. Please use another email.", 'danger')
            return redirect(url_for('Register'))
        
        
        # Hash the password using bcrypt
        hashed_password = bcrypt.generate_password_hash(pwd).decode('utf-8')

        # Create a new user using hashed password
        new_user = User(name=name, username =uname, email =email, password=hashed_password)

        try:
                
            db.session.add(new_user)
            db.session.commit()
            flash("Welcome You have been registered.", 'success')
            return redirect(url_for('main'))
        except Exception as e:
            flash("An error occured while registering. Please try again.", 'danger')
            print(str(e))
            return render_template('register.html')
    
   
    return render_template('register.html')
        
"""
 Login Logic on the web application
 
"""
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['username']
        pwd = request.form['password']
        user = User.query.filter_by(username=user_id).first()
        
 
        if user:
            if not user.is_deleted:
                #  Verify hashed password using bcrypt
                if bcrypt.check_password_hash(user.password, pwd):
                    session['logged_in'] =True
                    session['user_id'] = user.id
                    session['email'] = user.email
                    session['username'] = user.username
                    session['name'] = user.name
                    flash("Login successful!", 'success')
                    
                    user_data = {'username' : user.username,
                                'name' : user.name,
                                'email' : user.email
                                }
                    
                    return render_template('index.html',  name = user_data['name'] )

                else:
                    flash("Incorrect username or password. Please try again.", 'error')
                    
                    return  redirect(url_for('signin'))
            
            else:
                flash("User does not exist or has been deleted. Please register.", 'error')
                return redirect(url_for('signup'))
        else:
            flash("Incorrect username or password. Please try again.", 'error')     
            return  redirect(url_for('signin'))
    else:
        return redirect(url_for('signin'))
    
"""
Code for verifying the gmail using otp

"""

@app.route('/generate_otp')
def generate_otp():
        otp = ''
        for i in range(6):
            otp += str(random.randint(0, 9))
        
        return otp

@app.route('/verification')
def verification():
    name = session['name']
    return render_template('verification.html', name =name)
    

@app.route('/verify', methods = ['POST'])
def verify():
    
    session['otp'] = int(generate_otp())
    otp = session.get('otp')
    gmail = session['email']
    name = session['name']
    msg = Message("Verification Mail", sender='rajakshat7985@gmail.com', recipients=[gmail])
    msg.body = f"Your otp for the verifiaction of Text Summarizer is {str(otp)} and your username is {session['username']}."
    try:
        mail.send(msg)
        flash("Otp sent successfully")

    except Exception as e:
        msg = f"There was some problem sending the email: {str(e)}."

    return render_template('verification.html', msg =msg, name =name)
        

@app.route('/validate', methods = ['POST', 'GET'])
def validate():
    user_otp = request.form['otp']
    stored_otp = session.get('otp')
    # print("user_opt", type(user_otp))
    # print("stored_otp", type(stored_otp))
   
    name =  session['name']

    if stored_otp and stored_otp == int(user_otp):
        user = User.query.filter_by(email = session['email']).first()
        
        if user:
            
            if user.is_verified:
                flash("Your account is already verified.", 'success')

                
            else:
                # set the is_verified to True for the found user
                user.is_verified =True
                try:
                    db.session.commit()
                    flash("Email Verification Succeefully", "success")
                    
                except Exception as e:
                    db.session.rollback()
                    flash("An error occured while updating verification status", 'danger')
                    print(str(e))
        else:
            flash("User not found.", 'danger')
                
    else:
        flash("Verification failed! Try again", "danger")
       
   
    return render_template('verification.html', name=name)

""" 

Take the user complain using this form

"""

@app.route('/user_message', methods=["GET", 'POST'])
def user_message():

    if request.method == "POST":
        
        name = request.form['user_name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        date = UserQuery.query.order_by(UserQuery.date).all()

        # check if the email already exists in the database
        existing_query = UserQuery.query.filter_by(email =email).first()
        if existing_query:
            flash("This email already exists", 'danger')
            return redirect(url_for('contact'))
        
        print(name, email, subject, message)
        
        user_query = UserQuery(fname = name, email=email, subject=subject, message =message)
        
        
        try:
            db.session.add(user_query)
            db.session.commit()
            flash("Your Query form submitted successfully", 'success')
        except Exception as e:
            flash("An error occurred while submitting your query", 'danger')
            print(str(e))
            
    return render_template('contacts.html', name =name, email=email, subject=subject, message =message)



"""

Reset Password using tokens 

"""

def send_mail(user):
    token = user.get_token()
    msg = Message('Password Reset Request', recipients= [user.email], sender='rajakshat7985@gmail.com')

    msg.body = f""" To reset your password. Please follow the link below.
    
    
    {url_for('reset_token', token=token, _external =True)}
    
    and your username is {user.username}
    
    If you didn't send a password reset request. Please ignore this message.
    
    """
    mail.send(msg)



@app.route('/reset_request', methods = ['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        session['email'] = email
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



@app.route('/reset_request/<token>', methods =['GET', 'POST'])
def reset_token(token):
    user = User.verify_token(token)
    
    if user is None:
        flash("That is an invalid token or it has expired. Please try again.", 'warning')
        return redirect(url_for('reset_request'))
    else:
        return redirect(url_for('reset_password'))

"""
Logic for the Password reset

"""

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password():


    user = User.query.filter_by(email = session['email']).first()
    # print(email)
    
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
            
            
            user.password = hashed_password
            db.session.commit()
            flash("Password changed! Please login", "success")
            return redirect(url_for('login'))
    return render_template('reset_password.html')




@app.route('/account', methods= ['POST', 'GET'])
def account():
    # user_data = None
    if 'logged_in' not in session or not session['logged_in']:
        flash('Please log in first', 'error')
        return redirect(url_for('signin'))
    
    
    user_id = session['user_id']
    user = User.query.get(user_id)
        
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('signin'))
    
    user_data = {
        'username': user.username,
        'name': user.name,
        'email': user.email    
            }
            
    if user.is_verified:
        verified_msg = "Verified"
    else:
        verified_msg = "Not Verified! Kindly"
            
    
    return render_template('account.html', user_data=user_data, verified_message=verified_msg, name = user_data['name'])



# Delete the account

@app.route('/delete')
def delete():
    username = session['username']
    user = User.query.filter_by(username=username).first_or_404()
    if user:
        if user.is_deleted:
            flash('You have deleted your account', 'error')
        else:
            user.is_deleted = True
            try:
                db.session.commit()
                flash('Account deleted successfully.', 'success')
                return redirect('/')
            except Exception as e:
                db.session.rollback()
                flash("There was an issue deleting your account.", 'danger')
                print(str(e))
    else:
        flash('You are not logged in.', 'danger')
        
    
        return redirect(url_for('account'))



"""

Edit the profile details

"""

@app.route('/update', methods =['GET', 'POST'])
def edit_profile():
    
    user = User.query.filter_by(username = session['username']).first()
    
    if user:
        if request.method == 'POST':
            # Update the user Information in the database
            
            user.name = request.form['name']
            user.username = request.form['uname']
            try:
                db.session.commit()
                flash('Profile updated successfully.', 'success')
                return redirect(url_for('account'))
            except Exception as e:
                db.session.rollback()
                flash('Failed to update profile.', 'danger')
                print(str(e))
             
        
    
    return render_template('edit_profile.html', user =user)
    


""" To get out of your account """  

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash('Log out successful', 'success')
    return redirect(url_for('login'))   
    
"""Main logic that summarize the lenthy article into summary"""  

@app.route('/summarizer', methods=['POST'])
def summarizer():

    data = {}
    if request.method == "POST":
        user_input = request.form['userinput']
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(user_input)
        def calculate_word_frequency(doc):
            """This will calculate the how many times a word is repetation
                in an articles or in another word frequency of each and every word.
            """
            
            stopwords = list(STOP_WORDS) 
            word_frequencies = {}
            for word in doc:
                if word.text.lower() not in stopwords:
                    if word.text.lower() not in punctuation:
                        if word.text not in word_frequencies.keys():
                            word_frequencies[word.text] = 1
                        else:
                            word_frequencies[word.text] += 1

            # Now Normalized the word frequencies
            max_frequency = max(word_frequencies.values())
            # Normalize the word_frequencies
            for word in word_frequencies.keys():
                word_frequencies[word] = word_frequencies[word]/max_frequency
            return word_frequencies
        
        
        def find_sentence_tokens(doc):
            """Sentence tokens are units of text that represent individual sentences within a larger body of text. In natural language processing (NLP), tokenization is the process of breaking down a text into smaller components, which can be words, phrases, or sentences, depending on the level of granularity. Sentence tokens specifically refer to the segmentation of text into sentences.
            """
            return [sent for sent in doc.sents]
        
        # we are going to calculate the sentence score, to calculate the sentence score we have to calculate the frequency of repeated word in each sentence
        
        
        def find_sentence_scores(doc):
            """Sentence scores are values assigned to sentences in a document based on various criteria, such as the frequency of important words, their position in the text, or their relationships with other sentences. These scores are used to identify and prioritize sentences for inclusion in a summary.
            """
            sentence_tokens = find_sentence_tokens(doc)
            word_frequencies = calculate_word_frequency(doc)
            sentence_scores = {} 
            for sent in sentence_tokens:
                for word in sent:
                    if word.text.lower() in word_frequencies.keys():
                        if sent not in sentence_scores.keys():
                            sentence_scores[sent] = word_frequencies[word.text.lower()]
                        else:
                            sentence_scores[sent] += word_frequencies[word.text.lower()]
            return sentence_scores
        
        
        
        def find_summary(doc, content_length):
            #we have to select maximum 4 sentences out of all sentences
            """Summaries are typically much shorter than the original text, often reducing the length by a significant factor. The goal is to present the core information while eliminating unnecessary details.
            """
            
            sent_tokens = find_sentence_tokens(doc)
            content_length = int(len(sent_tokens) * content_length)
            sentence_score = find_sentence_scores(doc)
            summary = nlargest(content_length,sentence_score, key = sentence_score.get)  
            
            # if i need to combine these top 3 sentencs then 
            
            final_summary = [word.text for word in summary]
            return final_summary
        
        data['summary'] = find_summary(doc, content_length=0.5)
        
        
        def preprocess_text(sentences):
            cleaned_sentences = []
            for sentence in sentences:
                # Remove \r \n tag from the text.
                clean_sent = re.sub(r"\r\n", " ", sentence)
                # Replace :, ; this kind of symbol
                clean_sent = re.sub("[;:]", "", clean_sent)
                # Replace this [21], [34], [hdf] kind of text with with nothing.
                clean_sent = re.sub("\[.*?\]", "", clean_sent)
                
                clean_sent = " ".join(clean_sent.split())
                cleaned_sentences.append(clean_sent)
                
            return cleaned_sentences
        
        clean_output = preprocess_text(data['summary'])
        # Join this so that it won't show in a list format. like this ['hi, hello', 'My name is akshat',]
        clean_output = " ".join(clean_output)
        
        summary = Summary(user_input = user_input, summary_text = clean_output)
        
        
        db.session.add(summary)
        db.session.commit()
        # return redirect('/')
        date = Summary.query.order_by(Summary.date_created).all()
        
            
    return render_template('index.html', data =clean_output)


if __name__ == "__main__":
    app.run(debug=True, port=80)