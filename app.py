import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    ls = []
    id = session["user_id"]
    info = db.execute("SELECT * FROM holdings WHERE user_id = ? AND qty != 0",id)
    cash = db.execute("SELECT cash FROM users WHERE id = ?",id)
    print(cash)
    cash= round(cash[0]['cash'],2)
    total = 0
    for each in info:
        #look for price of stock
        baz = lookup(each["symbol"])
        price = baz["price"]
        ctotal = baz["price"] * each["qty"]
        total = total + ctotal
        each["cprice"] =round(price,2)
        each["ctotal"] = ctotal
        ls.append(each)
    total = total + cash
    total = usd(total)
    return render_template("index.html",ls = ls, cash = cash, total = total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        info = lookup(request.form.get("symbol"))
        #return as string
        qty = request.form.get("shares")
        if not info:
            return apology("Blank quote", 400)
        try:
            qty = float(qty)
        except:
            return apology("Must be number",400)
        try:
            if qty % 1 != 0:
                return apology("Only whole numbers!", 400)
            qty = int(qty)
        except:
            return apology("Must be number",400)
        if type(qty) == str:
            return apology("Must be a number!",400)
        if not info:
            return apology("Stock symbol does not exist!", 400)
        if qty < 0:
            return apology("Invalid quantity", 400)
        total = info["price"] * qty
        id = session["user_id"]
        cash = db.execute("SELECT cash FROM users WHERE id = ?", id)
        cash = cash[0]['cash']
        typeof = "buy"
        foo = db.execute("SELECT cash FROM users WHERE id = ?", id)
        remain = cash - total
        if total> cash:
            return apology("Not enough cash to buy!", 400)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", remain, id)
        # if found holdings
        i = 0
        for z in db.execute("SELECT stock FROM holdings WHERE user_id = ?", id):
            if info["name"] in z["stock"]:
                finalqty = db.execute("SELECT qty FROM holdings WHERE user_id = ? AND stock = ?",id,info["name"])
                finalqty = finalqty[0]['qty'] + qty
                db.execute("INSERT INTO trans VALUES (?,?,?,?,?,?)",id,info["name"],qty,info["price"],typeof,info["symbol"])
                db.execute("UPDATE holdings SET qty = ?, type =?, trans = ? WHERE user_id = ? AND stock = ? ", finalqty, typeof,qty,id, info["name"])
            else:
                db.execute("INSERT INTO trans VALUES (?,?,?,?,?,?)",id,info["name"],qty,info["price"],typeof,info["symbol"])
                db.execute("INSERT INTO holdings VALUES (?,?,?,?,?,?,?)", id, info["name"], qty, total,typeof, info["symbol"],info["price"])
            i = i+1
        if i == 0:
            db.execute("INSERT INTO trans VALUES (?,?,?,?,?,?)",id,info["name"],qty,info["price"],typeof,info["symbol"])
            db.execute("INSERT INTO holdings VALUES (?,?,?,?,?,?,?)", id, info["name"], qty, total,typeof, info["symbol"],info["price"])
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    id = session["user_id"]
    transaction = db.execute("SELECT * FROM trans WHERE id = ?",id)
    return render_template("history.html", transaction = transaction)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

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
##
@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "GET":
        return render_template("quote.html", quote="")
    #post method
    else:
        quote = lookup(request.form.get("symbol"))
        if not quote:
            return apology("Blank quote", 400)
        #if exist,
        text = "A share of " + quote['name'] + " cost "
        price = usd(quote['price'])
        return render_template("quote.html", quote=quote, text = text, price=price)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        rusername = request.form.get("username")
        rpassword = (request.form.get("password"))
        cpassword = (request.form.get("confirmation"))
        if rpassword != cpassword:
            return apology("Password doesn't match", 400)
        if not rusername:
            return apology("Username cannot be empty", 400)
        if not rpassword:
            return apology("Password cannot be empty", 400)
        if not cpassword:
            return apology("Confirm Password cannot be empty", 400)
        rows = db.execute("SELECT * FROM users WHERE username = ?", rusername)
        # Ensure username exists and password is correct
        if len(rows) !=0:
             return apology("Username already taken", 400)
        db.execute("INSERT INTO users(username, hash) VALUES (?,?)",rusername, generate_password_hash(cpassword))
        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    typec = "sell"
    id = session["user_id"]
    hold = db.execute("SELECT * FROM holdings WHERE user_id =?",id)
    if request.method == "GET":
        return render_template("sell.html", hold=hold)
    else:
        stock = request.form.get("symbol")
        qty = request.form.get("shares")
        try:
            qty = float(qty)
        except:
            return apology("Must be number",400)
        try:
            if qty % 1 != 0:
                return apology("Only whole numbers!", 400)
            qty = int(qty)
        except:
            return apology("Must be number",400)
        if type(qty) == str:
            return apology("Must be a number!",400)
        if qty < 0:
            return apology("Invalid quantity", 400)
        cash = db.execute("SELECT cash FROM users WHERE id = ?", id)
        cash = cash[0]['cash']
        quote = lookup(stock)
        gains = float(quote['price']) * float(qty)
        cash = cash + gains
        row = db.execute("SELECT qty FROM holdings WHERE user_id = ? AND symbol = ?",id, stock)
        left = row[0]['qty'] - qty
        if left < 0:
            return apology("Invalid quantity", 400)
        if left == 0:
            db.execute("DELETE FROM holdings WHERE user_id = ? AND symbol = ?",id, stock)
        else:
            db.execute("UPDATE holdings SET qty = ?, type = ? WHERE user_id = ? AND symbol = ?",left,typec,id, stock)
        db.execute("INSERT INTO trans VALUES (?,?,?,?,?,?)",id,quote["name"],qty,quote["price"],typec,stock)
        db.execute("UPDATE users SET cash = ? WHERE id = ?",cash,id)
        return redirect("/")