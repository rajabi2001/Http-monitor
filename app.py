from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import jwt
import uvicorn


app = FastAPI()


@app.post("/login")
async def login():
    return "login"


@app.post('/register')
def register():
    return "register"


if __name__ == "__main__":
    uvicorn.run("test_fastapi:app", port=5000, log_level="info", reload=True)
