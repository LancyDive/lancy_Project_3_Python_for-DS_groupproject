from flask import Flask, render_template , jsonify, request, session, redirect, url_for
import pickle
import numpy as np
import sklearn
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
model = pickle.load(open('model.pkl','rb'))

app.secret_key = 'loanApproval-app-1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/loanpred'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

# db.create_all()
# db.session.commit()
        

# This function is used to create all the database tables
def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the username already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', message='User already exists!')
        # Create a new user instance
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('home'))
    
    # If the request method is GET, render the registration form
    return render_template('register.html')
   

# Login API route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.user_id
            return render_template('predict.html') 
        else:
            return 'Invalid username or password'
    else:
        return render_template('login.html')


# Predict API route
@app.route('/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return redirect(url_for('login')) 

    # Get input data from the form
  # Get input data from the form
    gender = int(request.form.get('gender'))
    married = int(request.form.get('married'))
    dependents = int(request.form.get('dependents'))
    education = int(request.form.get('education'))
    self_employed = int(request.form.get('self_employed'))
    
    # Retrieve form fields and handle None values
    applicantincome = int(request.form.get('applicantincome')) 
    coapplicantincome = float(request.form.get('coapplicantincome')) 
    loanamount = float(request.form.get('loanamount')) 
    loan_amount_term = float(request.form.get('loan_amount_term')) 
    credit_history = int(request.form.get('credit_history'))
    property_area = int(request.form.get('property_area'))


    # Perform loan eligibility prediction using the trained model
    prediction = model.predict([[gender,married,dependents,education,self_employed,applicantincome,coapplicantincome,loanamount,loan_amount_term,credit_history,property_area]])
    
    # output = round(prediction[0],2)

    prediction_result = "Eligible" if prediction[0] == 1 else "Not Eligible"

    # Render the prediction result on the predict.html page
    return render_template('predict.html', prediction_result=prediction_result)


# Logout API route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

# Call the create_tables function to create the tables
create_tables()

if __name__ == '__main__':
    app.run(debug=True)
