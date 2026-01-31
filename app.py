import os
from flask import Flask, render_template, request, url_for, redirect, flash
from db import init_app, get_db

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'sports_management.db'),
)

try:
    os.makedirs(app.instance_path)
except OSError:
    pass

init_app(app)

# --- USER ROUTES ---

@app.route('/')
def index():
    """User Homepage: Gallery of Sports"""
    db = get_db()
    sports = db.execute('SELECT * FROM sports').fetchall()
    return render_template('index.html', sports=sports)

@app.route('/join/<int:sport_id>', methods=('GET', 'POST'))
def join_sport(sport_id):
    """User Action: Join a specific sport"""
    db = get_db()
    sport = db.execute('SELECT * FROM sports WHERE id = ?', (sport_id,)).fetchone()
    
    if request.method == 'POST':
        # Simple student registration + enrollment flow for better UX
        name = request.form['name']
        roll_no = request.form['roll_no']
        grade = request.form['grade']
        
        try:
            # 1. Check if student exists or create new
            student = db.execute('SELECT id FROM students WHERE roll_no = ?', (roll_no,)).fetchone()
            
            if student is None:
                cursor = db.execute('INSERT INTO students (name, roll_no, grade) VALUES (?, ?, ?)',
                                  (name, roll_no, grade))
                student_id = cursor.lastrowid
            else:
                student_id = student['id']

            # 2. Enroll
            db.execute('INSERT INTO enrollments (student_id, sport_id) VALUES (?, ?)',
                      (student_id, sport_id))
            db.commit()
            flash(f"Successfully joined {sport['name']}!")
            return redirect(url_for('index'))
            
        except db.IntegrityError:
            flash(f"You are already enrolled in {sport['name']}!")
            return redirect(url_for('index'))

    return render_template('join_sport.html', sport=sport)


@app.route('/my-bookings', methods=('GET', 'POST'))
def my_bookings():
    """Student Dashboard: Check enrollments by Roll No"""
    bookings = None
    student = None
    
    if request.method == 'POST':
        roll_no = request.form['roll_no']
        db = get_db()
        student = db.execute('SELECT * FROM students WHERE roll_no = ?', (roll_no,)).fetchone()
        
        if student:
            bookings = db.execute('''
                SELECT s.name as sport_name, s.coach, s.image_url, e.date_enrolled
                FROM enrollments e
                JOIN sports s ON e.sport_id = s.id
                WHERE e.student_id = ?
            ''', (student['id'],)).fetchall()
        else:
            flash(f"No student found with Roll No {roll_no}")

    return render_template('my_bookings.html', bookings=bookings, student=student)


# --- ADMIN ROUTES ---

@app.route('/admin')
def admin_dashboard():
    """Admin Dashboard: Overview"""
    db = get_db()
    student_count = db.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    sport_count = db.execute('SELECT COUNT(*) FROM sports').fetchone()[0]
    enrollment_count = db.execute('SELECT COUNT(*) FROM enrollments').fetchone()[0]
    return render_template('admin_dashboard.html', 
                         student_count=student_count, 
                         sport_count=sport_count, 
                         enrollment_count=enrollment_count)

@app.route('/admin/students')
def admin_students():
    db = get_db()
    students = db.execute('SELECT * FROM students').fetchall()
    return render_template('students.html', students=students)

@app.route('/admin/sports')
def admin_sports():
    db = get_db()
    sports = db.execute('SELECT * FROM sports').fetchall()
    return render_template('sports.html', sports=sports)

@app.route('/admin/sports/add', methods=('GET', 'POST'))
def add_sport():
    if request.method == 'POST':
        name = request.form['name']
        coach = request.form['coach']
        description = request.form['description']
        image_url = request.form['image_url']
        
        db = get_db()
        try:
            db.execute(
                'INSERT INTO sports (name, coach, description, image_url) VALUES (?, ?, ?, ?)',
                (name, coach, description, image_url)
            )
            db.commit()
            return redirect(url_for('admin_sports'))
        except db.IntegrityError:
            flash(f"Sport {name} already exists.")

    return render_template('add_sport.html')

@app.route('/admin/enrollments', methods=('GET', 'POST'))
def admin_enrollments():
    db = get_db()
    if request.method == 'POST':
        # Admin can manually enroll existing students
        student_id = request.form['student_id']
        sport_id = request.form['sport_id']
        try:
            db.execute(
                'INSERT INTO enrollments (student_id, sport_id) VALUES (?, ?)',
                (student_id, sport_id)
            )
            db.commit()
        except db.IntegrityError:
            flash("Student is already enrolled in this sport.")
        return redirect(url_for('admin_enrollments'))

    students = db.execute('SELECT * FROM students').fetchall()
    sports = db.execute('SELECT * FROM sports').fetchall()
    enrollments = db.execute('''
        SELECT e.id, s.name as student_name, sp.name as sport_name, e.date_enrolled
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN sports sp ON e.sport_id = sp.id
    ''').fetchall()
    return render_template('enroll.html', students=students, sports=sports, enrollments=enrollments)

@app.route('/admin/enrollments/delete/<int:id>', methods=('POST',))
def delete_enrollment(id):
    db = get_db()
    db.execute('DELETE FROM enrollments WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('admin_enrollments'))

if __name__ == '__main__':
    app.run(debug=True)
