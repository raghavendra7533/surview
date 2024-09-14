# Surview

Surview is a web application that allows users to create and manage surveys. It features user authentication, a dashboard for viewing created surveys, and the ability to add questions to surveys.

## Features

- User registration and login
- Create and manage surveys
- User-friendly interface with Bootstrap
- Flash messages for user feedback

## Technologies Used

- Flask: A lightweight WSGI web application framework in Python.
- HTML/CSS: For structuring and styling the web pages.
- JavaScript: For dynamic interactions on the client side.
- JSON: For storing user and survey data.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/raghavendra7533/surview.git
   cd surview
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `users.json` file in the root directory to store user data. You can start with an empty array:

   ```json
   []
   ```

4. Run the application:

   ```bash
   python app.py
   ```

5. Open your browser and go to `http://127.0.0.1:5000` to access the application.

## Usage

- **Sign Up**: Create a new account by filling out the sign-up form.
- **Log In**: Use your credentials to log in to your account.
- **Create Surview**: After logging in, navigate to the "Create Surview" page to create a new survey.
- **Dashboard**: View your created surveys on the dashboard.
