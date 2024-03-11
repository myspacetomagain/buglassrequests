import sqlite3
from flask import Flask, render_template, request, redirect, g

DATABASE = 'database.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This enables column access by name: row['column_name']
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      type TEXT NOT NULL,
                      content TEXT NOT NULL,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                    )''')
    conn.commit()
    conn.close()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        feedback_type = request.form['type']
        content = request.form['content']
        conn = get_db_connection()
        conn.execute('INSERT INTO feedback (type, content) VALUES (?, ?)', (feedback_type, content))
        conn.commit()
        conn.close()
        return redirect('/thankyou')
    return render_template('feedback.html')


@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')


# this will close the db connection once the form has been submitted
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# used for dropping the table is it fucks up
def drop_feedback_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS feedback')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
