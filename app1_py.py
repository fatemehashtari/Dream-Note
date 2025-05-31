from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_path():
    return os.path.join(os.path.dirname(__file__), 'notes.db')

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    search = request.args.get('search', '')
    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.cursor()
        if search:
            cursor.execute("SELECT * FROM notes WHERE user_id=? AND content LIKE ?", (session['user_id'], f'%{search}%',))
        else:
            cursor.execute("SELECT * FROM notes WHERE user_id=?", (session['user_id'],))
        notes = cursor.fetchall()
    return render_template('index.html', notes=notes, search=search)

@app.route('/add', methods=['POST'])
def add_note():
    content = request.form['content']
    category = request.form.get('category', 'عمومی')
    if 'user_id' in session and content:
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (user_id, content, category) VALUES (?, ?, ?)",
                           (session['user_id'], content, category))
            conn.commit()
    return redirect('/')

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    if 'user_id' not in session:
        return redirect('/login')
    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            content = request.form['content']
            category = request.form.get('category', 'عمومی')
            cursor.execute("UPDATE notes SET content=?, category=? WHERE id=? AND user_id=?",
                           (content, category, note_id, session['user_id']))
            conn.commit()
            return redirect('/')
        else:
            cursor.execute("SELECT content, category FROM notes WHERE id=? AND user_id=?", (note_id, session['user_id']))
            note = cursor.fetchone()
    if note:
        return render_template('edit.html', content=note[0], category=note[1])
    return redirect('/')

@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    if 'user_id' in session:
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id=? AND user_id=?", (note_id, session['user_id']))
            conn.commit()
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                return redirect('/')
            else:
                error = "نام کاربری یا رمز عبور اشتباه است."
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                conn.commit()
                return redirect('/login')
            except sqlite3.IntegrityError:
                error = "این نام کاربری قبلاً ثبت شده است."
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
