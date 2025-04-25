from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, parking, booking, feedback

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Parking Management System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(parking.router, tags=["Parking"])
app.include_router(booking.router, tags=["Booking"])
app.include_router(feedback.router, tags=["Feedback"])

@app.get("/")
async def root():
    return {"message": "Welcome to Parking Management System API"} 