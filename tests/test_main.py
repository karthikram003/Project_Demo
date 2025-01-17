import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.database import Base

# Set up test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_and_read_department():
    # Create a department
    create_response = client.post(
        "/departments/",
        json={"name": "Engineering"}
    )
    assert create_response.status_code == 200
    dept_data = create_response.json()
    assert dept_data["name"] == "Engineering"
    dept_id = dept_data["id"]

    # Read the created department
    read_response = client.get(f"/departments/{dept_id}")
    assert read_response.status_code == 200
    assert read_response.json() == dept_data

def test_create_and_read_employee():
    # Create a department first
    dept_response = client.post(
        "/departments/",
        json={"name": "IT"}
    )
    dept_id = dept_response.json()["id"]

    # Create an employee
    create_response = client.post(
        f"/departments/{dept_id}/employees/",
        json={
            "name": "John Doe",
            "experience": 5.5,
            "salary": 75000.0
        }
    )
    assert create_response.status_code == 200
    emp_data = create_response.json()
    assert emp_data["name"] == "John Doe"
    assert emp_data["experience"] == 5.5
    assert emp_data["salary"] == 75000.0
    assert emp_data["department_id"] == dept_id
    emp_id = emp_data["id"]

    # Read the created employee
    read_response = client.get(f"/employees/{emp_id}")
    assert read_response.status_code == 200
    assert read_response.json() == emp_data