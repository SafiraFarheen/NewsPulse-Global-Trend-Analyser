from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import auth, schemas, news_backend.models as models
from database import Base, engine, get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from auth import SECRET_KEY, ALGORITHM, verify_password, create_access_token, hash_password
from news_backend.models import User, NewsBase
from news_backend.news_fetcher import get_combined_news, save_news_to_db
from text_preprocessor import preprocess_query
from datetime import timedelta, datetime
import requests
from dotenv import load_dotenv
import os


load_dotenv()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = auth.hash_password(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/protected")
def protected_route(payload: dict = Depends(verify_token)):
    return {"message": f"Hello, {payload['sub']}! You accessed a protected route."}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/users/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"user": current_user}

def save_article(db: Session, article):
    existing = db.query(NewsBase).filter(NewsBase.url == article["url"]).first()
    if existing:
        return
    news = NewsBase(
        title=article.get("title"),
        source=article.get("source", {}).get("name", "Unknown"),
        publishedAt=datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00")),
        url=article.get("url"),
        description=article.get("description")
    )
    db.add(news)
    db.commit()
    db.refresh(news)

@app.get("/news")
def get_news(query: str = "technology", db: Session = Depends(get_db)):
    processed_query = preprocess_query(query)
    articles = get_combined_news(processed_query)
    save_news_to_db(db, articles)
    return {"original_query": query, "processed_query": processed_query, "articles": articles}

@app.get("/news_stored")
def get_stored_news(db: Session = Depends(get_db)):
    return db.query(NewsBase).all()
