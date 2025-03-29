import re
from flask import Flask, render_template, request, redirect, session, url_for,flash
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///TaskLog_database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key='secret_key'


# For user database
class user_register(db.Model):
    _tablename_ = "user_register"
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable= False)
    email =db.Column(db.String(100), nullable = False)
    password = db.Column(db.String(100), nullable =False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    
    def __repr__(self) -> str:
            return f"{self.sno} -  {self.title}"
    def __init__ (self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

with app.app_context():
    db.create_all()        

#email validation
def is_valid_email(email):
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_pattern, email)


@app.route('/')
def home():
    return render_template("home.html")

@app.route('/user_reg', methods = ['GET', 'POST'])
def register():
    if request.method=="POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if not is_valid_email(email):
            flash("Invalid Email formart! Please enter valid email.", "danger")
            return redirect(url_for('register'))
        
        
        existing_user = user_register.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered! Please login","danger")
            return redirect(url_for('register'))
        
        #Hash Password befoe storing(Security Purpose)
        hashed_password = generate_password_hash(password)
        
        register_user = user_register(name=name, email=email, password=hashed_password)
        db.session.add(register_user)
        db.session.commit()
        
        flash("Registration Successful!", "success")
        return redirect(url_for('register'))
    allregister = user_register.query.all()
    return render_template("user.html", allregister=allregister)

@app.route('/userdetail', methods =['GET', 'POST'])
def user_detail():
    allregister = user_register.query.all()
    return render_template('userdetail.html', allregister=allregister)

@app.route('/updateuser/<int:user_id>', methods =['POST', 'GET'])
def updateuser(user_id):
    if request.method=="POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        register_user = user_register.query.filter_by(user_id=user_id).first()
        register_user.name = name
        register_user.email =email
        register_user.password = password
        db.session.add(register_user)
        db.session.commit()
        return redirect('/userdetail')
    register_user = user_register.query.filter_by(user_id=user_id).first()
    return render_template('updateuser.html', register_user=register_user)

@app.route('/delete_userdata/<int:user_id>')
def delete_userdata(user_id):
    register_user= user_register.query.filter_by(user_id=user_id).first()
    db.session.delete(register_user)
    db.session.commit()
    return redirect('/userdetail')

        

if __name__ == '__main__':
    app.run(debug=True) 