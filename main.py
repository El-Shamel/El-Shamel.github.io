from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "Hello, You See Api Mohamed Helal!",
        "infoapi":"new applcition"
        }
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}



if __name__ =="__main__":
    uvicorn.run("main:app",host="0.0.0.0",port="8080",reload=True)
