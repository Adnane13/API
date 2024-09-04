from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "hey"}

@app.post("/te")
def testpost( msg : str):
    return {" you said " : msg}
