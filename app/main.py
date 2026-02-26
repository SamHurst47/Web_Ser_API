from fastapi import FastAPI
from db import Base, engine
from routers import lap_summary as lap_router
from routers import users as account_router
Base.metadata.create_all(bind=engine)

app = FastAPI(title="F1 Lap Summary API")
app.include_router(lap_router.router)
app.include_router(account_router.router)
