from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "Textile Waste Platform API Running"
    }