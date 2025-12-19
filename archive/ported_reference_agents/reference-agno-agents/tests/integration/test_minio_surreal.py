import pytest
import os
from unittest.mock import MagicMock, patch
from khala.infrastructure.storage.minio_adapter import MinIOStorage
from khala.application.services.multimodal_service import MultimodalService

# Mock or use real connection if available via docker-compose
# For TDD, we start with structure verification

@pytest.mark.asyncio
async def test_upload_image_and_persist_metadata():
    """
    Feature: Blob Storage Integration
    Scenario: Uploading an image
    Given I have a raw image byte stream
    When I ingest the image via MultimodalService
    Then the image should be stored in MinIO bucket 'vivi-infra-raw'
    And the image metadata (including MinIO URI) should be stored in SurrealDB
    """
    
    # Arrange
    raw_data = b"fake_image_content"
    filename = "test_image.png"
    
    # Mocks for dependencies
    repo_mock = MagicMock()
    repo_mock.save = MagicMock(side_effect=lambda x: x) # Return the memory object
    repo_mock.create = MagicMock(side_effect=lambda x: None) # Async mock usually needed
    
    # We need AsyncMock for async methods
    async def async_return(val=None):
        return val

    repo_mock.create = MagicMock(return_value=async_return())

    gemini_mock = MagicMock()
    gemini_mock.generate_text = MagicMock(return_value=async_return({"content": "A fake image description"}))
    
    # Mock Storage Adapter to avoid needing real MinIO for this specific test
    # (or use real one if we want full integration, but let's test wiring first)
    storage_mock = MagicMock(spec=MinIOStorage)
    storage_mock.upload = MagicMock(return_value=async_return("s3://vivi-infra-raw/test_image.png"))

    # Mock DB Client to avoid "Missing required environment variables" error
    db_mock = MagicMock()

    # Act
    service = MultimodalService(
        memory_repository=repo_mock,
        gemini_client=gemini_mock,
        db_client=db_mock,
        blob_storage=storage_mock
    )
    
    # This method currently suppresses raw data. We want it to return a URI or object with URI.
    # Modifying call to match signature
    result = await service.ingest_image(
        user_id="test_user",
        image_data=raw_data,
        mime_type="image/png",
        metadata={"filename": filename}
    )
    
    # Assert
    # Verify upload was called
    storage_mock.upload.assert_called_once()
    
    # Check result contains URI (from our recent change)
    # Note: ingest_image returns memory_id (str) in original code, but we might have changed it to dict?
    # Let's check the implementation again. 
    # Original implementation returns: memory.id (str)
    # My previous REPLACE (Step 1109) changed return type to Dict[str, Any] but then I reverted/repaired.
    # The repaired code (Step 1115) shows it returns `memory.id`.
    # AND it saves metadata inside the memory.
    
    # So we should verify the memory passed to repository.create has the metadata.
    saved_memory = repo_mock.create.call_args[0][0]
    assert saved_memory.metadata['uri'] == "s3://vivi-infra-raw/test_image.png"
    assert saved_memory.metadata['storage_provider'] == "minio"
