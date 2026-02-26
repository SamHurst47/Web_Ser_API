from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from db import get_db
from models import Users
from services.users import SECRET_KEY, ALGORITHM

# This tells FastAPI where clients should go to get their token (your login route!)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/accounts/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT to get the user's ID (which we stored in the "sub" claim)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Fetch the user from the database
    user = db.query(Users).filter(Users.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
        
    return user