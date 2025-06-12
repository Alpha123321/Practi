from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Test API"}

@app.get("/docs")
async def swagger_redirect():
    return {"message": "Swagger UI should be at /docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)