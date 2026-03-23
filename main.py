import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow INFO and WARNING logs

from fastapi import FastAPI
from api.verify import router as verify_router
from api.known_face import router as known_face_router

app = FastAPI()

app.include_router(verify_router, prefix="/api")
app.include_router(known_face_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
