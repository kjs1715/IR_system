# coding=utf-8

import os 
import sys
from flask import Flask, redirect, url_for

''' 2019/11/25 
    flask example (testing)
'''

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello world'

@app.route('/guest/<guest>')
def hello_guest(guest):
   return 'Hello %s as Guest' % guest


@app.route('/user/<name>')
def hello_user(name):
   if name =='admin':
      return redirect(url_for('hello'))
   else:
      return redirect(url_for('hello_guest',guest = name))

if __name__ == '__main__':
    app.run(debug=True)
    