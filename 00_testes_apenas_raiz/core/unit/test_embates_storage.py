"""
Testes unitários para storage de embates.
"""

import pytest

from backend_rag_ia.cli.embates.storage import SupabaseStorage
from backend_rag_ia.tests.utils.test_helpers import MockSupabaseClient, create_test_embate


@pytest.fixture
def mock_supabase_client():
    return MockSupabaseClient()

@pytest.fixture
def storage(mock_supabase_client):
    return SupabaseStorage(mock_supabase_client)

@pytest.mark.asyncio
async def test_create_embate(storage):
    embate = create_test_embate()
    await storage.create_embate(embate)
    assert storage.client.table_data["embates"][0]["id"] == embate.id

@pytest.mark.asyncio
async def test_search_embates(storage):
    embate = create_test_embate()
    await storage.create_embate(embate)
    results = await storage.search_embates("test")
    assert len(results) == 1
    assert results[0].id == embate.id

@pytest.mark.asyncio
async def test_update_embate(storage):
    embate = create_test_embate()
    await storage.create_embate(embate)
    embate.status = "completed"
    await storage.update_embate(embate)
    assert storage.client.table_data["embates"][0]["status"] == "completed" 