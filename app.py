from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from pymongo import MongoClient
import ml_model  # Ensure this file defines a load_model() function that returns a trained model
from urllib.parse import quote_plus
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Function to create a new MongoClient instance
def create_mongo_client():
    username = 'Dhiraj2060'
    password = 'Vimal502'
    connection_string = f'mongodb+srv://{username}:{quote_plus(password)}@asmthamacluster0.d6anv.mongodb.net/asthma_care?retryWrites=true&w=majority'
    return MongoClient(connection_string)

# Initialize model
model = ml_model.load_model()

@app.before_request
def before_request():
    """Initialize MongoDB client and set up database connection for each request."""
    global db, collection
    client = create_mongo_client()
    db = client['asthma_care']
    collection = db['predictions']

def map_yes_no_to_int(answer):
    """Convert 'yes' or 'no' to 1 or 0."""
    return 1 if answer.lower() == 'yes' else 0

def check_threshold(symptoms, age, gender):
    """Check if the threshold conditions for severity prediction are met."""
    if all(symptoms) and age >= 60:
        return True
    elif all(symptoms) and age < 11:
        return True
    elif all(symptoms):
        return True
    elif not any(symptoms) and gender == 'male' and age >= 25:
        return False
    else:
        return False

def get_recommendation(severity):
    """Generate a recommendation based on severity."""
    recommendations = {
        0: "Your asthma condition is currently under control. Continue to monitor your symptoms regularly.",
        1: """You are experiencing mild to moderate asthma symptoms. Try some home remedies such as:
            1. Steam Inhalation: Inhale steam from hot water to open up the airways.
            2. Staying Hydrated: Drink plenty of water to keep the airways moist.
            3. Using a Humidifier: Add moisture to the air with a humidifier to prevent dryness in the airways.
            4. Breathing Exercises: Practice deep breathing exercises and pursed-lip breathing to improve lung function.
            5. Avoiding Triggers: Identify and avoid triggers such as smoke, dust, pollen, and pet dander.
            6. Maintaining a Clean Environment: Keep the home clean and free of dust, mold, and allergens.""",
        2: """You are experiencing mild to moderate asthma symptoms. Follow the same home remedies as mentioned above and consider seeing a healthcare provider if symptoms persist or worsen.""",
        3: """You are experiencing severe asthma symptoms. Please seek immediate medical attention. In the meantime, you may find the following resources helpful:
            1. <a href="https://www.youtube.com/watch?v=FyjZLPmZ534">How to ease asthma symptoms - 3 effective breathing exercises by Airofit</a>
            2. <a href="https://www.youtube.com/watch?v=B8pNeYFZNew">Exercise-Induced Asthma by CNN</a>
            3. <a href="https://www.youtube.com/watch?v=jv-revgQdPE">ASTHMA / how to cure exercise induced wheezing naturally by Andrew Folts</a>
            4. <a href="https://www.youtube.com/watch?v=JwRG8AsStLQ">Easy tips to treat Asthma & Bronchitis | Dr. Hansaji Yogendra by The Yoga Institute</a>
            5. <a href="https://www.youtube.com/watch?v=dpTNUGwXbTU">Breathing Exercises for COPD, Asthma, Bronchitis & Emphysema - Ask Doctor Jo by AskDoctorJo</a>"""
    }
    return recommendations.get(severity, "No recommendation available.")

@app.route('/')
def index():
    """Render the main page of the application."""
    if 'username' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests and return results."""
    try:
        data = request.form
        # Extract form data
        name = data['name']
        tiredness = map_yes_no_to_int(data['tiredness'])
        dry_cough = map_yes_no_to_int(data['dry_cough'])
        difficulty_breathing = map_yes_no_to_int(data['difficulty_breathing'])
        sore_throat = map_yes_no_to_int(data['sore_throat'])
        nasal_congestion = map_yes_no_to_int(data['nasal_congestion'])
        runny_nose = map_yes_no_to_int(data['runny_nose'])
        age = int(data['age'])
        gender = data['gender']

        # Prepare the symptom list and check thresholds
        symptoms = [tiredness, dry_cough, difficulty_breathing, sore_throat, nasal_congestion, runny_nose]
        if not any(symptoms):
            severity_prediction = 0
        else:
            if check_threshold(symptoms, age, gender):
                severity_prediction = 3
            else:
                none_experiencing = 1 if sum(symptoms) == 0 else 0
                user_input = [
                    tiredness, dry_cough, difficulty_breathing, sore_throat, nasal_congestion, runny_nose,
                    none_experiencing,
                    1 if age <= 9 else 0,
                    1 if age >= 10 and age <= 19 else 0,
                    1 if age >= 20 and age <= 24 else 0,
                    1 if age >= 25 and age <= 59 else 0,
                    1 if age >= 60 else 0,
                    1 if gender == 'female' else 0,
                    1 if gender == 'male' else 0,
                    0,  # Severity_Mild placeholder
                    0   # Severity_Moderate placeholder
                ]
                severity_prediction = model.predict([user_input])[0]

        # Generate recommendation
        recommendation = get_recommendation(severity_prediction)

        # Convert numpy types to native Python types
        severity_prediction = int(severity_prediction)

        # Save prediction to MongoDB
        collection.insert_one({
            'name': name,
            'symptoms': symptoms,
            'age': age,
            'gender': gender,
            'severity': severity_prediction,
            'recommendation': recommendation
        })

        # Render the result page
        return render_template('result.html', name=name, gender=gender, severity=severity_prediction, recommendation=recommendation)

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/signup', methods=['GET'])
def signup_form():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if not username or not password or not confirm_password:
        return jsonify({'error': 'All fields are required!'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match!'}), 400

    # Check if user already exists
    if collection.find_one({'username': username}):
        return jsonify({'error': 'Username already exists!'}), 400

    # Hash the password before storing it
    hashed_password = generate_password_hash(password)

    # Insert user into the database
    collection.insert_one({
        'username': username,
        'password': hashed_password
    })

    # Redirect to login page after successful signup
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login form and authenticate users."""
    if request.method == 'POST':
        data = request.form
        username = data['username']
        password = data['password']
        
        # Find the user in the database
        user = collection.find_one({'username': username})
        
        if not user:
            return jsonify({'error': 'User does not exist!'}), 404
        
        # Check the password hash
        if not check_password_hash(user['password'], password):
            return jsonify({'error': 'Incorrect password!'}), 401
        
        # Set session data and redirect to index page on successful login
        session['username'] = username
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handle user logout."""
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
