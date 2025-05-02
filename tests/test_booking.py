import pytest
from fastapi import status
from datetime import datetime
from app.models.parking import ParkingSlot
from app.models.booking import Booking
from app.schemas.parking import SlotStatus

def test_list_bookings_unauthorized(client):
    """Test listing bookings without authorization."""
    response = client.get("/bookings")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 

def test_create_booking_success(client, db_session, user_token):
    """Test successful booking creation"""
    # Create an available parking slot
    slot = ParkingSlot(floor=1, label="A1", status="free")
    db_session.add(slot)
    db_session.commit()

    response = client.post(
        "/bookings",
        json={
            "floor_id": 1,
            "label_id": "A1"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "Booking created successfully" in response.json()["message"]

    # Verify slot status was updated
    updated_slot = db_session.query(ParkingSlot).filter_by(floor=1, label="A1").first()
    assert updated_slot.status == "occupied"

def test_create_booking_admin_forbidden(client, db_session, admin_token):
    """Test that admins cannot create bookings"""
    # Create an available parking slot
    slot = ParkingSlot(floor=1, label="A1", status="free")
    db_session.add(slot)
    db_session.commit()

    response = client.post(
        "/bookings",
        json={
            "floor_id": 1,
            "label_id": "A1"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Admins cannot create bookings" in response.json()["detail"]

def test_create_booking_nonexistent_slot(client, user_token):
    """Test booking a non-existent parking slot"""
    response = client.post(
        "/bookings",
        json={
            "floor_id": 999,
            "label_id": "XX"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Parking slot not found" in response.json()["detail"]

def test_create_booking_occupied_slot(client, db_session, user_token):
    """Test booking an occupied parking slot"""
    # Create an occupied parking slot
    slot = ParkingSlot(floor=1, label="A1", status="occupied")
    db_session.add(slot)
    db_session.commit()

    response = client.post(
        "/bookings",
        json={
            "floor_id": 1,
            "label_id": "A1"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Parking slot is not available" in response.json()["detail"]

def test_list_bookings_user(client, db_session, user_token, test_user):
    """Test listing user's bookings"""
    # Create a booking for the user
    slot = ParkingSlot(floor=1, label="A1", status="occupied")
    booking = Booking(
        user_id=test_user.id,
        floor_id=1,
        label_id="A1",
        status="active"
    )
    db_session.add(slot)
    db_session.add(booking)
    db_session.commit()

    response = client.get(
        "/bookings",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert str(data[0]["floor_id"]) == "1"  # Compare as strings
    assert data[0]["label_id"] == "A1"
    assert data[0]["status"] == "active"

def test_list_bookings_admin(client, db_session, admin_token, test_user):
    """Test listing all bookings as admin"""
    # Create bookings for different users
    slot1 = ParkingSlot(floor=1, label="A1", status="occupied")
    slot2 = ParkingSlot(floor=1, label="A2", status="occupied")
    booking1 = Booking(user_id=test_user.id, floor_id=1, label_id="A1", status="active")
    booking2 = Booking(user_id=test_user.id, floor_id=1, label_id="A2", status="active")
    
    db_session.add_all([slot1, slot2, booking1, booking2])
    db_session.commit()

    response = client.get(
        "/bookings",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2

def test_list_bookings_empty(client, user_token):
    """Test listing bookings when none exist"""
    response = client.get(
        "/bookings",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "No bookings found" in response.json()["detail"]

def test_cancel_booking_success(client, db_session, user_token, test_user):
    """Test successful booking cancellation"""
    # Create an active booking
    slot = ParkingSlot(floor=1, label="A1", status="occupied")
    booking = Booking(
        user_id=test_user.id,
        floor_id=1,
        label_id="A1",
        status="active"
    )
    db_session.add(slot)
    db_session.add(booking)
    db_session.commit()

    response = client.put(
        f"/bookings/{booking.id}/cancel",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "Booking cancelled successfully" in response.json()["message"]

    # Verify booking and slot status were updated
    updated_booking = db_session.query(Booking).filter_by(id=booking.id).first()
    updated_slot = db_session.query(ParkingSlot).filter_by(floor=1, label="A1").first()
    assert updated_booking.status == "cancelled"
    assert updated_slot.status == "free"
    assert updated_booking.end_time is not None

def test_cancel_booking_not_found(client, user_token):
    """Test cancelling non-existent booking"""
    response = client.put(
        "/bookings/999/cancel",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Booking not found" in response.json()["detail"]

def test_cancel_others_booking(client, db_session, user_token, test_admin):
    """Test cancelling someone else's booking"""
    # Create a booking for admin
    slot = ParkingSlot(floor=1, label="A1", status="occupied")
    booking = Booking(
        user_id=test_admin.id,  # Different user's booking
        floor_id=1,
        label_id="A1",
        status="active"
    )
    db_session.add(slot)
    db_session.add(booking)
    db_session.commit()

    response = client.put(
        f"/bookings/{booking.id}/cancel",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Not authorized to cancel this booking" in response.json()["detail"]

def test_cancel_inactive_booking(client, db_session, user_token, test_user):
    """Test cancelling an already cancelled booking"""
    # Create a cancelled booking
    slot = ParkingSlot(floor=1, label="A1", status="free")
    booking = Booking(
        user_id=test_user.id,
        floor_id=1,
        label_id="A1",
        status="cancelled",
        end_time=datetime.utcnow()
    )
    db_session.add(slot)
    db_session.add(booking)
    db_session.commit()

    response = client.put(
        f"/bookings/{booking.id}/cancel",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Booking is not active" in response.json()["detail"]

def test_admin_cancel_any_booking(client, db_session, admin_token, test_user):
    """Test admin cancelling any user's booking"""
    # Create a booking for regular user
    slot = ParkingSlot(floor=1, label="A1", status="occupied")
    booking = Booking(
        user_id=test_user.id,
        floor_id=1,
        label_id="A1",
        status="active"
    )
    db_session.add(slot)
    db_session.add(booking)
    db_session.commit()

    response = client.put(
        f"/bookings/{booking.id}/cancel",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "Booking cancelled successfully" in response.json()["message"]

def test_unauthorized_access(client):
    """Test unauthorized access to booking endpoints"""
    response = client.post("/bookings", json={
        "floor_id": 1,
        "label_id": "A1",
        "start_time": "2024-01-01T10:00:00",
        "end_time": "2024-01-01T12:00:00"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 