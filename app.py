from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import json
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for sessions and flashing messages

# User authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        new_user = {
            'full_name': request.form['full_name'],
            'email': request.form['email'],
            'username': request.form['username'],
            'password': request.form['password'],  # Note: In a real application, never store passwords in plain text
            'terms_agreed': request.form.get('terms_agreed') == 'on',
            'signup_date': datetime.now().isoformat()
        }

        # Read existing data
        try:
            with open('users.json', 'r') as f:
                users = json.load(f)
        except FileNotFoundError:
            users = []

        # Check if user already exists
        for user in users:
            if user['email'] == new_user['email']:
                flash('An account with this email already exists.', 'error')
                return redirect(url_for('index'))
            if user['username'] == new_user['username']:
                flash('This username is already taken.', 'error')
                return redirect(url_for('index'))

        # If we get here, the user doesn't exist, so we can add them
        users.append(new_user)

        # Write updated data
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=2)

        # Redirect to a welcome page or dashboard
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    # If it's a GET request, just render the signup form
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Read existing data
        try:
            with open('users.json', 'r') as f:
                users = json.load(f)
        except FileNotFoundError:
            users = []

        # Check if user exists and password is correct
        for user in users:
            if (user['username'] == username or user['email'] == username) and user['password'] == password:
                session['user'] = user['username']
                flash('Logged in successfully!', 'success')
                return redirect(url_for('homepage'))

        flash('Invalid username or password.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/homepage')
@login_required
def homepage():
    user_surviews = []
    with open('surviews.json', 'r') as f:
        surviews = json.load(f)
    for surview in surviews:
        if surview['creator'] == session['user']:
            user_surviews.append(surview)
    return render_template('homepage.html', username=session['user'], surviews=surviews, user_surviews=user_surviews)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/create_surview', methods=['GET', 'POST'])
@login_required
def create_surview():
    if request.method == 'POST':
        new_surview = {
            'title': request.form['title'],
            'description': request.form['description'],
            'creator': session['user'],
            'created_at': datetime.now().isoformat(),
            'questions': []
        }
        
        questions = request.form.getlist('questions[]')
        question_types = request.form.getlist('question_types[]')
        
        for q, q_type in zip(questions, question_types):
            new_surview['questions'].append({
                'question': q,
                'type': q_type
            })
        
        # Load existing surviews
        try:
            with open('surviews.json', 'r') as f:
                surviews = json.load(f)
        except FileNotFoundError:
            surviews = []
        
        # Add new surview and save
        surviews.append(new_surview)
        with open('surviews.json', 'w') as f:
            json.dump(surviews, f, indent=2)
        
        flash('Surview created successfully!', 'success')
        return redirect(url_for('homepage'))
    
    return render_template('create_surview.html')


if __name__ == '__main__':
    app.run(debug=True)