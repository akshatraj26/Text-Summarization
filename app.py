from flask import Flask, url_for, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import spacy
from string import punctuation
from heapq import nlargest
from spacy.lang.en.stop_words import STOP_WORDS
import re


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "thismyfirstproject"
db = SQLAlchemy(app)
app.app_context().push()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    
    
    def __repr__(self):
        return f"User: {self.name} - {self.email}"
    
  
class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.Text(), nullable=False)
    summary_text = db.Column(db.Text(), nullable=False)
    date_created = db.Column(db.DateTime, default= datetime.utcnow)
    
    def __repr__(self):
        return f"User: {self.user_input} - {self.summary_text}"
    
class UserQuery(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    fname = db.Column(db.String(80), nullable = False)
    message = db.Column(db.Text, nullable =False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    subject = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default = datetime.utcnow)
    
    def __repr_(self):
        return f"UserQuery: {self.fname} - {self.message}"
  
@app.route('/')
def main():
    return render_template('main.html')

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/contact')
def contact():
    return render_template('contacts.html')

@app.route('/signup')
def signup():
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    return redirect(url_for('main'))
    

@app.route('/user_message', methods=["GET", 'POST'])
def user_message():
    
    
    if request.method == "POST":
        name = ''
        email = ''
        name = request.form['user_name']
        
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        print(name, email, subject, message)
        
        user_query = UserQuery(fname = name, email=email, subject=subject, message =message)
        date = UserQuery.query.order_by(UserQuery.date).all()
        try:
            db.session.add(user_query)
            db.session.commit()
        except:
            warning = "This email already exists"
            return render_template('contacts.html', message = warning)
    return render_template('contacts.html', name =name, email=email, subject=subject, message =message)
            
            
            
      

@app.route('/register_data', methods = ['GET', 'POST'])
def Register():
    if request.method == "POST":
        name = request.form['name']
        uname = request.form['uname']
        email = request.form['email']
        pwd = request.form['password']
        
        # print(name, uname, email, pwd)
        
        new_user = User(name=name, username =uname, email =email, password=pwd)


        try:
            
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
        except:
            warning_message = "This username already exists. please choose another one."
            return render_template('register.html', message =warning_message)
    
    else:
        
        return render_template('register.html', name = name, uname =uname, email=email, pwd=pwd)
        

@app.route('/signin')
def signin():
    
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['username']
        pwd = request.form['password']
        user = User.query.filter_by(username=user_id).first()
        
        if user:
            if user.password == pwd:
                session['logged_in'] =True
                session['user_id'] = user.id
                flash("Login successful!", 'success')
                return redirect(url_for('index'))

            else:
                flash("Incorrect password. Please try again.", 'error')
                message = "Incorrect password. Please try again."
                return  render_template('login.html', message = message)
            
        else:
            flash("User does not exist. Please register.", 'error')
            message = "User does not exist. Please register."
            return render_template('login.html', message = message)
    else:
        return redirect(url_for('signin'))
    

    

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
    app.run(debug=True)