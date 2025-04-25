# Parking Management System API

A FastAPI-based RESTful API for managing parking slots, bookings, and user feedback.

## Features

- JWT-based authentication
- Role-based access control (Admin/User)
- Parking slot management
- Booking system
- User feedback collection
- Administrative tools for bulk operations
- Maintenance mode for parking slots

## Tech Stack

- Python 3.8+
- FastAPI
- SQLAlchemy (SQLite database)
- Pydantic
- JWT for authentication
- Pytest for testing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/suhaldar/FASTAPI_ASSIGNMENT.git
cd FASTAPI_ASSIGNMENT
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the server:
```bash
uvicorn app.main:app --reload
```

2. Access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- POST `/register` - Register a new user
- POST `/token` - Login and get access token
- GET `/users/me` - Get current user information

### Parking Slots
- GET `/parking-slots` - List all parking slots
- POST `/parking-slots` - Create a new parking slot (Admin only)
- PUT `/parking-slots/{slot_id}` - Update a parking slot (Admin only)
- DELETE `/parking-slots/{slot_id}` - Delete a parking slot (Admin only)
- POST `/parking-slots/bulk` - Bulk create parking slots (Admin only)
- PUT `/parking-slots/{slot_id}/maintenance` - Set maintenance mode (Admin only)

### Bookings
- POST `/bookings` - Create a new booking
- GET `/bookings` - List user's bookings
- PUT `/bookings/{booking_id}/cancel` - Cancel a booking

### Feedback
- POST `/feedback` - Submit feedback for a booking
- GET `/feedback` - List user's feedback
- GET `/feedback/{booking_id}` - Get feedback for a specific booking

## Testing

Run the tests using pytest:
```bash
# Install pytest and pytest-cov if not already installed
pip install pytest pytest-cov

# Run tests with coverage report
pytest --cov=app tests/
```

## Project Structure 