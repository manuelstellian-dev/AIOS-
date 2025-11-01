"""Tests for Knowledge Graph"""
import pytest
import tempfile
import os
from venom.knowledge.graph import KnowledgeGraph


@pytest.fixture
def graph():
    """Create a knowledge graph with sample data"""
    kg = KnowledgeGraph()
    
    # Add nodes
    kg.add_node("person1", "person", {"name": "Alice", "age": 30})
    kg.add_node("person2", "person", {"name": "Bob", "age": 25})
    kg.add_node("company1", "company", {"name": "TechCorp"})
    kg.add_node("project1", "project", {"name": "AI System"})
    
    # Add edges
    kg.add_edge("person1", "company1", "works_at")
    kg.add_edge("person2", "company1", "works_at")
    kg.add_edge("person1", "project1", "manages")
    kg.add_edge("person2", "project1", "contributes_to")
    
    return kg


def test_add_and_get_node(graph):
    """Test adding and retrieving nodes"""
    # Get existing node
    node = graph.get_node("person1")
    assert node['node_id'] == "person1"
    assert node['type'] == "person"
    assert node['properties']['name'] == "Alice"
    
    # Add new node
    assert graph.add_node("person3", "person", {"name": "Charlie"}) is True
    node = graph.get_node("person3")
    assert node['properties']['name'] == "Charlie"


def test_update_node(graph):
    """Test updating node properties"""
    # Update existing node
    assert graph.update_node("person1", {"age": 31, "city": "NYC"}) is True
    
    node = graph.get_node("person1")
    assert node['properties']['age'] == 31
    assert node['properties']['city'] == "NYC"
    assert node['properties']['name'] == "Alice"  # Original property preserved


def test_edges(graph):
    """Test edge operations"""
    # Get edges
    edges = graph.get_edges("person1", direction="out")
    assert len(edges) == 2
    
    # Check edge details
    edge_relations = [e['relation'] for e in edges]
    assert "works_at" in edge_relations
    assert "manages" in edge_relations
    
    # Get incoming edges
    in_edges = graph.get_edges("company1", direction="in")
    assert len(in_edges) == 2


def test_find_path(graph):
    """Test pathfinding between nodes"""
    # Find path from person2 to company1
    paths = graph.find_path("person2", "company1", max_depth=5)
    
    assert len(paths) > 0
    # Check that path contains start and end nodes
    assert paths[0][0] == "person2"
    assert paths[0][-1] == "company1"


def test_get_neighbors(graph):
    """Test getting neighbors within depth"""
    # Get immediate neighbors of person1
    neighbors = graph.get_neighbors("person1", depth=1)
    
    assert len(neighbors) == 2
    neighbor_ids = [n['node_id'] for n in neighbors]
    assert "company1" in neighbor_ids
    assert "project1" in neighbor_ids
    
    # Get neighbors within depth 2
    neighbors_2 = graph.get_neighbors("person1", depth=2)
    assert len(neighbors_2) >= len(neighbors)


def test_query(graph):
    """Test graph queries"""
    # Query by type
    persons = graph.query("type:person")
    assert len(persons) == 2
    
    # Query by property
    results = graph.query("property:name=Alice")
    assert len(results) == 1
    assert results[0]['node_id'] == "person1"


def test_delete_node(graph):
    """Test deleting nodes"""
    # Delete node
    assert graph.delete_node("person2") is True
    
    # Verify node is deleted
    node = graph.get_node("person2")
    assert node == {}
    
    # Verify edges are also removed
    edges = graph.get_edges("company1", direction="in")
    edge_sources = [e['from'] for e in edges]
    assert "person2" not in edge_sources


def test_persistence():
    """Test saving and loading graph"""
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_path = temp_file.name
    temp_file.close()
    
    try:
        # Create and populate graph
        kg1 = KnowledgeGraph()
        kg1.add_node("n1", "type1", {"key": "value"})
        kg1.add_node("n2", "type2")
        kg1.add_edge("n1", "n2", "relates_to")
        
        # Save graph
        assert kg1.save(temp_path) is True
        
        # Load into new graph
        kg2 = KnowledgeGraph()
        assert kg2.load(temp_path) is True
        
        # Verify data
        assert len(kg2.nodes) == 2
        node = kg2.get_node("n1")
        assert node['properties']['key'] == "value"
        
        edges = kg2.get_edges("n1", direction="out")
        assert len(edges) == 1
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_graphviz_export(graph):
    """Test GraphViz export"""
    dot = graph.export_graphviz()
    
    assert "digraph KnowledgeGraph" in dot
    assert "person1" in dot
    assert "works_at" in dot
