import sqlite3, os, json
from flask import Flask, render_template, session, request, jsonify, flash, make_response, redirect
from passlib.hash import sha256_crypt as sha256

app = Flask(__name__)
app.secret_key = os.urandom(24)

def row_dictionary(row):
        return {key: value for key, value in zip(row.keys(), row)}

@app.context_processor
def inject_user():
    if 'username' in session:
        logged_in = True
        username = session['username']
    else:
        logged_in = False
        username = None
    return dict(logged_in=logged_in, username=username)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/codes', methods=["GET", "POST"])
def api_codes():
    if 'username' in session:
        if request.method == "GET":
            with sqlite3.connect('database.db') as connection:
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                cursor.execute('''
                    SELECT * FROM codes WHERE code_id IN (
                        SELECT code_id FROM users_codes WHERE user_id = (
                            SELECT user_id FROM users WHERE username = :username
                        )
                    )
                ''', {'username': session['username']})
            codes = cursor.fetchall()
            return jsonify([row_dictionary(row) for row in codes])
        
        if request.method == "POST":
            print(request.form)
            username = session['username']
            title = request.form.get('title')
            content = request.form.get('content')
            visibility = request.form.get('visibility')
            formdata = {'username': username, 'title': title, 'content': content, 'visibility': visibility}
            with sqlite3.connect('database.db') as connection:
                cursor = connection.cursor()
                cursor.execute('''INSERT INTO codes (title, content, owner_id, visibility) VALUES (:title, :content, (SELECT user_id FROM users WHERE username = :username), :visibility)''', formdata)
                cursor.execute('''INSERT INTO users_codes (user_id, code_id) VALUES ((SELECT user_id FROM users WHERE username = :username), (SELECT last_insert_rowid() FROM codes))''', formdata)
            return "200"
    return "403"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form.get("username")
        if not username:
            flash("No username provided")
            return make_response(redirect("/login"))
        
        password = request.form.get("password")
        if not password:
            flash("No password provided")
            return make_response(redirect("/login"))
        
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT username FROM users WHERE username=?', (username,))
            if not cursor.fetchall():
                flash(f"Could not find username '{username}'")
                return make_response(redirect("/login"))
            
            cursor.execute('SELECT password FROM users WHERE username=?', (username,))
            hashed_password = cursor.fetchone()[0]
            if not sha256.verify(password, hashed_password):
                flash("Incorrect username or password")
                return make_response(redirect("/login"))

            session['username'] = username
            res = make_response(redirect("/"))
            return res

@app.route("/logout", methods=["GET"])
def logout():
    session.pop('username', None)
    res = make_response(redirect("/"))
    return res

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    if request.method == 'POST':
        username = request.form.get("username")
        if not username:
            flash("No username provided")
            return make_response(redirect("/signup"))
        
        password = request.form.get("password")
        if not password:
            flash("No password provided")
            return make_response(redirect("/signup"))
        
        confirm_password = request.form.get("confirm-password")
        if not confirm_password:
            flash("No confirmation password provided")
            return make_response(redirect("/signup"))
        
        if password != confirm_password:
            flash("Passwords do not match")
            return make_response(redirect("/signup"))
        
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT username FROM users WHERE username=?', (username,))
            if cursor.fetchall():
                flash(f"Username '{username}' unavailable")
                return make_response(redirect("/signup"))
            
            hashed_password = sha256.hash(password)
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        
            session['username'] = username
            res = make_response(redirect("/"))
            return res

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if 'username' not in session:
        flash("You are not logged in")
        return make_response(redirect("/login"))

    if request.method == 'GET':
        return render_template('reset-password.html')
    
    if request.method == 'POST':
        current_password = request.form.get("current-password")
        if not current_password:
            flash("No current password provided")
            return make_response(redirect("/reset-password"))
        
        new_password = request.form.get("new-password")
        if not new_password:
            flash("No new password provided")
            return make_response(redirect("/reset-password"))
        
        confirm_new_password = request.form.get("confirm-new-password")
        if not confirm_new_password:
            flash("No confirmation new password provided")
            return make_response(redirect("/reset-password"))
        
        if new_password != confirm_new_password:
            flash("New passwords do not match")
            return make_response(redirect("/reset-password"))
        
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT password FROM users WHERE username=?', (session['username'],))
            hashed_password = cursor.fetchone()[0]
            if not sha256.verify(current_password, hashed_password):
                flash("Incorrect current password")
                return make_response(redirect("/reset-password"))
            new_hashed_password = sha256.hash(new_password)
            cursor.execute('UPDATE users SET password=? WHERE username=?', (new_hashed_password, session['username']))
            res = make_response(redirect("/account"))
            return res

@app.route('/account', methods=['GET'])
def account():
    if request.method == 'GET':
        return render_template('account.html')

if (__name__ == '__main__'):
    app.run(host="0.0.0.0", port=8000, debug=True)