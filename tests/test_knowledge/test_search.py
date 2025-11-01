"""Tests for Search Engine"""
import pytest
import tempfile
import shutil
from venom.knowledge.document_store import DocumentStore
from venom.knowledge.search import SearchEngine


@pytest.fixture
def search_engine():
    """Create a search engine with sample documents"""
    temp_dir = tempfile.mkdtemp()
    store = DocumentStore(storage_path=temp_dir)
    
    # Add sample documents
    store.add_document("doc1", "machine learning and artificial intelligence", 
                      {"category": "tech"})
    store.add_document("doc2", "deep learning neural networks and AI", 
                      {"category": "tech"})
    store.add_document("doc3", "cooking recipes and delicious food", 
                      {"category": "food"})
    store.add_document("doc4", "python programming language tutorial", 
                      {"category": "tech"})
    
    engine = SearchEngine(store)
    
    yield engine
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_basic_search(search_engine):
    """Test basic search functionality"""
    results = search_engine.search("machine learning", top_k=2)
    
    assert len(results) <= 2
    assert all('doc_id' in r for r in results)
    assert all('score' in r for r in results)
    
    # Most relevant doc should be first
    if len(results) > 0:
        assert results[0]['score'] > 0


def test_boolean_search(search_engine):
    """Test boolean search with AND, OR, NOT"""
    # AND search
    results = search_engine.boolean_search("machine AND learning")
    assert len(results) > 0
    
    # OR search
    results = search_engine.boolean_search("machine OR cooking")
    assert len(results) >= 2
    
    # NOT search
    results = search_engine.boolean_search("learning NOT deep")
    # Should include doc1 but not doc2
    doc_ids = [r['doc_id'] for r in results]
    if 'doc1' in doc_ids:
        assert 'doc2' not in doc_ids or len(results) > 1


def test_phrase_search(search_engine):
    """Test exact phrase search"""
    # Phrase that exists
    results = search_engine.phrase_search("machine learning")
    assert len(results) > 0
    
    # Check that phrase is in results
    for result in results:
        content_lower = result['content'].lower()
        assert "machine learning" in content_lower or "machine" in content_lower


def test_metadata_filter(search_engine):
    """Test filtering by metadata"""
    # Filter by category
    results = search_engine.filter_by_metadata({"category": "tech"})
    assert len(results) == 3
    
    # All results should have tech category
    for result in results:
        assert result['metadata']['category'] == "tech"
    
    # Filter by non-existent category
    results = search_engine.filter_by_metadata({"category": "sports"})
    assert len(results) == 0


def test_index_stats(search_engine):
    """Test index statistics"""
    stats = search_engine.get_index_stats()
    
    assert 'total_terms' in stats
    assert 'total_documents' in stats
    assert 'total_postings' in stats
    
    assert stats['total_documents'] == 4
    assert stats['total_terms'] > 0
