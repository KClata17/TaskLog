import re
from flask import Flask, render_template, request, redirect, session, url_for,flash
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from werkzeug.security import check_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///TaskLog_database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key='secret_key'
login_manager = LoginManager(app)  # Initialize LoginManager
login_manager.login_view = 'user_login'  # Redirect to login page if not logged in

#load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return user_register.query.get(int(user_id))


# For user database
class user_register(db.Model, UserMixin):
    __tablename__ = "user_register"
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable= False)
    email =db.Column(db.String(100), nullable = False, unique=True)
    password = db.Column(db.String(255), nullable =False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    
    def get_id(self):
        return str(self.user_id)
    
    def __repr__(self) -> str:
            return f"{self.user_id} -  {self.name}"
    def __init__ (self, name, email, password):
        self.name = name
        self.email = email
        #self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.password = generate_password_hash(password)
        
    def check_password(self,password):
        #return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
        return check_password_hash(self.password, password)
        



class Task_log(db.Model):
    __tablename__ = 'TaskLog'
    task_id = db.Column(db.Integer, primary_key =True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_register.user_id'), nullable=False)
    title = db.Column(db.String(200), nullable = False)
    description = db.Column(db.String(700), nullable = False)
    task_created = db.Column(db.DateTime, default = datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"{self.task_id} - {self.title}"


    
with app.app_context():
    db.create_all()        

#email validation
def is_valid_email(email):
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_pattern, email)


@app.route('/')
def home():
    return render_template("home.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

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
        #hashed_password = generate_password_hash(password)
        
        register_user = user_register(name=name, email=email, password=password)
        db.session.add(register_user)
        db.session.commit()
        
        flash("Registration Successful!", "success")
        return redirect(url_for('user_login'))
    allregister = user_register.query.all()
    return render_template("user.html", allregister=allregister)

@app.route('/userdetail', methods =['GET', 'POST'])
def user_detail():
    allregister = user_register.query.all()
    return render_template('userdetail.html', allregister=allregister)

@app.route('/updateuser/<int:user_id>', methods =['POST', 'GET'])
def updateuser(user_id):
    register_user = user_register.query.filter_by(user_id=user_id).first()
    if request.method=="POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        
        register_user.name = name
        register_user.email =email
        
        # register_user.password = password
        if password:
            register_user.password = generate_password_hash(password)
        # db.session.add(register_user)
        db.session.commit()
        flash("User updated successfully!", "Success")
        return redirect('/userdetail')
    # register_user = user_register.query.filter_by(user_id=user_id).first()
    return render_template('updateuser.html', register_user=register_user)

@app.route('/delete_userdata/<int:user_id>')
def delete_userdata(user_id):
    register_user= user_register.query.filter_by(user_id=user_id).first()
    db.session.delete(register_user)
    db.session.commit()
    return redirect('/userdetail')




## Login parts are available from here
@app.route('/login', methods =['GET', 'POST'])
def user_login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        
        user = user_register.query.filter_by(email=email).first()
        
        if user:
            print(f"Stored Hash: {user.password}")  # Debugging line
            print(f"Entered Password: {password}")  # Debugging line
            print(f"Check: {user.check_password(password)}")  # Debugging line
    #     if user:
    #         if user.check_password(password):
    #             login_user(user)
    #             flash("Login Successfyll!", "success")
    #             return redirect(url_for('dashboard'))
    #         else:
    #             flash("Invalid Password!", "danger")
                
    #     else:
    #         flash("Sorry! User not found.", "danger")
    # return render_template('login.html')
                
        if user and user.check_password(password):
            login_user(user)
            flash("Login Successful", "Success")
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('user_login'))
    return render_template('login.html')

## Tasklog parts are here:
@app.route('/tasklog', methods =['GET', 'POST'])
@login_required
def tasklog():
    if request.method =="POST":
        title = request.form['title']
        description = request.form['description']
        task_todo = Task_log(title = title, description=description, user_id =current_user.user_id)
        db.session.add(task_todo)
        db.session.commit()
        flash("Task added Successfully", "Success")
    alltasklog = Task_log.query.filter_by(user_id=current_user.user_id).all()
    #Debug: print the datas in terminal

    # for task in alltasklog:
    #     print(f"Task ID: {task.task_id}, tittle: {task.tittle}, Description: {task.description}, User:{task.user_id} ")
    return render_template('tasklog.html', alltasklog=alltasklog)



    
@app.route('/tasklogdetail', methods =['GET', 'POST'])
def tasklogdetails():
    alltasklog=Task_log.query.all()
    return render_template('tasklogdetail.html', alltasklog=alltasklog)
 
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for('user_login'))

        



if __name__ == '__main__':
    app.run(debug=True) 