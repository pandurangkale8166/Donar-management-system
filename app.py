from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret_key"

DB_NAME = "donor.db"

# Database connection
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize DB
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS donors(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            blood_group TEXT NOT NULL,
            contact TEXT NOT NULL,
            donation_date TEXT NOT NULL,
            city TEXT NOT NULL
        )
    ''')
    # Create default user
    c.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'admin123')")
    conn.commit()
    conn.close()

init_db()

# ----------------- Login -----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = username
            flash("Login Successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password!", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

# ----------------- Logout -----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

# ----------------- Home -----------------
@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['user'])

# ----------------- Add Donor -----------------
@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        blood_group = request.form['blood_group']
        contact = request.form['contact']
        donation_date = request.form['donation_date']
        city = request.form['city']
        if not name or not age or not blood_group or not contact or not donation_date or not city:
            flash("All fields are required!", "error")
        else:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO donors (name, age, blood_group, contact, donation_date, city) VALUES (?, ?, ?, ?, ?, ?)",
                      (name, age, blood_group, contact, donation_date, city))
            conn.commit()
            conn.close()
            flash("Donor Added Successfully!", "success")
            return redirect(url_for('show'))
    return render_template('add.html')

# ----------------- Show Donors -----------------
@app.route('/show')
def show():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM donors")
    donors = c.fetchall()
    conn.close()
    return render_template('show.html', donors=donors)

# ----------------- Update Donor -----------------
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM donors WHERE id=?", (id,))
    donor = c.fetchone()
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        blood_group = request.form['blood_group']
        contact = request.form['contact']
        donation_date = request.form['donation_date']
        city = request.form['city']
        if not name or not age or not blood_group or not contact or not donation_date or not city:
            flash("All fields are required!", "error")
        else:
            c.execute("UPDATE donors SET name=?, age=?, blood_group=?, contact=?, donation_date=?, city=? WHERE id=?",
                      (name, age, blood_group, contact, donation_date, city, id))
            conn.commit()
            conn.close()
            flash("Donor Updated Successfully!", "success")
            return redirect(url_for('show'))
    conn.close()
    return render_template('update.html', donor=donor)

# ----------------- Delete Donor -----------------
@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM donors WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Donor Deleted Successfully!", "success")
    return redirect(url_for('show'))

# ----------------- Search Donor -----------------
@app.route('/search', methods=['GET','POST'])
def search():
    donors = []
    keyword = None
    if request.method == 'POST':
        keyword = request.form['keyword']
        conn = get_db_connection()
        c = conn.cursor()
        query = """
        SELECT * FROM donors
        WHERE name LIKE ? OR blood_group LIKE ? OR city LIKE ? OR donation_date LIKE ?
        """
        c.execute(query, ('%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%'))
        donors = c.fetchall()
        conn.close()
    
    return render_template('search.html', donors=donors, keyword=keyword)


# ----------------- Run App -----------------
if __name__ == '__main__':
    app.run(debug=True)
