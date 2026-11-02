// ============================================================
// Лабораторная работа 7. Neo4j + Cypher. Вариант 1: Университет
// Все данные синтетические. Выполняйте блоки по порядку в Neo4j Browser.
// ============================================================

// ---------- 0. Проверка соединения ----------
RETURN 'Neo4j works' AS status;

// ---------- 1. Ограничения уникальности ----------
CREATE CONSTRAINT student_id IF NOT EXISTS
FOR (s:Student) REQUIRE s.studentId IS UNIQUE;
CREATE CONSTRAINT teacher_id IF NOT EXISTS
FOR (t:Teacher) REQUIRE t.teacherId IS UNIQUE;
CREATE CONSTRAINT course_code IF NOT EXISTS
FOR (c:Course) REQUIRE c.code IS UNIQUE;

// ---------- 2. Узлы (16: 7 Student, 3 Teacher, 6 Course) ----------
MERGE (s:Student {studentId:1001}) SET s.name='Aruzhan', s.year=3
MERGE (s2:Student {studentId:1002}) SET s2.name='Dias', s2.year=3
MERGE (s3:Student {studentId:1003}) SET s3.name='Madina', s3.year=2
MERGE (s4:Student {studentId:1004}) SET s4.name='Timur', s4.year=4
MERGE (s5:Student {studentId:1005}) SET s5.name='Aigerim', s5.year=3
MERGE (s6:Student {studentId:1006}) SET s6.name='Nurlan', s6.year=1
MERGE (s7:Student {studentId:1007}) SET s7.name='Zhanna', s7.year=3;

MERGE (t1:Teacher {teacherId:501}) SET t1.name='A. Teacher'
MERGE (t2:Teacher {teacherId:502}) SET t2.name='B. Mentor'
MERGE (t3:Teacher {teacherId:503}) SET t3.name='C. Lecturer';

MERGE (c1:Course {code:'PROG101'})  SET c1.title='Programming Basics',        c1.credits=5
MERGE (c2:Course {code:'DS202'})    SET c2.title='Data Structures',            c2.credits=5
MERGE (c3:Course {code:'DB201'})    SET c3.title='Database Systems',           c3.credits=5
MERGE (c4:Course {code:'NOSQL301'}) SET c4.title='NoSQL Technologies',         c4.credits=5
MERGE (c5:Course {code:'ADV401'})   SET c5.title='Advanced Data Engineering',  c5.credits=6
MERGE (c6:Course {code:'CLOUD402'}) SET c6.title='Cloud Data Platforms',       c6.credits=6;

// ---------- 3. Отношения (24: 6 REQUIRES, 6 TEACHES, 12 ENROLLED_IN) ----------
// REQUIRES: (курс)-[:REQUIRES]->(пререквизит)
UNWIND [
  ['DS202','PROG101'], ['DB201','PROG101'], ['NOSQL301','DB201'],
  ['ADV401','NOSQL301'], ['ADV401','DS202'], ['CLOUD402','NOSQL301']
] AS p
MATCH (c:Course {code:p[0]}), (r:Course {code:p[1]})
MERGE (c)-[:REQUIRES]->(r);

// TEACHES: (преподаватель)-[:TEACHES]->(курс)
UNWIND [
  [501,'PROG101'], [501,'DB201'], [502,'NOSQL301'],
  [502,'ADV401'],  [503,'DS202'], [503,'CLOUD402']
] AS p
MATCH (t:Teacher {teacherId:p[0]}), (c:Course {code:p[1]})
MERGE (t)-[:TEACHES]->(c);

// ENROLLED_IN: (студент)-[:ENROLLED_IN {semester}]->(курс)
UNWIND [
  [1001,'DB201','2026-Spring'],    [1001,'NOSQL301','2026-Fall'],
  [1002,'DB201','2026-Spring'],    [1002,'NOSQL301','2026-Fall'],
  [1003,'PROG101','2026-Spring'],  [1003,'DS202','2026-Fall'],
  [1004,'NOSQL301','2026-Fall'],   [1004,'ADV401','2026-Fall'],
  [1005,'DB201','2026-Spring'],    [1005,'CLOUD402','2026-Fall'],
  [1006,'PROG101','2026-Spring'],  [1007,'NOSQL301','2026-Fall']
] AS e
MATCH (s:Student {studentId:e[0]}), (c:Course {code:e[1]})
MERGE (s)-[:ENROLLED_IN {semester:e[2]}]->(c);

// ---------- 4. Проверка структуры ----------
MATCH (n) RETURN labels(n) AS labels, count(*) AS qty ORDER BY labels;
// ожидается: Course 6, Student 7, Teacher 3
MATCH ()-[r]->() RETURN type(r) AS relation, count(*) AS qty ORDER BY relation;
// ожидается: ENROLLED_IN 12, REQUIRES 6, TEACHES 6

// ---------- 5. Запросы ----------
// Q1. Простое MATCH: все дисциплины
MATCH (c:Course) RETURN c.code, c.title ORDER BY c.code;

// Q2. Фильтрация: студенты курса NOSQL301 в семестре 2026-Fall
MATCH (s:Student)-[e:ENROLLED_IN]->(c:Course {code:'NOSQL301'})
WHERE e.semester = '2026-Fall'
RETURN s.studentId, s.name ORDER BY s.name;
// ожидается: Aruzhan, Dias, Timur, Zhanna

// Q3. Сортировка и LIMIT: 3 самых популярных курса
MATCH (:Student)-[:ENROLLED_IN]->(c:Course)
RETURN c.code, c.title, count(*) AS students
ORDER BY students DESC LIMIT 3;
// ожидается: NOSQL301 4, DB201 3, PROG101 2

// Q4. Запрос по отношению: кто преподаёт NOSQL301
MATCH (t:Teacher)-[:TEACHES]->(:Course {code:'NOSQL301'})
RETURN t.name;
// ожидается: B. Mentor

// Q5. Двухшаговый обход: студенты преподавателя 502 (через курс)
MATCH (t:Teacher {teacherId:502})-[:TEACHES]->(c:Course)<-[:ENROLLED_IN]-(s:Student)
RETURN DISTINCT s.name ORDER BY s.name;
// ожидается: Aruzhan, Dias, Timur, Zhanna

// Q6. Variable-length (глубина 1..3): пререквизиты ADV401
MATCH path = (:Course {code:'ADV401'})-[:REQUIRES*1..3]->(p:Course)
RETURN p.code, p.title, min(length(path)) AS depth
ORDER BY depth, p.code;
// ожидается: DS202 1, NOSQL301 1, DB201 2, PROG101 2

// Q7. Агрегирование: число уникальных студентов у каждого преподавателя
MATCH (t:Teacher)-[:TEACHES]->(:Course)<-[:ENROLLED_IN]-(s:Student)
RETURN t.name, count(DISTINCT s) AS students
ORDER BY students DESC;
// ожидается: A. Teacher 5, B. Mentor 4, C. Lecturer 2

// Q8 (повышенное). Все цепочки пререквизитов ADV401 до 3 уровней
MATCH path = (:Course {code:'ADV401'})-[:REQUIRES*1..3]->(:Course)
RETURN [n IN nodes(path) | n.code] AS chain, length(path) AS len
ORDER BY len, chain;
// ожидается 5 цепочек:
// [ADV401,NOSQL301], [ADV401,DS202],
// [ADV401,NOSQL301,DB201], [ADV401,DS202,PROG101],
// [ADV401,NOSQL301,DB201,PROG101]

// Q9 (повышенное). Какие курсы доступны студенту 1006 после PROG101
MATCH (:Student {studentId:1006})-[:ENROLLED_IN]->(done:Course)<-[:REQUIRES]-(next:Course)
RETURN next.code, next.title ORDER BY next.code;
// ожидается: DB201, DS202

// ---------- 6. Изменение ----------
// 6.1 свойство узла
MATCH (s:Student {studentId:1001}) SET s.name='Aruzhan S.' RETURN s.studentId, s.name;
// контроль
MATCH (s:Student {studentId:1001}) RETURN s.name;   // Aruzhan S.

// 6.2 свойство отношения
MATCH (:Student {studentId:1004})-[r:ENROLLED_IN]->(:Course {code:'ADV401'})
SET r.semester='2027-Spring' RETURN r.semester;
// контроль
MATCH (:Student {studentId:1004})-[r:ENROLLED_IN]->(:Course {code:'ADV401'})
RETURN r.semester;                                   // 2027-Spring

// ---------- 7. Безопасное удаление тестовой связи ----------
// 7.1 сначала показать
MATCH (s:Student {studentId:1007})-[r:ENROLLED_IN]->(c:Course {code:'NOSQL301'})
RETURN s, r, c;
// 7.2 удалить только отношение
MATCH (s:Student {studentId:1007})-[r:ENROLLED_IN]->(c:Course {code:'NOSQL301'})
DELETE r;
// 7.3 подтвердить отсутствие
MATCH (:Student {studentId:1007})-[r:ENROLLED_IN]->(:Course {code:'NOSQL301'})
RETURN count(r) AS remaining;                        // 0
MATCH ()-[r:ENROLLED_IN]->() RETURN count(r) AS enrolled;  // 11

// ---------- 8. Очистка (ТОЛЬКО на учебной БД!) ----------
// Сначала проверьте: MATCH (n) RETURN count(n);
// MATCH (n) DETACH DELETE n;
