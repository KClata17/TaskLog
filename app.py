import re
from flask import Flask, render_template, request, redirect, session, url_for,flash, jsonify
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from functools import wraps

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
    status = db.Column(db.String(50), default ="Pending")
    
    categories = db.relationship('task_catagories', backref='task', lazy=True)
    
    def __repr__(self) -> str:
        return f"{self.task_id} - {self.title}"

class task_catagories(db.Model):
    __tablename__ ='task_catagories'
    cat_id = db.Column(db.Integer, primary_key=True)
    category_type = db.Column(db.String(50), nullable= False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_register.user_id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('TaskLog.task_id'), nullable=False)
    def __repr__(self):
        return f"{self.cat_id} - {self.category_type}"
    
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
@login_required
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
    if current_user.user_id != user_id:
        flash("You are not authorized to update this user.", "danger")
        return redirect(url_for('userdash'))
    
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
        return redirect('/userdash')
    # register_user = user_register.query.filter_by(user_id=user_id).first()
    return render_template('updateuser.html', register_user=register_user)

@app.route('/delete_userdata/<int:user_id>')
def delete_userdata(user_id):
    register_user= user_register.query.filter_by(user_id=user_id).first()
    db.session.delete(register_user)
    db.session.commit()
    return redirect('/userdetail')

@app.route('/userdash')
@login_required
def userdash():
    return render_template("userdash.html",user=current_user)

##Only Login user can access the other data
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session and not current_user.is_authenticated:
            return redirect(url_for('user_login'))  # Correct endpoint name
        return f(*args, **kwargs)
    return decorated_function



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
        category_type = request.form['category']
        
        task_todo = Task_log(title = title, description=description, user_id =current_user.user_id)
        db.session.add(task_todo)
        db.session.commit()
        
        task_category = task_catagories(
            task_id = task_todo.task_id,
            user_id = current_user.user_id,
            category_type= category_type
        )
        db.session.add(task_category)
        db.session.commit()
        flash("Task added Successfully", "success")
        return redirect(url_for('tasklog'))
    
    alltasklog = (db.session.query(Task_log, task_catagories.category_type)
                  .outerjoin(task_catagories, Task_log.task_id == task_catagories.task_id)
                  .filter(Task_log.user_id == current_user.user_id)
                  .all())
    
    return render_template('tasklog.html', alltasklog=alltasklog)



    
@app.route('/tasklogdetail', methods =['GET', 'POST'])
def tasklogdetails():
    alltasklog = (
        db.session.query(Task_log, task_catagories.category_type,user_register.name)
        .outerjoin(task_catagories, Task_log.task_id == task_catagories.task_id)
        .join(user_register, Task_log.user_id==user_register.user_id)
        .all()
    )
    return render_template('tasklogdetail.html', alltasklog=alltasklog)

@app.route('/update_tasklog/<int:task_id>', methods=['GET', 'POST'])
def updatetasklog(task_id):
    task_todo = Task_log.query.filter_by(task_id=task_id).first()
    
    # Get category from query parameter (default to empty string)
    category = request.args.get('category', '')

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        task_todo.title = title
        task_todo.description = description
        db.session.commit()

        # Redirect to category page if category provided, else to /tasklogdetail
        if category:
            return redirect(url_for('category_view', cat_type=category))
        else:
            return redirect('/tasklogdetail')

    return render_template('updatetasklog.html', task_todo=task_todo)


@app.route('/delete_tasklog/<int:task_id>')
def delete_tasklog(task_id):
    task_todo = Task_log.query.filter_by(task_id=task_id).first()
    db.session.delete(task_todo)
    db.session.commit()
    return redirect('/tasklogdetail')

@app.route('/completed_task')
@login_required
def completed_task():
    completed_task = Task_log.query.filter_by(
        status='done',
        user_id=current_user.user_id
    ).all()
    return render_template('completed_task.html', alltasklog=completed_task)

@app.route('/pending_task')
def pending_task():
    pending_task = Task_log.query.filter_by(status = 'pending').all()
    return render_template('pending_tasks.html', alltasklog=pending_task)
    
 
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for('home'))

        
@app.route('/update_task_status', methods=['POST'])
def update_task_status():
    data = request.get_json()
    task_id = data.get('task_id')
    status = data.get('status')

    task = Task_log.query.get(task_id)

    if task:
        task.status = status.lower()  # Ensure lowercase for matching
        print("Task found. Updating status to:", task.status)
        db.session.commit()
        # redirect based on status
        if status.lower() == 'done':
            print("Redirecting to completed_task")
            return jsonify(success=True, redirect=url_for('completed_task'))
        else:
            print("Redirecting to pending_task")
            return jsonify(success=True, redirect=url_for('pending_task'))
        
    print("Task not found!")
    print(f"Updating Task ID {task_id} to status {status}")
    return jsonify(success=False), 400


        
@app.route('/category/<string:cat_type>')
@login_required
def view_by_category(cat_type):
    tasks = (
        db.session.query(Task_log, task_catagories.category_type)
        .join(task_catagories, Task_log.task_id == task_catagories.task_id)
        .filter(Task_log.user_id == current_user.user_id, task_catagories.category_type == cat_type)
        .all()
    )
    return render_template('category_view.html', tasks=tasks, cat_type=cat_type)



    

if __name__ == '__main__':
    app.run(debug=True) 