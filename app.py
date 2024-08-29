from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient
import ml_model  # Ensure this file defines a load_model() function that returns a trained model
import numpy as np

app = Flask(__name__)
model = ml_model.load_model()  # Load your pre-trained model

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
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
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)
