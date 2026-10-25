from fastapi import FastAPI,HTTPException,Path, Query
import json

app = FastAPI()

"""
HTTP Methods:
- GET: Retrieve data
- POST: Create new data
- PUT: Update existing data
- DELETE: Remove data
"""

@app.get("/")
def greet():
    return{
        'message': 'Welcome to the FastAPI application!'
    }

@app.get("/hello")
def say_hello(name: str = "i am subhasish"):
    return {
        'message': f'Hello, {name}!'
    }

# loadind adta from json file
def get_data():
    with open('students.json', 'r') as f:
        return json.load(f)

@app.get("/students")
def student():
    return get_data()

# Path parameter & Path  try: S009
@app.get("/student/{student_id}")
def get_id(student_id: str = Path(...,description="The ID of the student to retrieve", example="S001")):
    data  = get_data()
    if student_id not in data:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    return data[student_id]

# Query parameter [use '?']
"""
http://127.0.0.1:8000/filter?course=python
"""

@app.get("/filter")
def filter_students(course: str | None = Query(None,description="Filter students by course", example="python")):
    data = get_data()

    if course is None:
        return data

    filtered = {}

    for student_id, info in data.items():
        if info["course"].lower() == course.lower():
            filtered[student_id] = info
    return filtered
# http://127.0.0.1:8000/filter?course=python check this url in browser to see the output

# http://127.0.0.1:8000/sort?sort_by = mark,age,name&order=asc,desc
# http://127.0.0.1:8000/sort?sort_by=marks&order=asc  check it

SORT_ORDER = ["asc", "desc"]


@app.get("/sort")
def sort_students(
    sort_by: str = Query(
        ...,
        description="Sort students by field",
        examples=["marks"]
    ),
    order: str = Query(
        "asc",
        description="Order of sorting (asc or desc)"
    )
):
    data = get_data()

    # Validate the sort field
    if sort_by not in ["marks", "age", "name"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort field. Must be 'marks', 'age', or 'name'."
        )

    # Validate the sorting order
    if order not in SORT_ORDER:
        raise HTTPException(
            status_code=400,
            detail="Invalid order. Must be 'asc' or 'desc'."
        )

    students = []

    for student_id, info in data.items():
        student = {**info, "id": student_id}
        students.append(student)

    reverse = order == "desc"

    sorted_students = sorted(
        students,
        key=lambda x: x[sort_by],
        reverse=reverse
    )

    return sorted_students

# pagination -> page and limit use which page and how many data you want to see in one page
# see the url in browser http://127.0.0.1:8000/pagination?page=2&limit=3
@app.get("/pagination")
def paginate_students(
    page: int = Query(1, description="Page number",ge=1),
    limit: int = Query(10, description="Number of students per page", ge=1)
):
    data = get_data()
    student =[]
    for student_id, info in data.items():
        info["id"] = student_id
        student.append(info)

    start = (page - 1) * limit
    end = start + limit

    page_students = student[start:end]
    return {
        "page": page,
        "limit": limit,
        "total_students": len(student),
        "students": page_students
    }

# Pydantic

