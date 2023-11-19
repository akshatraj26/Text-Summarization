from flask import Flask, url_for, render_template, request
import json
import spacy
from string import punctuation
from heapq import nlargest
from spacy.lang.en.stop_words import STOP_WORDS
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup')
def signup():
 
    return render_template('register.html')

@app.route('/register_data', methods = ['POST'])
def register_data():
    if request.method == "POST":
        name = request.form['name']
        uname = request.form['uname']
        email = request.form['email']
        pwd = request.form['password']
        
        # print(name, uname, email, pwd)
        return render_template('register.html', name = name, uname =uname, email=email, pwd=pwd)
        

@app.route('/signin')
def signin():
    
    return render_template('login.html')

@app.route('/login')
def login():
    email = request.form['email'] 
    pwd = request.form['password']
    if email and pwd:
        return json.dumps({'validation' : validateUser(email, pwd)})
    
    return json({'validation': False})


def validateUser(username, password):
    return True



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
            
    return render_template('index.html', data =clean_output)


if __name__ == "__main__":
    app.run(debug=True)