from fastapi import FastAPI
from db import Base, engine
from routers import lap_summary as lap_router
from routers import users as account_router
from routers import analytics as analytics_router
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TimeSlice F1 API",
    description="""
Welcome to **TimeSlice**, a high-performance analytical engine for Formula 1 telemetry. 

This API is designed to bridge the gap between raw track data and actionable racing insights. By choosing specific data points across historical and modern sessions, TimeSlice allows you to dive deep into lap-by-lap performance, tyre degradation trends, and strategic execution.

**WARNING**: All endpoint Require a Login so please sign up first. No data after 2023 is available.

*Explore the endpoints below to start generating your own racing insights.*
    """,
    version="1.0.0",
)
app.include_router(account_router.router)
app.include_router(lap_router.router)
app.include_router(analytics_router.router)