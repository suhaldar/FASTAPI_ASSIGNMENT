import pytest
from app.models.parking import ParkingSlot, SlotStatus

def test_create_parking_slot(client, admin_token):
    response = client.post(
        "/parking-slots",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "label": "A1",
            "status": "free"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "A1"
    assert data["status"] == "free"

def test_list_parking_slots(client, db_session, user_token):
    # Create test parking slots
    slots = [
        ParkingSlot(label="A1", status=SlotStatus 