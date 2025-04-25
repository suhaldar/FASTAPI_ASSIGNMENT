import pytest
from app.models.parking import ParkingSlot, SlotStatus
from app.models.booking import Booking
from app.models.feedback import Feedback
from datetime import datetime

def test_create_feedback(client, db_session, user_token, test_user):
    # Create parking slot
    slot = ParkingSlot(label="F1", status=SlotStatus.OCCUPIED)
    db_session.add(slot)
    db_session.commit()

    # Create booking
    booking = Booking(
        user_id=test_user.id,
        slot_id=slot.id,
        status="active",
        start_time=datetime.utcnow()
    )
    db_session.add(booking)
    db_session.commit()

    # Create feedback
    response = client.post(
        "/feedback",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "booking_id": booking.id,
            "rating": 5,
            "comment": "Great parking experience!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["booking_id"] == booking.id
    assert data["rating"] == 5
    assert data["comment"] == "Great parking experience!"

def test_create_feedback_invalid_booking(client, user_token):
    # Try to create feedback for non-existent booking
    response = client.post(
        "/feedback",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "booking_id": 99999,  # Non-existent booking ID
            "rating": 5,
            "comment": "This should fail"
        }
    )
    assert response.status_code == 404

def test_create_feedback_invalid_rating(client, db_session, user_token, test_user):
    # Create parking slot
    slot = ParkingSlot(label="F2", status=SlotStatus.OCCUPIED)
    db_session.add(slot)
    db_session.commit()

    # Create booking
    booking = Booking(
        user_id=test_user.id,
        slot_id=slot.id,
        status="active",
        start_time=datetime.utcnow()
    )
    db_session.add(booking)
    db_session.commit()

    # Try to create feedback with invalid rating
    response = client.post(
        "/feedback",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "booking_id": booking.id,
            "rating": 6,  # Invalid rating (should be 1-5)
            "comment": "This should fail"
        }
    )
    assert response.status_code == 422  # Validation error

def test_get_feedback(client, db_session, user_token, test_user):
    # Create parking slot
    slot = ParkingSlot(label="F3", status=SlotStatus.OCCUPIED)
    db_session.add(slot)
    db_session.commit()

    # Create booking
    booking = Booking(
        user_id=test_user.id,
        slot_id=slot.id,
        status="active",
        start_time=datetime.utcnow()
    )
    db_session.add(booking)
    db_session.commit()

    # Create feedback
    feedback = Feedback(
        user_id=test_user.id,
        booking_id=booking.id,
        rating=4,
        comment="Good service"
    )
    db_session.add(feedback)
    db_session.commit()

    # Get feedback
    response = client.get(
        f"/feedback/{booking.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["booking_id"] == booking.id
    assert data["rating"] == 4
    assert data["comment"] == "Good service"

def test_list_user_feedback(client, db_session, user_token, test_user):
    # Create parking slot
    slot = ParkingSlot(label="F4", status=SlotStatus.OCCUPIED)
    db_session.add(slot)
    db_session.commit()

    # Create booking
    booking = Booking(
        user_id=test_user.id,
        slot_id=slot.id,
        status="active",
        start_time=datetime.utcnow()
    )
    db_session.add(booking)
    db_session.commit()

    # Create feedback
    feedback = Feedback(
        user_id=test_user.id,
        booking_id=booking.id,
        rating=5,
        comment="Excellent"
    )
    db_session.add(feedback)
    db_session.commit()

    # List feedback
    response = client.get(
        "/feedback",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(f["rating"] == 5 and f["comment"] == "Excellent" for f in data)

def test_get_nonexistent_feedback(client, user_token):
    response = client.get(
        "/feedback/99999",  # Non-existent booking ID
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 404

def test_create_feedback_unauthorized(client, db_session):
    # Try to create feedback without authentication
    response = client.post(
        "/feedback",
        json={
            "booking_id": 1,
            "rating": 5,
            "comment": "This should fail"
        }
    )
    assert response.status_code == 401  # Unauthorized 