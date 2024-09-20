from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
import json
from datetime import datetime
from functools import wraps
from openai import OpenAI
import uuid
from helper import generate_questions

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for sessions and flashing messages
OPENAI_API_KEY = ''
client = OpenAI(api_key=OPENAI_API_KEY)

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
            'user_profile_picture': 'default_avatar.jpg',
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
def create_surview():
    if request.method == 'POST':
        survey_data = {
            'id': str(uuid.uuid4().int)[:6],
            'title': request.form['title'],
            'description': request.form['problem_description'],
            'creator': session.get('user', 'anonymous'),
            'created_at': datetime.now().strftime("%d %b %Y"),
            'insights': request.form['insights'],
            'status': 'in_progress',
            'question_count': int(request.form['question_count']),
            'follow_up_questions': int(request.form['follow_up_questions']),
            'interview_tone': request.form['interview_tone'],
            'problem_description': request.form['problem_description']
        }
        
        # Generate questions using OpenAI
        prompt = generate_questions(survey_data)

        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.7,
        )

        questions = response.choices[0].text.strip().split('\n')
        
        # Format questions for JSON
        survey_data['questions'] = [{"question": q} for q in questions]
        
        # Read existing data
        try:
            with open('surviews.json', 'r') as f:
                surviews = json.load(f)
        except FileNotFoundError:
            surviews = []
        
        # Append new survey data
        surviews.append(survey_data)
        
        # Write updated data
        with open('surviews.json', 'w') as f:
            json.dump(surviews, f, indent=2)
        
        # Store the generated questions in the session for editing
        session['generated_questions'] = questions
        
        return redirect(url_for('edit_questions'))
    
    return render_template('create_surview.html')

@app.route('/edit_questions', methods=['GET', 'POST'])
def edit_questions():
    questions = session.get('generated_questions', [])
    if request.method == 'POST':
        print(questions)
        return redirect(url_for('homepage'))
    
    return render_template('edit_questions.html', questions=questions)

@app.route('/surview/<surview_id>')
def view_surview(surview_id):
    # Load surviews from JSON file
    with open('surviews.json', 'r') as f:
        surviews = json.load(f)
    
    # Find the specific surview
    surview = next((s for s in surviews if s['id'] == surview_id), None)
    
    if surview is None:
        abort(404)  # Surview not found
    
    return render_template('view_surview.html', surview=surview)



if __name__ == '__main__':
    app.run(debug=True)