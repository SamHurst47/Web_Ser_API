from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from db import get_db
from models import Users
from schemas.users import UserCreate, UserRead, Token
from services.users import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from services.dependencies import get_current_user 

router = APIRouter(prefix="/api/v1/accounts", tags=["Account Management"])

@router.post(
    "/register", 
    response_model=UserRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Register a New User",
    description="""
Creates a new user account in the system. 
The password will be securely hashed before being stored in the database. 
Once registered, the user can use their credentials to obtain a JWT access token.
    """
)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(Users).filter(Users.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="An account with this email already exists."
        )
    
    hashed_password = get_password_hash(user_in.password)
    new_user = Users(email=user_in.email, hashed_password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post(
    "/login", 
    response_model=Token,
    summary="User Login / Token Generation",
    description="""
Authenticates a user using their email (username) and password. 
Upon success, returns a **JWT Bearer Token** which must be included in the header of all protected requests.
    """
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # form_data.username is treated as the email in this implementation
    user = db.query(Users).filter(Users.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.delete(
    "", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Account",
    description="""
Permanently deletes the currently authenticated user account. 
**Warning:** This action is irreversible and will cascade to delete all associated lap summaries and curated data.
    """
)
def delete_user_account(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    db.delete(current_user)
    db.commit()
    return None