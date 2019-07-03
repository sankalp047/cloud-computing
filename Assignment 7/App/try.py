CREATE TABLE enrollment (
    id int(10) PRIMARY KEY AUTO_INCREMENT,
    course_num int(10),
    student_id int(10),
    section_num int(10)
)

# My courses
SELECT * FROM classes as c
LEFT OUTER JOIN enrollment as e ON c.course = e.course_num AND c.section = e.section_num
WHERE e.student_id = 10012

# My details
SELECT * FROM students WHERE IdNum = 10012