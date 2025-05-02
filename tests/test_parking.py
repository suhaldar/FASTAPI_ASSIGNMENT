import pytest
from fastapi import status
from app.models.parking import ParkingSlot
from app.schemas.parking import SlotStatus

def test_list_parking_slots(client, db_session, user_token):
    """Test listing available parking slots"""
    # Create some test parking slots
    slots = [
        ParkingSlot(floor=1, label="A1", status="free"),
        ParkingSlot(floor=1, label="A2", status="free"),
        ParkingSlot(floor=2, label="B1", status="occupied")
    ]
    db_session.add_all(slots)
    db_session.commit()

    response = client.get(
        "/parking-slots",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2  # Only free slots should be returned
    assert all(slot["status"] == "free" for slot in data)

def test_list_parking_slots_empty(client, db_session, user_token):
    """Test listing parking slots when none exist"""
    response = client.get(
        "/parking-slots",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "No parking slots found"

def test_create_parking_slot_success(client, db_session, admin_token):
    """Test successful creation of a parking slot"""
    response = client.post(
        "/parking-slots",
        json={
            "floor": 1,
            "label": "A1",
            "status": "free"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "created successfully" in response.json()["message"]

def test_create_parking_slot_negative_floor(client, admin_token):
    """Test creating parking slot with negative floor number"""
    response = client.post(
        "/parking-slots",
        json={
            "floor": -1,
            "label": "A1",
            "status": "free"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Floor number cannot be negative" in response.json()["detail"]

def test_create_parking_slot_duplicate(client, db_session, admin_token):
    """Test creating duplicate parking slot"""
    # Create initial slot
    slot = ParkingSlot(floor=1, label="A1", status="free")
    db_session.add(slot)
    db_session.commit()

    # Try to create duplicate
    response = client.post(
        "/parking-slots",
        json={
            "floor": 1,
            "label": "A1",
            "status": "free"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]

def test_update_parking_slot_success(client, db_session, admin_token):
    """Test successful update of parking slot status"""
    # Create initial slot
    slot = ParkingSlot(floor=1, label="A1", status="free")
    db_session.add(slot)
    db_session.commit()

    response = client.put(
        "/parking-slots/",
        json={
            "floor": 1,
            "label": "A1",
            "status": "maintenance"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "updated to 'maintenance' status" in response.json()["message"]

def test_update_parking_slot_not_found(client, admin_token):
    """Test updating non-existent parking slot"""
    response = client.put(
        "/parking-slots/",
        json={
            "floor": 999,
            "label": "XX",
            "status": "maintenance"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]

def test_update_parking_slot_same_status(client, db_session, admin_token):
    """Test updating parking slot with same status"""
    # Create initial slot
    slot = ParkingSlot(floor=1, label="A1", status="free")
    db_session.add(slot)
    db_session.commit()

    response = client.put(
        "/parking-slots/",
        json={
            "floor": 1,
            "label": "A1",
            "status": "free"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already in 'free' status" in response.json()["detail"]

def test_delete_parking_slot_success(client, db_session, admin_token):
    """Test successful deletion of parking slot"""
    # Create slot to delete
    slot = ParkingSlot(floor=1, label="A1", status="free")
    db_session.add(slot)
    db_session.commit()

    response = client.delete(
        "/parking-slots/1/A1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "deleted successfully" in response.json()["message"]

def test_delete_parking_slot_not_found(client, admin_token):
    """Test deleting non-existent parking slot"""
    response = client.delete(
        "/parking-slots/999/XX",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]

def test_create_bulk_parking_slots(client, db_session, admin_token):
    """Test bulk creation of parking slots"""
    response = client.post(
        "/parking-slots/bulk",
        json=[
            {"floor": 1, "label": "A1", "status": "free"},
            {"floor": 1, "label": "A2", "status": "free"},
            {"floor": 2, "label": "B1", "status": "free"}
        ],
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["created"] == 3
    assert response.json()["skipped"] == 0

def test_create_bulk_parking_slots_with_duplicates(client, db_session, admin_token):
    """Test bulk creation with some existing slots"""
    # Create initial slot
    slot = ParkingSlot(floor=1, label="A1", status="free")
    db_session.add(slot)
    db_session.commit()

    response = client.post(
        "/parking-slots/bulk",
        json=[
            {"floor": 1, "label": "A1", "status": "free"},  # Existing
            {"floor": 1, "label": "A2", "status": "free"},  # New
            {"floor": 2, "label": "B1", "status": "free"}   # New
        ],
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["created"] == 2
    assert response.json()["skipped"] == 1

def test_update_bulk_parking_slots(client, db_session, admin_token):
    """Test bulk update of parking slots"""
    # Create initial slots
    slots = [
        ParkingSlot(floor=1, label="A1", status="free"),
        ParkingSlot(floor=1, label="A2", status="free")
    ]
    db_session.add_all(slots)
    db_session.commit()

    response = client.put(
        "/parking-slots/bulk",
        json=[
            {"floor": 1, "label": "A1", "status": "maintenance"},
            {"floor": 1, "label": "A2", "status": "maintenance"},
            {"floor": 2, "label": "B1", "status": "maintenance"}  # Non-existent
        ],
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["updated"] == 2
    assert response.json()["not_found"] == 1

def test_set_maintenance_mode_all(client, db_session, admin_token):
    """Test setting maintenance mode for all slots"""
    # Create test slots
    slots = [
        ParkingSlot(floor=1, label="A1", status="free"),
        ParkingSlot(floor=1, label="A2", status="free"),
        ParkingSlot(floor=2, label="B1", status="free")
    ]
    db_session.add_all(slots)
    db_session.commit()

    response = client.put(
        "/parking-slots/maintenance",
        params={"maintenance": True},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"].startswith("Maintenance mode enabled")
    assert len(response.json()["updated_slots"]) == 3

def test_set_maintenance_mode_by_floor(client, db_session, admin_token):
    """Test setting maintenance mode for specific floor"""
    # Create test slots
    slots = [
        ParkingSlot(floor=1, label="A1", status="free"),
        ParkingSlot(floor=1, label="A2", status="free"),
        ParkingSlot(floor=2, label="B1", status="free")
    ]
    db_session.add_all(slots)
    db_session.commit()

    response = client.put(
        "/parking-slots/maintenance",
        params={"floor": 1, "maintenance": True},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["updated_slots"]) == 2

def test_set_maintenance_mode_by_label(client, db_session, admin_token):
    """Test setting maintenance mode for specific label"""
    # Create test slots
    slots = [
        ParkingSlot(floor=1, label="A1", status="free"),
        ParkingSlot(floor=2, label="A1", status="free"),
        ParkingSlot(floor=1, label="A2", status="free")
    ]
    db_session.add_all(slots)
    db_session.commit()

    response = client.put(
        "/parking-slots/maintenance",
        params={"label": "A1", "maintenance": True},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["updated_slots"]) == 2

def test_set_maintenance_mode_not_found(client, admin_token):
    """Test setting maintenance mode for non-existent slots"""
    response = client.put(
        "/parking-slots/maintenance",
        params={"floor": 999, "label": "XX", "maintenance": True},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "No parking slots found" in response.json()["detail"]

def test_unauthorized_access(client):
    """Test unauthorized access to parking endpoints"""
    # List slots
    response = client.get("/parking-slots")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Create slot
    response = client.post("/parking-slots", json={"floor": 1, "label": "A1", "status": "free"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Update slot
    response = client.put("/parking-slots/", json={"floor": 1, "label": "A1", "status": "maintenance"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Delete slot
    response = client.delete("/parking-slots/1/A1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Bulk operations
    response = client.post("/parking-slots/bulk", json=[{"floor": 1, "label": "A1", "status": "free"}])
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.put("/parking-slots/bulk", json=[{"floor": 1, "label": "A1", "status": "maintenance"}])
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Maintenance mode
    response = client.put("/parking-slots/maintenance")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_user_operations_forbidden(client, user_token):
    """Test that regular users cannot perform admin operations"""
    # Create slot
    response = client.post(
        "/parking-slots",
        json={"floor": 1, "label": "A1", "status": "free"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Update slot
    response = client.put(
        "/parking-slots/",
        json={"floor": 1, "label": "A1", "status": "maintenance"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Delete slot
    response = client.delete(
        "/parking-slots/1/A1",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Bulk operations
    response = client.post(
        "/parking-slots/bulk",
        json=[{"floor": 1, "label": "A1", "status": "free"}],
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.put(
        "/parking-slots/bulk",
        json=[{"floor": 1, "label": "A1", "status": "maintenance"}],
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Maintenance mode
    response = client.put(
        "/parking-slots/maintenance",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_user_operations_unauthorized(client):
    """Test that unauthorized users cannot perform admin operations."""
    # Try to create a slot without token
    response = client.post(
        "/parking-slots",
        json={
            "floor": 1,
            "label": "A1",
            "status": "FREE"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 