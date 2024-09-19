from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
import json
from datetime import datetime
from functools import wraps
from openai import OpenAI
import uuid
from helper import generate_questions, create_call, create_agent
import logging
import os
from dotenv import load_dotenv

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
            'problem_description': request.form['problem_description'],
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
        logging.debug(f"Generated {len(questions)} questions")
        
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
        logging.debug(f"Stored {len(questions)} questions in session")
        
        return redirect(url_for('edit_questions'))
    
    return render_template('create_surview.html')

logging.basicConfig(level=logging.DEBUG)

import json
import logging

logging.basicConfig(level=logging.DEBUG)

@app.route('/edit_questions', methods=['GET', 'POST'])
def edit_questions():
    if request.method == 'POST':
        updated_questions = request.form.getlist('questions[]')
        logging.debug(f"Received {len(updated_questions)} questions: {updated_questions}")

        try:
            # Read the existing surviews from the JSON file
            with open('surviews.json', 'r') as f:
                surviews = json.load(f)
            logging.debug(f"Loaded {len(surviews)} surveys from JSON")

            # Find the survey we're editing (assuming it's the last one added)
            if surviews:
                current_survey = surviews[-1]
                current_survey['questions'] = [{"question": q} for q in updated_questions]
                logging.debug(f"Updated survey with {len(current_survey['questions'])} questions")
                current_survey_id = current_survey['id']
                current_survey_title = current_survey['title']
                current_survey_username = current_survey['creator']
                print(current_survey_title)

                # Write the updated data back to the JSON file
                with open('surviews.json', 'w') as f:
                    json.dump(surviews, f, indent=2)
                logging.debug("Wrote updated surveys to JSON")

                # Call the create_agent function
                create_call(current_survey_title, current_survey_username, current_survey_id)
                logging.debug("Created agent")
                logging.debug(current_survey_title)

                flash('Questions updated successfully!', 'success')
            else:
                flash('No surveys found to update.', 'error')
                logging.error("No surveys found in the JSON file")

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}", exc_info=True)
            flash(f'An error occurred while updating questions: {str(e)}', 'error')

        return redirect(url_for('homepage'))
    
    # For GET requests, display the questions for editing
    try:
        with open('surviews.json', 'r') as f:
            surviews = json.load(f)
        if surviews:
            questions = [q['question'] for q in surviews[-1]['questions']]
        else:
            questions = []
    except Exception as e:
        logging.error(f"Error loading questions: {str(e)}", exc_info=True)
        questions = []

    logging.debug(f"Rendering edit_questions.html with {len(questions)} questions")
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

from flask import jsonify

@app.route('/regenerate_questions', methods=['POST'])
def regenerate_questions():
    # Retrieve the survey details from the session or database
    survey_data = session.get('current_survey', {})

    # Generate new questions using OpenAI (similar to your create_surview function)
    prompt = f"Generate {survey_data.get('question_count', 5)} survey questions based on the following information:\n\n"
    prompt += f"Title: {survey_data.get('title', '')}\n"
    prompt += f"Expected Insights: {survey_data.get('insights', '')}\n"
    prompt += f"Problem Description: {survey_data.get('problem_description', '')}\n"
    prompt += f"Interview Tone: {survey_data.get('interview_tone', '')}\n"
    prompt += f"Maximum Follow-up Questions: {survey_data.get('follow_up_questions', 0)}\n\n"
    prompt += "Provide only the questions, separated by newlines."

    try:
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.7,
        )

        new_questions = response.choices[0].text.strip().split('\n')
        
        # Update the session with new questions
        session['generated_questions'] = new_questions

        return jsonify({'success': True, 'questions': new_questions})
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to generate questions'}), 500


if __name__ == '__main__':
    app.run(debug=True)