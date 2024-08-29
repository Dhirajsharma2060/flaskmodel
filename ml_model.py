import pickle

def load_model():
    with open('model.pkl', 'rb') as file:
        model = pickle.load(file)
    return model

def predict(data, model):
    return model.predict(data)
