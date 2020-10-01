#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
import wave
import os
import ast
from flask import Flask, render_template
import time
app = Flask(__name__)

CHUNK = 1024


@app.route('/')
def index():
  return render_template('index.html')

audio_path = 'C:/Users/admin/Downloads/'

l=[]
@app.route('/yo/')
def my_link():
    time.sleep(15)
    c = '0' + '.wav'
    counter  = 0
    while(c in os.listdir(audio_path)):
    #for i in os.listdir(audio_path):
        #if i.endswith('.wav'):
        #sound = AudioSegment.from_wav('C:/Users/admin/Downloads/' +  i )
        #sound = sound.set_channels(1) # To make it MONO Channel
        #sound = sound.set_frame_rate(44100) # Sample Frame rate taken here = 44,100 Hz
        #sound.export('C:/Users/admin/Downloads/' + i , format="wav")

        wf = wave.open(audio_path +'/'+ c, 'rb')

        model = Model("vosk-model-small-en-in-0.4")

        rec = KaldiRecognizer(model, wf.getframerate())

        while True:
            data = wf.readframes(CHUNK)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                pass

        dict = ast.literal_eval(rec.FinalResult()) #changing the string to dictionary

        print(c)
        print(dict["text"])
        l.append(dict["text"])
        time.sleep(0.01)
        counter = counter + 1
        c = '0' + ' ' + '(' + str(counter) + ')' + '.wav'
    #for i in l:
    return render_template('index.html')

if __name__ == '__main__':
  app.run(debug=True)
