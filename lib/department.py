# department.py
from __init__ import CONN, CURSOR

class Department:
    all = {}  # Cache all instances by id

    def __init__(self, name, location, _id=None):
        self.id = _id
        self.name = name
        self.location = location

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                location TEXT
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS departments")
        CONN.commit()
        cls.all.clear()  # Clear cache when table is dropped

    def save(self):
        CURSOR.execute(
            "INSERT INTO departments (name, location) VALUES (?, ?)",
            (self.name, self.location)
        )
        CONN.commit()
        self.id = CURSOR.lastrowid
        Department.all[self.id] = self

    @classmethod
    def create(cls, name, location):
        dept = cls(name, location)
        dept.save()
        return dept

    def update(self):
        if not self.id:
            raise ValueError("Cannot update unsaved department")
        CURSOR.execute(
            "UPDATE departments SET name=?, location=? WHERE id=?",
            (self.name, self.location, self.id)
        )
        CONN.commit()
        Department.all[self.id] = self

    def delete(self):
        if self.id:
            CURSOR.execute("DELETE FROM departments WHERE id=?", (self.id,))
            CONN.commit()
            Department.all.pop(self.id, None)
            self.id = None

    @classmethod
    def instance_from_db(cls, row):
        _id, name, location = row
        dept = cls(name, location, _id)
        cls.all[_id] = dept
        return dept

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM departments")
        rows = CURSOR.fetchall()
        # Clear cache first to avoid duplicates from previous calls
        cls.all.clear()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, _id):
        if _id in cls.all:
            return cls.all[_id]
        CURSOR.execute("SELECT * FROM departments WHERE id=?", (_id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        CURSOR.execute("SELECT * FROM departments WHERE name=?", (name,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None
