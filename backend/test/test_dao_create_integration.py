import pytest
from pymongo import MongoClient
from src.util.dao import DAO

@pytest.fixture(scope="module")
def mongo_test_db():
    """Create a test-only Mongo collection with a MOCKED validator."""
    client = MongoClient("mongodb://root:root@localhost:27017")
    db = client["edutask_test"]
    collection_name = "it_user_create"
    
    mock_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["mock_email"],
            "properties": {
                "mock_email": {
                    "bsonType": "string"
                }
            }
        }
    }

    if collection_name in db.list_collection_names():
        db[collection_name].drop()
    
    db.create_collection(collection_name, validator=mock_validator)

    dao = DAO.__new__(DAO)
    dao.collection = db[collection_name]

    try:
        yield dao
    finally:
        db[collection_name].drop()
        client.close()


def test_create_valid_document(mongo_test_db):
    """Should insert a valid document according to the MOCK validator."""
    data = {
        "mock_email": "ardian@example.com",
        "extra_field": "This is allowed"
    }

    created = mongo_test_db.create(data)

    assert created["mock_email"] == "ardian@example.com"
    assert "_id" in created


def test_create_invalid_document_rejected(mongo_test_db):
    """Should reject invalid data that violates the MOCK validator."""
    invalid_data = {
        "wrong_field": "Habibullah"
    }

    with pytest.raises(Exception):
        mongo_test_db.create(invalid_data)