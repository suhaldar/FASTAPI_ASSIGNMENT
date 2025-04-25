import pytest
from app.models.parking import ParkingSlot, SlotStatus
from fastapi import status

def test_create_parking_slot(client, admin_token):
    """Test creating a new parking slot."""
    response = client.post(
        "/parking-slots",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "label": "A1",
            "status": "free"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["label"] == "A1"
    assert data["status"] == "free"

def test_list_parking_slots(client, db_session, user_token):
    """Test listing all parking slots."""
    # Create test parking slots
    slots = [
        ParkingSlot(label="A2", status=SlotStatus.FREE),
        ParkingSlot(label="A3", status=SlotStatus.FREE)
    ]
    for slot in slots:
        db_session.add(slot)
    db_session.commit()

    response = client.get(
        "/parking-slots",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["label"] == "A2"
    assert data[1]["label"] == "A3"

def test_update_nonexistent_parking_slot(client, admin_token):
    """Test updating non-existent parking slot."""
    response = client.put(
        "/parking-slots/999",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "label": "P999",
            "status": "free"
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_nonexistent_parking_slot(client, admin_token):
    """Test deleting non-existent parking slot."""
    response = client.delete(
        "/parking-slots/999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_parking_slot_invalid_status(client, admin_token):
    """Test creating parking slot with invalid status."""
    response = client.post(
        "/parking-slots",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "label": "P1",
            "status": "invalid_status"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_bulk_create_parking_slots(client, admin_token):
    """Test bulk creation of parking slots."""
    response = client.post(
        "/parking-slots/bulk",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=[
            {"label": "B1", "status": "free"},
            {"label": "B2", "status": "free"}
        ]
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["label"] == "B1"
    assert data[1]["label"] == "B2"

def test_bulk_create_parking_slots_duplicate_labels(client, admin_token):
    """Test bulk creation with duplicate labels."""
    response = client.post(
        "/parking-slots/bulk",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=[
            {"label": "B3", "status": "free"},
            {"label": "B3", "status": "free"}  # Duplicate label
        ]
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_create_parking_slot_unauthorized(client, user_token):
    """Test creating parking slot without admin privileges."""
    response = client.post(
        "/parking-slots",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "label": "P2",
            "status": "free"
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_update_parking_slot(client, db_session, admin_token):
    """Test updating an existing parking slot."""
    # Create test parking slot
    slot = ParkingSlot(label="P3", status=SlotStatus.FREE)
    db_session.add(slot)
    db_session.commit()

    response = client.put(
        f"/parking-slots/{slot.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "label": "P3-updated",
            "status": "maintenance"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["label"] == "P3-updated"
    assert data["status"] == "maintenance"

def test_delete_parking_slot(client, db_session, admin_token):
    """Test deleting an existing parking slot."""
    # Create test parking slot
    slot = ParkingSlot(label="P4", status=SlotStatus.FREE)
    db_session.add(slot)
    db_session.commit()

    response = client.delete(
        f"/parking-slots/{slot.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK

    # Verify slot is deleted
    response = client.get(
        "/parking-slots",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    data = response.json()
    assert not any(s["label"] == "P4" for s in data) 