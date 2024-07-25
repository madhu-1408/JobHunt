from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)

# Configuration for MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Madhu%4014@localhost/digital_diary'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '23adfe1f9b2e5a3d9c416406c39c5f7c23c876f0cbb5a51e'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Job model
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    pay_range = db.Column(db.String(20), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    user_username = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False)
    
    # Define relationship with User model
    user = db.relationship('User', backref=db.backref('jobs', lazy=True))

    def __repr__(self):
        return f'<Job {self.company_name}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html', current_user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Create a new user and add it to the database
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        # Redirect to the login page after registration
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/dashboard')
@login_required
def dashboard():
    # Query all jobs from the database
    jobs = Job.query.all()
    return render_template('dashboard.html', jobs=jobs)

@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    if request.method == 'POST':
        company_name = request.form['company_name']
        address = request.form['address']
        phone_number = request.form['phone_number']
        pay_range = request.form['pay_range']
        job_description = request.form['job_description']
        job_title = request.form['job_title']
        
        # Create a new job post associated with the current user
        new_job = Job(company_name=company_name, address=address, phone_number=phone_number,
                      pay_range=pay_range, job_description=job_description, job_title=job_title,
                      user_username=current_user.username)
        
        db.session.add(new_job)
        db.session.commit()
        
        return redirect(url_for('post'))
    
    jobs = Job.query.filter_by(user_username=current_user.username).all()
    return render_template('post.html', jobs=jobs)


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    job = Job.query.get_or_404(post_id)
    
    # Check if the current user is the owner of the job post
    if job.user_username != current_user.username:
        flash('You are not authorized to edit this job post.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        job.company_name = request.form['company_name']
        job.address = request.form['address']
        job.phone_number = request.form['phone_number']
        job.pay_range = request.form['pay_range']
        job.job_description = request.form['job_description']
        job.job_title = request.form['job_title']
        
        db.session.commit()
        return redirect(url_for('post'))
    
    return render_template('edit_post.html', job=job)

@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    job = Job.query.get_or_404(post_id)
    
    # Check if the current user is the owner of the job post
    if job.user_username != current_user.username:
        flash('You are not authorized to delete this job post.', 'error')
        return redirect(url_for('dashboard'))
    
    db.session.delete(job)
    db.session.commit()
    
    return redirect(url_for('post'))

if __name__ == '__main__':
    app.run(debug=True)
