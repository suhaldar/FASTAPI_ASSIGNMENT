# Parking Management System API

A FastAPI-based RESTful API for managing parking slots, bookings, and user feedback.

## Features

- 🔐 JWT-based authentication with role-based access control (Admin/User)
- 🅿️ Comprehensive parking slot management
  - Create, update, and delete parking slots
  - Bulk operations for efficient management
  - Maintenance mode for parking slots
- 📅 Advanced booking system
  - Real-time slot availability
  - Booking creation and cancellation
  - User-specific booking history
- 💬 Feedback system
  - Submit and view feedback
  - Rating system
  - Admin feedback management
- 📊 Administrative tools
  - Bulk operations
  - User management
  - System monitoring

## Tech Stack

- 🐍 Python 3.8+
- ⚡ FastAPI - High-performance web framework
- 🗄️ SQLAlchemy - SQL toolkit and ORM
- 📦 Pydantic - Data validation
- 🔑 JWT - Secure authentication
- 🧪 Pytest - Testing framework
- 📊 SQLite - Lightweight database

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

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /register` - Register a new user
- `POST /token` - Login and get access token
- `GET /users/me` - Get current user information

### Parking Slots
- `GET /parking-slots` - List all parking slots
- `POST /parking-slots` - Create a new parking slot (Admin only)
- `PUT /parking-slots/{slot_id}` - Update a parking slot (Admin only)
- `DELETE /parking-slots/{slot_id}` - Delete a parking slot (Admin only)
- `POST /parking-slots/bulk` - Bulk create parking slots (Admin only)
- `PUT /parking-slots/{slot_id}/maintenance` - Set maintenance mode (Admin only)

### Bookings
- `POST /bookings` - Create a new booking
- `GET /bookings` - List user's bookings
- `PUT /bookings/{booking_id}/cancel` - Cancel a booking

### Feedback
- `POST /feedback` - Submit feedback for a booking
- `GET /feedback` - List user's feedback
- `GET /feedback/{booking_id}` - Get feedback for a specific booking

## Testing

Run the tests using pytest:
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests with coverage report
pytest --cov=app tests/
```

## Project Structure

```
FASTAPI_ASSIGNMENT/
├── app/
│   ├── models/          # Database models
│   ├── routers/         # API endpoints
│   ├── schemas/         # Pydantic models
│   ├── utils/           # Utility functions
│   ├── database.py      # Database configuration
│   └── main.py          # Application entry point
├── tests/               # Test files
├── requirements.txt     # Production dependencies
├── requirements-test.txt # Test dependencies
└── README.md           # Project documentation
```

## Code Coverage

Current code coverage:
- Overall: 87%
- Models: 100%
- Routers: 
  - Booking: 100%
  - Parking: 99%
  - Feedback: 86%
  - Auth: 37%
- Schemas: 70-100%

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 