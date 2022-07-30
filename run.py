from flask import Flask, flash, redirect, render_template, url_for, session, request, jsonify 


app = Flask(__name__)



# Home page
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
     return render_template('myhome.html')



@app.route('/profile', methods=['GET', 'POST'])
def profile():
     return render_template('myprofile.html')


if __name__=='__main__':
    app.run()
