PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS student;
CREATE TABLE student (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    name VARCHAR (32)
);

DROP TABLE IF EXISTS category;
CREATE TABLE category (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    name VARCHAR (32),
    parent_id INTEGER DEFAULT 0,
    FOREIGN KEY (parent_id) REFERENCES category(id)
);

DROP TABLE IF EXISTS course;
CREATE TABLE course (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    name VARCHAR (32),
    category_id INTEGER DEFAULT 0,
    cType TEXT CHECK(cType IN ('record','interactive') )  NOT NULL DEFAULT 'record',
    FOREIGN KEY (category_id) REFERENCES category(id)
);

DROP TABLE IF EXISTS student_courses;
CREATE TABLE student_courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    student_id INTEGR NOT NULL,
    course_id INTEGER NOT NULL,
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (student_id) REFERENCES student(id)
);
CREATE UNIQUE INDEX IF NOT EXISTS unique_index ON student_courses ('student_id', 'course_id');

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
