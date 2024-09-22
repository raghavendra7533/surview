from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
import json
from datetime import datetime
from functools import wraps
from openai import OpenAI
import uuid
import re
from helper import generate_questions, create_call, extract_complete_questions, get_calls, get_call_details, extract_call_details

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for sessions and flashing messages
OPENAI_API_KEY = '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'
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
            'status': 'in_progress',
            'problem_description': request.form['problem_description'],
        }
        
        # Generate questions using OpenAI
        prompt = generate_questions(survey_data)

        try:
            response = client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=1000,
                n=1,
                stop=None,
                temperature=0.7,
            )

            # Log the raw response
            app.logger.debug(f"Raw OpenAI response: {response.choices[0].text}")

            # Extract complete question objects from the truncated response
            questions = extract_complete_questions(response.choices[0].text)

            # Log the parsed questions
            app.logger.debug(f"Parsed questions: {questions}")

            if not questions:
                raise ValueError("No valid questions found in the response")

            # Store the full question structure in the survey_data
            survey_data['questions'] = questions
            
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
            
            # Store the full question structure in the session for editing
            session['generated_questions'] = questions
            session['surview_id'] = survey_data['id']
            app.logger.debug(f"Stored {len(questions)} questions in session")
            
            return redirect(url_for('edit_questions'))

        except Exception as e:
            app.logger.error(f"Error in create_surview: {str(e)}")
            flash('An error occurred while generating questions. Please try again.', 'error')

    return render_template('create_surview.html')

@app.route('/edit_questions', methods=['GET', 'POST'])
def edit_questions():
    questions = session.get('generated_questions', [])
    survey_id = session.get('survey_id', '')
    print('HHHH'+survey_id)
    with open('surviews.json', 'r') as f:
        json_data = json.load(f)
    response = create_call(json_data[-1]['title'], session['user'], json_data[-1]['id'])
    if request.method == 'POST':
        print(questions)
        with open("surviews.json", "r") as f:
            json_data = json.load(f)
            agent_id = json_data[-1]['agent_id']
        return redirect(url_for('homepage'))
    return render_template('edit_questions.html', questions=questions)

@app.route('/preview/<agent_id>')
def preview(agent_id):
    return redirect("https://calleragent.vercel.app/?id="+agent_id)


@app.route('/surview/<surview_id>')
def view_surview(surview_id):
    with open('surviews.json', 'r') as f:
        surviews = json.load(f)
    # Find the specific surview
    surview = next((s for s in surviews if s['id'] == surview_id), None)
    
    get_calls(surview_id ,surview['agent_id'])
    if surview['calls']:
        print(surview['calls'])
    if surview is None:
        abort(404) 
    print(surview)
    return render_template('view_surview.html', surview=surview)

@app.route('/surview/agent/<agent_id>')
def disclaimer(agent_id):
    return render_template('disclaimer.html', agent_id=agent_id)

@app.route('/surview/<surview_id>/<call_id>')
def view_call(surview_id, call_id):
    try:
        response = get_call_details(surview_id, call_id)
        print(response)
        app.logger.debug(f"Response from get_call_details: {response}")
        
        call_details = extract_call_details(response)
        if call_details:
            return render_template('call_template.html', surview_id=surview_id, call_details=call_details)
        else:
            flash('Failed to extract call details', 'error')
    except Exception as e:
        app.logger.error(f"Error in view_call: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect(url_for('view_surview', surview_id=surview_id))

@app.route('/surview/<surview_id>/insights')
def view_insights(surview_id):
    # You can fetch any necessary data for the surview here
    # For now, we'll just render a template that will load our React app
    return render_template('insights_dashboard.html', surview_id=surview_id)

if __name__ == '__main__':
    app.run(debug=True)