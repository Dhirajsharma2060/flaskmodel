# Asthma Care chatbot Web Application

## Overview
The Asthma Care Prediction Web App is designed to assist users in monitoring their asthma symptoms and receiving personalized recommendations based on the severity of their condition. The application leverages machine learning and integrates with MongoDB for data storage, providing a user-friendly interface for symptom logging and health advice.

## Features
- **User Authentication**: Sign-up and login functionality using Flask sessions and MongoDB.
- **Asthma Severity Prediction**: Machine learning model to predict asthma severity based on user symptoms.
- **Personalized Recommendations**: Tailored health advice depending on the severity of asthma symptoms.
- **MongoDB Integration**: Store user details, symptoms, and prediction results in a MongoDB database.
- **Secure Password Storage**: Passwords are hashed using `werkzeug.security`.
- **Responsive UI**: Simple and intuitive interface for user interaction.

## Technology Stack
- **Backend**: Flask (Python)
- **Database**: MongoDB (MongoDB Atlas)
- **Machine Learning**: Integrated via a custom `ml_model.py` module
- **Frontend**: HTML/CSS (using Flask’s `render_template` for dynamic pages)
- **Security**: Flask sessions and password hashing

## Prerequisites
- Python 3.x
- MongoDB Atlas account (or local MongoDB installation)
- Flask and other dependencies (listed in `requirements.txt`)

## Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/asthma-care-app.git
cd asthma-care-app
```
### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```
### 3. Configure MongoDB Connection
```bash
username = 'YourMongoDBUsername'
password = 'YourMongoDBPassword'
connection_string = f'mongodb+srv://{username}:{quote_plus(password)}@your-cluster.mongodb.net/asthma_care?retryWrites=true&w=majority'
```
### 4. Machine Learning Model
Ensure the ml_model.py file contains the load_model() function that loads the machine learning model for asthma severity prediction.
### 5. Run the Application
```bash
python app.py
```
### 6. Access the Application
```bash
http://127.0.0.1:5000
```

### Key Endpoints

Usage
Key Endpoints
- /: The homepage (redirects to login if the user is not authenticated).
- /signup: New users can register.
- /login: Existing users can log in.
- /predict: Users can submit their symptoms to receive a severity prediction and recommendation.
- /logout: Users can log out from their session.