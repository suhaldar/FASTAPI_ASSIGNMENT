import pytest
from app.models.parking import ParkingSlot, SlotStatus
from app.models.booking import Booking

def test_create_booking(client, db_session, user_token):
    # Create available parking slot
    slot = ParkingSlot(label="A1", status=SlotStatus.FREE)
    db_session.add(slot)
    db_session.commit()

    response = client.post(
        "/bookings",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "slot_id": slot.id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["slot_id"] == slot.id
    assert data["status"] == "active"

def test_list_bookings(client, db_session, user_token, test_user):
    # Create parking slot and booking
    slot = ParkingSlot(label="A1", status=SlotStatus.OCCUPIED)
    db_session.add(slot)
    booking = Booking(user_id=test_user.id, slot_id=slot.id, status="active")
    db_session.add(booking)
    db_session.commit()

    response = client.get(
        "/bookings",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["slot_id"] == slot.id 