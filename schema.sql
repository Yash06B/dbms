DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS sports;

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_no TEXT UNIQUE NOT NULL,
    grade TEXT
);

CREATE TABLE sports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    coach TEXT,
    description TEXT,
    image_url TEXT
);

CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    sport_id INTEGER NOT NULL,
    date_enrolled DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (sport_id) REFERENCES sports (id),
    UNIQUE(student_id, sport_id)
);
