from fastapi import FastAPI
from database import engine

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is working!"}

@app.get("/test-db")
def test_db():
    try:
        connection = engine.connect()
        connection.close()
        return {"status": "Database connected successfully!"}
    except Exception as e:
        return {"status": "Connection failed", "error": str(e)}