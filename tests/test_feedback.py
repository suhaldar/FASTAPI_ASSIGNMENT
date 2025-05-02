import pytest
from fastapi import status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.booking import Booking
from app.models.parking import ParkingSlot
from app.models.feedback import Feedback
from app.schemas.feedback import Feedback as FeedbackSchema

def test_create_feedback_unauthorized(client):
    """Test creating feedback without authorization"""
    response = client.post("/feedback", json={
        "booking_id": 1,
        "rating": 5,
        "comment": "Great service!"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_feedback_success(client, test_user, db_session, user_token):
    """Test successful feedback creation"""
    # Create a parking slot
    slot = ParkingSlot(floor=1, label="A1", status="available")
    db_session.add(slot)
    db_session.commit()
    
    # Create a booking
    booking = Booking(
        user_id=test_user.id,
        floor_id=1,
        label_id="A1",
        status="completed"
    )
    db_session.add(booking)
    db_session.commit()
    
    # Create feedback
    response = client.post(
        "/feedback",
        json={
            "booking_id": booking.id,
            "rating": 5,
            "comment": "Great service!"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Feedback created successfully"

def test_create_feedback_admin_forbidden(client, test_admin, db_session, admin_token):
    """Test admin cannot create feedback"""
    # Create a parking slot
    slot = ParkingSlot(floor=1, label="A1", status="available")
    db_session.add(slot)
    db_session.commit()
    
    # Create a booking
    booking = Booking(
        user_id=test_admin.id,
        floor_id=1,
        label_id="A1",
        status="completed"
    )
    db_session.add(booking)
    db_session.commit()
    
    response = client.post(
        "/feedback",
        json={
            "booking_id": booking.id,
            "rating": 5,
            "comment": "Great service!"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_create_feedback_invalid_booking(client, test_user, user_token):
    """Test creating feedback for non-existent booking"""
    response = client.post(
        "/feedback",
        json={
            "booking_id": 999,
            "rating": 5,
            "comment": "Great service!"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_list_feedback_success(client, test_user, db_session, user_token):
    """Test listing feedback for a user"""
    # Create a parking slot
    slot = ParkingSlot(floor=1, label="A1", status="available")
    db_session.add(slot)
    db_session.commit()
    
    # Create a booking
    booking = Booking(
        user_id=test_user.id,
        floor_id=1,
        label_id="A1",
        status="completed"
    )
    db_session.add(booking)
    db_session.commit()
    
    # Create feedback
    feedback = Feedback(
        user_id=test_user.id,
        booking_id=booking.id,
        rating=5,
        comment="Great service!"
    )
    db_session.add(feedback)
    db_session.commit()
    
    response = client.get(
        "/feedback",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["rating"] == 5
    assert data[0]["comment"] == "Great service!"

def test_list_feedback_with_filters(client, test_user, db_session, user_token):
    """Test listing feedback with filters"""
    # Create parking slots
    slot1 = ParkingSlot(floor=1, label="A1", status="available")
    slot2 = ParkingSlot(floor=2, label="B1", status="available")
    db_session.add_all([slot1, slot2])
    db_session.commit()
    
    # Create bookings
    booking1 = Booking(
        user_id=test_user.id,
        floor_id=1,
        label_id="A1",
        status="completed"
    )
    booking2 = Booking(
        user_id=test_user.id,
        floor_id=2,
        label_id="B1",
        status="completed"
    )
    db_session.add_all([booking1, booking2])
    db_session.commit()
    
    # Create feedback
    feedback1 = Feedback(
        user_id=test_user.id,
        booking_id=booking1.id,
        rating=5,
        comment="Great service!"
    )
    feedback2 = Feedback(
        user_id=test_user.id,
        booking_id=booking2.id,
        rating=4,
        comment="Good service!"
    )
    db_session.add_all([feedback1, feedback2])
    db_session.commit()
    
    # Test floor filter
    response = client.get(
        "/feedback?floor=1",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["rating"] == 5
    
    # Test label filter
    response = client.get(
        "/feedback?label=B1",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["rating"] == 4

def test_manage_feedback_admin(client, test_admin, db_session, admin_token):
    """Test admin managing feedback"""
    # Create a parking slot
    slot = ParkingSlot(floor=1, label="A1", status="available")
    db_session.add(slot)
    db_session.commit()
    
    # Create a booking
    booking = Booking(
        user_id=test_admin.id,
        floor_id=1,
        label_id="A1",
        status="completed"
    )
    db_session.add(booking)
    db_session.commit()
    
    # Create feedback
    feedback = Feedback(
        user_id=test_admin.id,
        booking_id=booking.id,
        rating=5,
        comment="Great service!"
    )
    db_session.add(feedback)
    db_session.commit()
    
    response = client.get(
        "/feedback/manage",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["rating"] == 5

def test_manage_feedback_user_forbidden(client, test_user, user_token):
    """Test user cannot access manage feedback endpoint"""
    response = client.get(
        "/feedback/manage",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN 