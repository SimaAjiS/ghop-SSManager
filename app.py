import uvicorn


if __name__ == "__main__":
    # Run the application using uvicorn
    # "app:app" tells uvicorn to look for the 'app' object in this file (app.py)
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
