#authentication backend
#checks registration details, stops duplicates, hashes passwords
#verifies login credentials and manage sessions
from flask import request, redirect, session, flash, render_template
from werkzeug.security import generate_password_hash, check_password_hash

#need from daniel vvv
from db import get_db_connection 


#register a new user
def register():
    if request.method == "POST":

        fullName = request.form.get("fullName", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirmPassword = request.form.get("confirm_password", "")

        #check the empty fields
        if not fullName or not email or not password or not confirmPassword:
            flash("Please fill in all fields")
            return redirect("/register")

        #check email
        if "@" not in email or "." not in email.split("@")[-1]:
            flash("Invalid email address")
            return redirect("/register")

        #check passwords
        if password != confirmPassword:
            flash("Passwords do not match")
            return redirect("/register")

        if len(password) < 8:
            flash("Password must be at least 8 characters")
            return redirect("/register")

        #split the users full name
        names = fullName.split(maxsplit=1)

        if len(names) < 2:
            flash("Please enter your first and last name")
            return redirect("/register")

        first_name = names[0]
        last_name = names[1]

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            #check duplicate email
            cursor.execute(
                "SELECT user_id FROM Users WHERE email = %s",
                (email,)
            )

            if cursor.fetchone():
                flash("Email already registered")
                return redirect("/register")

            #hash password
            hashed_password = generate_password_hash(password)

            #save user
            cursor.execute(
                """INSERT INTO Users
                (first_name, last_name, email, password_hash, created_at)
                VALUES (%s, %s, %s, %s, NOW())""",
                (first_name, last_name, email, hashed_password)
            )

            connection.commit()

            flash("Registration successful")
            return redirect("/login")

        except Exception:
            if connection:
                connection.rollback()

            flash("Registration failed")
            return redirect("/register")

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    return render_template("register.html")


#log in an existing user
def login():
    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter your email and password")
            return redirect("/login")

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            #find user
            cursor.execute(
                """SELECT user_id, first_name, password_hash
                FROM Users WHERE email = %s""",
                (email,)
            )

            user = cursor.fetchone()

            #check password
            if user and check_password_hash(
                user["password_hash"], password
            ):
                session.clear()
                session["user_id"] = user["user_id"]
                session["first_name"] = user["first_name"]

                return redirect("/dashboard")

            flash("Invalid email or password")

        except Exception:
            flash("Login failed")

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return redirect("/login")

    return render_template("login.html")


#dashboard
def dashboard():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect("/login")

    return render_template("dashboard.html")
