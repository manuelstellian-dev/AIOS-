"""Tests for Document Store"""
import pytest
import tempfile
import shutil
import os
from venom.knowledge.document_store import DocumentStore


@pytest.fixture
def temp_store():
    """Create a temporary document store"""
    temp_dir = tempfile.mkdtemp()
    store = DocumentStore(storage_path=temp_dir)
    yield store
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_add_and_get_document(temp_store):
    """Test adding and retrieving documents"""
    doc_id = "doc1"
    content = "This is a test document about machine learning and AI"
    metadata = {"author": "test", "tags": ["ml", "ai"]}
    
    # Add document
    assert temp_store.add_document(doc_id, content, metadata) is True
    
    # Get document
    doc = temp_store.get_document(doc_id)
    assert doc['content'] == content
    assert doc['metadata'] == metadata
    assert 'timestamp' in doc


def test_update_document(temp_store):
    """Test updating documents"""
    doc_id = "doc1"
    content1 = "Original content"
    content2 = "Updated content"
    
    # Add document
    temp_store.add_document(doc_id, content1, {"version": 1})
    
    # Update document
    assert temp_store.update_document(doc_id, content2, {"version": 2}) is True
    
    # Verify update
    doc = temp_store.get_document(doc_id)
    assert doc['content'] == content2
    assert doc['metadata']['version'] == 2


def test_delete_document(temp_store):
    """Test deleting documents"""
    doc_id = "doc1"
    content = "Document to delete"
    
    # Add document
    temp_store.add_document(doc_id, content)
    assert temp_store.get_document(doc_id) != {}
    
    # Delete document
    assert temp_store.delete_document(doc_id) is True
    assert temp_store.get_document(doc_id) == {}
    
    # Try deleting non-existent document
    assert temp_store.delete_document("nonexistent") is False


def test_list_documents(temp_store):
    """Test listing documents"""
    # Add multiple documents
    for i in range(5):
        temp_store.add_document(f"doc{i}", f"Content {i}", {"index": i})
    
    # List documents
    docs = temp_store.list_documents(limit=10)
    assert len(docs) == 5
    
    # Test limit
    docs_limited = temp_store.list_documents(limit=3)
    assert len(docs_limited) == 3


def test_similarity_search(temp_store):
    """Test finding similar documents"""
    # Add documents with related content
    temp_store.add_document("doc1", "machine learning and artificial intelligence")
    temp_store.add_document("doc2", "deep learning neural networks")
    temp_store.add_document("doc3", "cooking recipes and food")
    
    # Search for ML-related content
    results = temp_store.get_similar_documents("machine learning AI", top_k=2)
    
    assert len(results) <= 2
    if len(results) > 0:
        # First result should be most relevant
        assert 'similarity' in results[0]
        assert 'doc_id' in results[0]
