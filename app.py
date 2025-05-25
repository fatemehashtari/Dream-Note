from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('notes.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET'])
def index():
    search = request.args.get('search', '')
    conn = get_db_connection()
    if search:
        notes = conn.execute("SELECT * FROM notes WHERE content LIKE ?", ('%' + search + '%',)).fetchall()
    else:
        notes = conn.execute("SELECT * FROM notes").fetchall()
    conn.close()
    return render_template('index.html', notes=notes, search=search)

@app.route('/add', methods=['POST'])
def add_note():
    content = request.form.get('content')
    category = request.form.get('category', 'عمومی')
    if content:
        conn = get_db_connection()
        conn.execute("INSERT INTO notes (content, category) VALUES (?, ?)", (content, category))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    conn = get_db_connection()
    if request.method == 'POST':
        content = request.form.get('content')
        category = request.form.get('category', 'عمومی')
        conn.execute("UPDATE notes SET content = ?, category = ? WHERE id = ?", (content, category, note_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        note = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        conn.close()
        return render_template('edit.html', content=note['content'], category=note['category'])

@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
