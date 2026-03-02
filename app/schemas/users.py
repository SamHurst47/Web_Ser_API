from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="The user's unique email address")
    password: str = Field(..., min_length=8, description="Account password (minimum 8 characters)")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "lewis.hamilton@mercedes.com",
                    "password": "SuperSecretPassword123!"
                }
            ]
        }
    )

class UserRead(BaseModel):
    id: int = Field(..., description="The unique internal ID of the user")
    email: EmailStr = Field(..., description="The registered email address")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [  
                {
                    "id": 1,
                    "email": "lewis.hamilton@mercedes.com"
                }
            ]
        }
    )

class Token(BaseModel):
    access_token: str = Field(..., description="The JWT access token used for Bearer authentication")
    token_type: str = Field(..., description="The type of token (typically 'bearer')", examples=["bearer"])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [ 
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer"
                }
            ]
        }
    )