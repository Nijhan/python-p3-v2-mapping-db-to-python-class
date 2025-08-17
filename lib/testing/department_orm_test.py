from __init__ import CONN, CURSOR
from department import Department
import pytest


class TestDepartment:
    """Tests for the Department class in department.py"""

    @pytest.fixture(autouse=True)
    def reset_db(self):
        """Drop tables and clear cache before each test."""
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CURSOR.execute("DROP TABLE IF EXISTS departments")
        Department.all = {}

    def test_creates_table(self):
        Department.create_table()
        CURSOR.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments'")
        assert CURSOR.fetchone() is not None

    def test_drops_table(self):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT
            )
        """)
        CONN.commit()

        Department.drop_table()
        CURSOR.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments'")
        assert CURSOR.fetchone() is None

    def test_saves_department(self):
        Department.create_table()
        dept = Department("Payroll", "Building A, 5th Floor")
        dept.save()

        CURSOR.execute("SELECT * FROM departments")
        row = CURSOR.fetchone()
        assert row[0] == dept.id
        assert row[1] == dept.name
        assert row[2] == dept.location

    def test_creates_department(self):
        Department.create_table()
        dept = Department.create("Payroll", "Building A, 5th Floor")

        CURSOR.execute("SELECT * FROM departments")
        row = CURSOR.fetchone()
        assert row[0] == dept.id
        assert row[1] == dept.name
        assert row[2] == dept.location

    def test_updates_row(self):
        Department.create_table()
        dept1 = Department.create("Human Resources", "Building C, East Wing")
        dept2 = Department.create("Marketing", "Building B, 3rd Floor")

        dept2.name = "Sales and Marketing"
        dept2.location = "Building B, 4th Floor"
        dept2.update()

        fetched1 = Department.find_by_id(dept1.id)
        assert fetched1.name == dept1.name
        assert fetched1.location == dept1.location

        fetched2 = Department.find_by_id(dept2.id)
        assert fetched2.name == "Sales and Marketing"
        assert fetched2.location == "Building B, 4th Floor"

    def test_deletes_row(self):
        Department.create_table()
        dept1 = Department.create("Human Resources", "Building C, East Wing")
        dept2 = Department.create("Sales and Marketing", "Building B, 4th Floor")

        dept2.delete()
        assert Department.find_by_id(dept2.id) is None
        assert dept2.id is None
        assert Department.all.get(dept2.id) is None

        fetched1 = Department.find_by_id(dept1.id)
        assert fetched1.name == dept1.name
        assert fetched1.location == dept1.location

    def test_instance_from_db(self):
        Department.create_table()
        dept = Department.create("Payroll", "Building A, 5th Floor")

        CURSOR.execute("SELECT * FROM departments")
        row = CURSOR.fetchone()
        instance = Department.instance_from_db(row)
        assert instance.id == dept.id
        assert instance.name == dept.name
        assert instance.location == dept.location

    def test_gets_all(self):
        Department.create_table()
        dept1 = Department.create("Human Resources", "Building C, East Wing")
        dept2 = Department.create("Marketing", "Building B, 3rd Floor")

        all_departments = Department.get_all()
        assert len(all_departments) == 2
        assert all_departments[0].id == dept1.id
        assert all_departments[1].id == dept2.id

    def test_finds_by_id(self):
        Department.create_table()
        dept1 = Department.create("Human Resources", "Building C, East Wing")
        dept2 = Department.create("Marketing", "Building B, 3rd Floor")

        assert Department.find_by_id(dept1.id).name == dept1.name
        assert Department.find_by_id(dept2.id).name == dept2.name
        assert Department.find_by_id(0) is None

    def test_finds_by_name(self):
        Department.create_table()
        dept1 = Department.create("Human Resources", "Building C, East Wing")
        dept2 = Department.create("Marketing", "Building B, 3rd Floor")

        assert Department.find_by_name("Human Resources").id == dept1.id
        assert Department.find_by_name("Marketing").id == dept2.id
        assert Department.find_by_name("Unknown") is None
