import os
import datetime
import math

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import decimal

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdate
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
import logging
logging.getLogger().setLevel(logging.CRITICAL)

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

now = datetime.datetime.now()

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/history")
@login_required
def history():
    """Display all records for users"""

    rows = db.execute("SELECT counter, expenses, amount, note, date FROM record WHERE id = :id", id=session["user_id"])

    rows1 = db.execute("SELECT spend FROM users where id = :id", id=session["user_id"])

    return render_template("history.html", rows=rows, rows1=rows1)

@app.route("/")
@login_required
def index():
    """Display the pie chart and total expenditures for each type of expenses"""

    mobilization = db.execute("SELECT mobilization FROM totalcompute WHERE id = :id", id = session["user_id"])
    excavation = db.execute("SELECT excavation FROM totalcompute WHERE id = :id", id=session["user_id"])
    foundation = db.execute("SELECT foundation FROM totalcompute WHERE id = :id", id = session["user_id"])
    structural = db.execute("SELECT structural FROM totalcompute WHERE id = :id", id = session["user_id"])
    architectural = db.execute("SELECT architectural FROM totalcompute WHERE id = :id", id = session["user_id"])
    plumbing = db.execute("SELECT plumbing FROM totalcompute WHERE id = :id", id = session["user_id"])
    hvac = db.execute("SELECT hvac FROM totalcompute WHERE id = :id", id = session["user_id"])
    electrical = db.execute("SELECT electrical FROM totalcompute WHERE id = :id", id = session["user_id"])
    landscaping = db.execute("SELECT landscaping FROM totalcompute WHERE id = :id", id = session["user_id"])
    others = db.execute("SELECT others FROM totalcompute WHERE id = :id", id = session["user_id"])

    # Check if the expenditure of each type exists and convert the dict to float
    if mobilization:
        mobilizationc = float(mobilization[0]["mobilization"])
    else:
        mobilizationc = 0

    if foundation:
        foundationc = float(foundation[0]["foundation"])
    else:
        foundationc = 0

    if excavation:
        excavationc = float(excavation[0]["excavation"])
    else:
        excavationc = 0

    if structural:
        structuralc = float(structural[0]["structural"])
    else:
        structuralc = 0

    if architectural:
        architecturalc = float(architectural[0]["architectural"])
    else:
        architecturalc = 0

    if plumbing:
        plumbingc = float(plumbing[0]["plumbing"])
    else:
        plumbingc = 0

    if hvac:
        hvacc = float(hvac[0]["hvac"])
    else:
        hvacc = 0

    if electrical:
        electricalc = float(electrical[0]["electrical"])
    else:
        electricalc = 0

    if landscaping:
        landscapingc = float(landscaping[0]["landscaping"])
    else:
        landscapingc = 0

    if others:
        othersc = float(others[0]["others"])
    else:
        othersc = 0

    # Display the total expenditures for each type of expenses
    totals = db.execute("SELECT mobilization, excavation, foundation, structural, architectural, plumbing, hvac, electrical, landscaping, others FROM totalcompute WHERE id = :id",
            id=session["user_id"])

    # Plot the pie chart
    category = ["mobilization", "excavation", "foundation", "structural", "architectural", "plumbing", "hvac", "electrical", "landscaping", "others"]
    expenses = pd.Series([mobilizationc, excavationc, foundationc, structuralc, architecturalc, plumbingc, hvacc, electricalc, landscapingc, othersc], index=['','','','','','','','','',''], name='Expenses')
    plt.ylabel('')

    expenses.plot.pie(figsize=(8, 8))
    plt.legend(category, loc=3, fontsize=10)
    plt.title("Overall Expenditure", size=20)
    plt.savefig("static/images/pie.png")

    return render_template("plotly.html", totals=totals)

@app.route("/calendar", methods=["GET", "POST"])
@login_required
def calendar():
    """Record the type of expenses and the amount with optional notes"""
    if request.method == "POST":

        note = request.form.get("note")
        # return apology page if the amount isn't provided correctly
        amount = float(request.form.get("amount"))

        if amount < 0 or not amount:
            return apology("provide a valid amount")

        expenses = request.form.get("expenses")

        mobilization = db.execute("SELECT mobilization FROM totalcompute WHERE id = :id", id = session["user_id"])
        excavation = db.execute("SELECT excavation FROM totalcompute WHERE id = :id", id=session["user_id"])
        foundation = db.execute("SELECT foundation FROM totalcompute WHERE id = :id", id = session["user_id"])
        structural = db.execute("SELECT structural FROM totalcompute WHERE id = :id", id = session["user_id"])
        architectural = db.execute("SELECT architectural FROM totalcompute WHERE id = :id", id = session["user_id"])
        plumbing = db.execute("SELECT plumbing FROM totalcompute WHERE id = :id", id = session["user_id"])
        hvac = db.execute("SELECT hvac FROM totalcompute WHERE id = :id", id = session["user_id"])
        electrical = db.execute("SELECT electrical FROM totalcompute WHERE id = :id", id = session["user_id"])
        landscaping = db.execute("SELECT landscaping FROM totalcompute WHERE id = :id", id = session["user_id"])
        others = db.execute("SELECT others FROM totalcompute WHERE id = :id", id = session["user_id"])

        # Recognize the type of expenses and update the amount of the chosen expense type
        if expenses == "mobilization":
            if mobilization:
                mobilization = mobilization[0]["mobilization"]+amount
                db.execute("UPDATE totalcompute SET mobilization = :mobilization WHERE id = :id", id=session["user_id"], mobilization=mobilization)
            else:
                db.execute("INSERT INTO totalcompute (id, mobilization) VALUES(:id, :mobilization)", id=session["user_id"], mobilization=amount)

        elif expenses == "excavation":
            if excavation:
                excavation = excavation[0]["excavation"]+amount
                db.execute("UPDATE totalcompute SET excavation = :excavation WHERE id = :id", id=session["user_id"], excavation=excavation)
            else:
                db.execute("INSERT INTO totalcompute (id, excavation) VALUES(:id, :excavation)", id=session["user_id"], excavation=amount)

        elif expenses == "foundation":
            if foundation:
                foundation = foundation[0]["foundation"]+amount
                db.execute("UPDATE totalcompute SET foundation = :foundation WHERE id = :id", id=session["user_id"], foundation=foundation)
            else:
                db.execute("INSERT INTO totalcompute (id, foundation) VALUES(:id, :foundation)", id=session["user_id"], foundation=amount)

        elif expenses == "structural":
            if structural:
                structural = structural[0]["structural"]+amount
                db.execute("UPDATE totalcompute SET structural = :structural WHERE id = :id", id=session["user_id"], structural=structural)
            else:
                db.execute("INSERT INTO totalcompute (id, structural) VALUES(:id, :structural)", id=session["user_id"], structural=amount)

        elif expenses == "architectural":
            if architectural:
                architectural = architectural[0]["architectural"]+amount
                db.execute("UPDATE totalcompute SET architectural = :architectural WHERE id = :id", id=session["user_id"], architectural=architectural)
            else:
                db.execute("INSERT INTO totalcompute (id, architectural) VALUES(:id, :architectural)", id=session["user_id"], architectural=amount)

        elif expenses == "plumbing":
            if plumbing:
                plumbing = plumbing[0]["plumbing"]+amount
                db.execute("UPDATE totalcompute SET plumbing = :plumbing WHERE id = :id", id=session["user_id"], plumbing=plumbing)
            else:
                db.execute("INSERT INTO totalcompute (id, plumbing) VALUES(:id, :plumbing)", id=session["user_id"], plumbing=amount)

        elif expenses == "hvac":
            if hvac:
                hvac = hvac[0]["hvac"]+amount
                db.execute("UPDATE totalcompute SET hvac = :hvac WHERE id = :id", id=session["user_id"], hvac=hvac)
            else:
                db.execute("INSERT INTO totalcompute (id, hvac) VALUES(:id, :hvac)", id=session["user_id"], hvac=amount)

        elif expenses == "electrical":
            if electrical:
                electrical = electrical[0]["electrical"]+amount
                db.execute("UPDATE totalcompute SET electrical = :electrical WHERE id = :id", id=session["user_id"], electrical=electrical)
            else:
                db.execute("INSERT INTO totalcompute (id, electrical) VALUES(:id, :electrical)", id=session["user_id"], electrical=amount)

        elif expenses == "landscaping":
            if landscaping:
                landscaping = landscaping[0]["landscaping"]+amount
                db.execute("UPDATE totalcompute SET landscaping = :landscaping WHERE id = :id", id=session["user_id"], landscaping=landscaping)
            else:
                db.execute("INSERT INTO totalcompute (id, landscaping) VALUES(:id, :landscaping)", id=session["user_id"], landscaping=amount)

        elif expenses == "others":
            if others:
                others = others[0]["others"]+amount
                db.execute("UPDATE totalcompute SET others = :others WHERE id = :id", id=session["user_id"], others=others)
            else:
                db.execute("INSERT INTO totalcompute (id, others) VALUES(:id, :others)", id=session["user_id"], others=amount)

        # update the record
        db.execute("INSERT INTO record (expenses, id, amount, note, date) VALUES(:expenses, :id, :amount, :note, :date)",
        expenses=expenses, id=session["user_id"], amount=amount, note=note, date=now.strftime("%m/%d/%Y %H:%M:%S"))
        # update the cumulative expenditure of the user
        spend = db.execute("SELECT spend FROM users WHERE id = :id", id=session["user_id"])
        new_spend = spend[0]["spend"] + amount
        db.execute("UPDATE users SET spend = :spend WHERE id = :id", id=session["user_id"], spend=new_spend)


        return redirect("/")
    else:
        return render_template("calendar.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/")
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # check if the user puts the username and also if the username is not already taken
        username = request.form.get("username")
        names = db.execute("SELECT username FROM users WHERE username = :username", username=username)
        if names:
            return apology("username already taken")
        if not request.form.get("username"):
            return apology("provide username")
        # check if the user enters the password and confirmation password, and also if those two match
        password = request.form.get("password")
        if not request.form.get("password"):
            return apology("Provide password")

        confirmation = request.form.get("confirmation")
        if not request.form.get("confirmation"):
            return apology("Provide confirmation password")

        if password not in confirmation:
            return apology("passwords are not matched")
        # store hash instead of the actual user password for privacy
        hash = generate_password_hash(password)
        # insert the username and hash into the database
        rows = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username=username, hash=hash)
        # remember which user is which
        session["user_id"] = rows

        #solve the NULL problem
        db.execute("UPDATE users SET spend=0 WHERE spend is NULL")

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """Let users delete any record they need to"""

    if request.method == "POST":

        note = request.form.get("note")
        expenses = request.form.get("expenses")
        # safety check for input expense type
        amount = float(request.form.get("amount"))
        if amount < 0 or not amount:
            return apology("provide a valid amount")

        mobilization = db.execute("SELECT mobilization FROM totalcompute WHERE id = :id", id = session["user_id"])
        excavation = db.execute("SELECT excavation FROM totalcompute WHERE id = :id", id=session["user_id"])
        foundation = db.execute("SELECT foundation FROM totalcompute WHERE id = :id", id = session["user_id"])
        structural = db.execute("SELECT structural FROM totalcompute WHERE id = :id", id = session["user_id"])
        architectural = db.execute("SELECT architectural FROM totalcompute WHERE id = :id", id = session["user_id"])
        plumbing = db.execute("SELECT plumbing FROM totalcompute WHERE id = :id", id = session["user_id"])
        hvac = db.execute("SELECT hvac FROM totalcompute WHERE id = :id", id = session["user_id"])
        electrical = db.execute("SELECT electrical FROM totalcompute WHERE id = :id", id = session["user_id"])
        landscaping = db.execute("SELECT landscaping FROM totalcompute WHERE id = :id", id = session["user_id"])
        others = db.execute("SELECT others FROM totalcompute WHERE id = :id", id = session["user_id"])

        if not expenses:
            return apology("Provide an expense type")

        if expenses == "mobilization":
            if mobilization:
                mobilization = mobilization[0]["mobilization"]-amount
                db.execute("UPDATE totalcompute SET mobilization = :mobilization WHERE id = :id", id=session["user_id"], mobilization=mobilization)

        elif expenses == "excavation":
            if excavation:
                excavation = excavation[0]["excavation"]-amount
                db.execute("UPDATE totalcompute SET excavation = :excavation WHERE id = :id", id=session["user_id"], excavation=excavation)

        elif expenses == "foundation":
            if foundation:
                foundation = foundation[0]["foundation"]-amount
                db.execute("UPDATE totalcompute SET foundation = :foundation WHERE id = :id", id=session["user_id"], foundation=foundation)

        elif expenses == "structural":
            if structural:
                structural = structural[0]["structural"]-amount
                db.execute("UPDATE totalcompute SET structural = :structural WHERE id = :id", id=session["user_id"], structural=structural)

        elif expenses == "architectural":
            if architectural:
                architectural = architectural[0]["architectural"]-amount
                db.execute("UPDATE totalcompute SET architectural = :architectural WHERE id = :id", id=session["user_id"], architectural=architectural)

        elif expenses == "plumbing":
            if plumbing:
                plumbing = plumbing[0]["plumbing"]-amount
                db.execute("UPDATE totalcompute SET plumbing = :plumbing WHERE id = :id", id=session["user_id"], plumbing=plumbing)

        elif expenses == "hvac":
            if hvac:
                hvac = hvac[0]["hvac"]-amount
                db.execute("UPDATE totalcompute SET hvac = :hvac WHERE id = :id", id=session["user_id"], hvac=hvac)

        elif expenses == "electrical":
            if electrical:
                electrical = electrical[0]["electrical"]-amount
                db.execute("UPDATE totalcompute SET electrical = :electrical WHERE id = :id", id=session["user_id"], electrical=electrical)

        elif expenses == "landscaping":
            if landscaping:
                landscaping = landscaping[0]["landscaping"]-amount
                db.execute("UPDATE totalcompute SET landscaping = :landscaping WHERE id = :id", id=session["user_id"], landscaping=landscaping)

        elif expenses == "others":
            if others:
                others = others[0]["others"]-amount
                db.execute("UPDATE totalcompute SET others = :others WHERE id = :id", id=session["user_id"], others=others)

        spend = db.execute("SELECT spend FROM users WHERE id = :id", id=session["user_id"])
        new_spend = spend[0]["spend"] - amount
        db.execute("UPDATE users SET spend = :spend WHERE id = :id", id=session["user_id"], spend=new_spend)

        # update the record
        db.execute("INSERT INTO record (expenses, id, amount, note, date) VALUES(:expenses, :id, :amount, :note, :date)", expenses=expenses, id=session["user_id"], amount=amount, note=note, date=now.strftime("%m/%d/%Y %H:%M:%S"))

        return redirect("/")
    else:
        return render_template("delete.html")

@app.route("/controlpanel", methods=["GET", "POST"])
def controlpanel():
    """render controlpanel."""
    if request.method == "POST":
        return redirect("/")
        #return redirect(url_for("home"))
    else:
        print
        return render_template("controlpanel.html")

@app.route("/structural")
def structural():
    rows = db.execute("SELECT counter, expenses, amount, note, date FROM record WHERE id = :id AND (expenses = 'structural')", id=session["user_id"])

    rows1 = db.execute("SELECT structural FROM totalcompute where id = :id", id=session["user_id"])

    return render_template("structural.html", rows=rows, rows1=rows1)

@app.route("/architectural")
def architectural():
    rows = db.execute("SELECT counter, expenses, amount, note, date FROM record WHERE id = :id AND (expenses = 'architectural')", id=session["user_id"])

    rows1 = db.execute("SELECT architectural FROM totalcompute where id = :id", id=session["user_id"])

    return render_template("architectural.html", rows=rows, rows1=rows1)

@app.route("/hvac")
def hvac():
    rows = db.execute("SELECT counter, expenses, amount, note, date FROM record WHERE id = :id AND (expenses = 'hvac')", id=session["user_id"])

    rows1 = db.execute("SELECT hvac FROM totalcompute where id = :id", id=session["user_id"])

    return render_template("hvac.html", rows=rows, rows1=rows1)

@app.route("/electrical")
def electrical():
    rows = db.execute("SELECT counter, expenses, amount, note, date FROM record WHERE id = :id AND (expenses = 'electrical')", id=session["user_id"])

    rows1 = db.execute("SELECT electrical FROM totalcompute where id = :id", id=session["user_id"])

    return render_template("electrical.html", rows=rows, rows1=rows1)

@app.route("/password", methods=["GET", "POST"])
def password():
    """change password"""

    if request.method == "POST":
        # check if the user enters his/her current password
        password = request.form.get("password")
        if not request.form.get("password"):
            return apology("Provide password")
        # ask for the new password
        password_new = request.form.get("newpassword")
        if not request.form.get("newpassword"):
            return apology("provide new password")
        # ask for the confirmation of the new password
        confirmation = request.form.get("confirmation")
        if not request.form.get("confirmation"):
            return apology("Provide confirmation password")
        # check if those two match
        if password_new not in confirmation:
            return apology("new passwords are not matched")
        # hash the password
        hash = generate_password_hash(password_new)
        # update the password on the users table
        password_final = db.execute("UPDATE users SET hash = :hash WHERE id = :id", id=session["user_id"], hash=hash)

        return redirect("/")

    else:
        return render_template("password.html")



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)