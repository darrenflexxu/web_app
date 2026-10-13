from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from web_app.schemas import PostResponse, PostCreate


app = FastAPI()

templates = Jinja2Templates(directory="templates")

posts: list[dict] = [
    { "id": 1, "author":"Xudefeng", "title":"Xudefeng Title", "content":"Xudefeng's Content", "date_posted":"April 20, 2025"},
    { "id": 2, "author":"Darren", "title":"Darren Title", "content":"Darren's Content", "date_posted":"April 20, 2025"} ]


@app.get("/", include_in_schema=False)
@app.get("/posts", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", 
                                      {"posts" : posts, "title" : "Home"}) 


@app.get("/posts/{post_id}")
def post_page(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return templates.TemplateResponse(request, "post.html",
                                               {"post" : post,
                                                 "title" : post.get("title") })
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.get("/api/posts", response_model=list[PostResponse])
def get_posts():
    return posts


@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.post("/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
    new_id = max(p["id"] for p in posts) + 1 if posts else 1
    new_post = { "id": new_id, "author": post.author, "title": post.title, "content": post.content, "date_posted": "April 23, 2026"}
    posts.append(new_post)
    return new_post


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail 
        if exception.detail 
        else "An error occurred. Please check your request and try again."
        )

    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=exception.status_code, content={"detail":message},)
    return templates.TemplateResponse(request, "error.html", 
                                      {"status_code": exception.status_code, 
                                       "title": exception.status_code, 
                                       "message": message},
                                         status_code=exception.status_code)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,content={"detail": exception.errors()})
    return templates.TemplateResponse(request, "error.html", 
                                      { "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
                                       "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
                                       "message": "Invalid request. Please check your input and try again."}, 
                                       status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
