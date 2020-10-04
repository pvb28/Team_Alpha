#!/usr/bin/env python
# coding: utf-8
#packages 
import pandas as pd
import numpy as np
from pandas import ExcelWriter, ExcelFile
import nltk

from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
import string
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
from nltk.corpus import wordnet
import mysql.connector as mc
from mysql.connector import Error
from mysql.connector import MySQLConnection
import time
import requests

from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
import wave
import os
import ast
from flask import Flask, render_template, redirect, flash
from flask_mysql_connector import MySQL
import time
#import MySQLdb

app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DATABASE'] = 'abusive_words'
app.config['MYSQL_PASSWORD'] = '28@PvB28'
mysql = MySQL(app)


#required functions
def connect():
    """connect to mysql database"""
    conn = None
    try:
        conn = mysql.connection 
        return conn
    except Error as e:
        print(e)


#func for checking list on words in database
def check_list(conn, wds):
    try:
        qry = "select distinct * from abusive where"
        for w in wds:
            t = w
            if len(w) > 5:
                t = w[:5]
            qry += " abusive_wrds like \'"+t+"%\' or"
        qry = qry[:-3]
        qry += ";"
        #print(qry)
        cursor = conn.cursor()
        cursor.execute(qry)
        row = cursor.fetchall()
        if row is None or len(row) == 0 or len(wds) == 0:
            return 0, []
        else:
            return 1, [row] 
        
    except Error as e:
        print(e)
    finally :
        pass

#for closing function
def close_the_connection(conn):
    try:
        conn.close()
    except Error as e:
        print(e)

#for text cleaning
def remove_punct(text):
    s =set(['"','(',')','.',',','-','<','>','/','\',%', '\\x', '!','?'])
    no_pnt = "".join([c.lower() for c in text if c not in s])
    return no_pnt

def tknz_text(text):
    return word_tokenize(text)
    
#after tokenization, we have to do remove stop words
def remove_stopwords(text):
    stopword = nltk.corpus.stopwords.words('english')
    tp = ["as","bone","hello","bon","bit","nig","fu","moth","mother","mot","mind","but","nut","crack","who","screw","nasty","fat","fag","skank","horn","big","fist","rap","dum","per","boot","boo","in","int","fioot","ball","wan","kiss","dog","ban","bang","puss","got","goto","mast","cam","foot","piece ","pieceof","pie","hand","hob","eat","hook","whack","upthe","up","blow","spa","span","fast","god","go","bull","no","easy","jack"]
    stopword.extend(tp)
    text = [word for word in text if word not in stopword]
    
    return text

#func for stemming
def stmng(wrds):
    stemmer = SnowballStemmer("english")
    res = []
    for w in wrds:
        res.append(stemmer.stem(w))
    return res 

CHUNK = 1024
@app.route('/')
def index():
    delete()
    #print("entered into index file")
    return render_template('index.html')

audio_path = '/home/veera/Downloads/'

def delete():
    global audio_path
    lst = os.listdir(audio_path)
    for i in lst:
        if i.endswith('.wav'):
            os.remove(audio_path+i)

l=[]
@app.route('/run/')
def my_link():
    print("entered into function for processing")
    
    time.sleep(15)
    c = '0' + '.wav'
    counter  = 0
    conn = connect()
    model = Model("vosk-model-small-en-in-0.4")
    pth = os.listdir(audio_path)
    #print(pth)
    print("entering into while loop")
    while(c in pth):
        #sound = AudioSegment.from_wav('C:/Users/admin/Downloads/' +  i )
        #sound = sound.set_channels(1) # To make it MONO Channel
        #sound = sound.set_frame_rate(44100) # Sample Frame rate taken here = 44,100 Hz
        #sound.export('C:/Users/admin/Downloads/' + i , format="wav")

        wf = wave.open(audio_path +'/'+ c, 'rb')
        rec = KaldiRecognizer(model, wf.getframerate())
        while True:
            data = wf.readframes(CHUNK)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                pass

        dict = ast.literal_eval(rec.FinalResult()) #changing the string to dictionary

        print(c)
        s = dict["text"]
        print(s)
        #integrate tc model
        temp = remove_punct(s)
        temp = tknz_text(temp)
        temp = remove_stopwords(temp)
        temp = stmng(temp)
        #for removing punctions
        puncs =set(['"','(',')','.',',','-','<','>','/','\',%', '\\x', '!','?',"'",'s'])
        temp2= []
        for i in temp:
            if i[0].isalpha() == True:
                temp2.append(i)        

        #for removing spaces
        temp1 = []
        for i in temp2:
            if i not in ("", '', " ",' '):
                temp1.append(i)
               
        fg, word = check_list(conn, temp1)
        if fg == 1:
            #flash("Abusive Detected")
            print("Abusive Detected")
        else:
            print("Normal Text")
        print()
        #close_the_connection(conn)

        time.sleep(0.01)
        counter = counter + 1
        c = '0' + ' ' + '(' + str(counter) + ')' + '.wav'
        pth = os.listdir(audio_path)
        time.sleep(5)
    print("exiting while loop")
    delete()
    return redirect('http://127.0.0.1:5000/')

if __name__ == '__main__':
  app.run(debug=True)
