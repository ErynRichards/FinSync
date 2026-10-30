#flask file
#can replace if needed
#creates flask app, connects website urls to functions that handle them
import os
from flask import Flask
from auth import register, login, dashboard

app = Flask(__name__)

app.secret_key = os.environ["FLASK_SECRET_KEY"]

#registration
app.add_url_rule("/register", "register", register, methods=["GET", "POST"])

#login
app.add_url_rule("/login", "login", login, methods=["GET", "POST"])

#dashboard
app.add_url_rule("/dashboard", "dashboard", dashboard)

if __name__ == "__main__":
    app.run(debug=True)
