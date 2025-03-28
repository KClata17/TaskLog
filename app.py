from flask import Flask, render_template, request, redirect, session, url_for,flash
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import bcrypt

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
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/user_reg', methods = ['GET', 'POST'])
def register():
    if request.method=="POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        register_user = user_register(name=name, email=email, password=password)
        db.session.add(register_user)
        db.session.commit()
    allregister = user_register.query.all()
    return render_template("user.html", allregister=allregister)

@app.route('/userdetail', methods =['GET', 'POST'])
def user_detail():
    allregister = user_register.query.all()
    return render_template('userdetail.html', allregister=allregister)

if __name__ == '__main__':
    app.run(debug=True) 