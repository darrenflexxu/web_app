from fastapi import FastAPI
from fastapi.responses import HTMLResponse 

app = FastAPI()

posts: list[dict] = [
    { "id": 1, "author":"Xudefeng", "title":"Test Title", "content":"", "date_posted":"April 20, 2025"},
    { "id": 2, "author":"Darren", "title":"Test Title", "content":"", "date_posted":"April 20, 2025"} ]

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/posts", response_class=HTMLResponse, include_in_schema=False)
def home():
    return f"<h1>{posts[0]['title']}</h1>" 

@app.get("/api/posts")
def get_posts():
    return posts