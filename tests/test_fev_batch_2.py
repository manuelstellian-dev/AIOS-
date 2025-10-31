"""Test FEV Batch 2 (Physics Domain)"""
import pytest
from venom.fev.concepts import FEVFoundation, PHYSICS_BATCH_2, MATH_BATCH_1

def test_fev_batch_2_loading():
    """Test batch 2 loads correctly with 10 physics concepts"""
    foundation = FEVFoundation()
    foundation.load_batch(PHYSICS_BATCH_2)
    
    assert len(foundation.concepts) == 10
    assert "PHYS_001" in foundation.concepts
    assert "PHYS_010" in foundation.concepts
    
    # Verify all concepts are from Physics domain
    for cid, concept in foundation.concepts.items():
        assert concept.domain == "Physics"

def test_fev_batch_2_confidence():
    """Test all physics concepts have high confidence"""
    foundation = FEVFoundation()
    foundation.load_batch(PHYSICS_BATCH_2)
    
    for cid, concept in foundation.concepts.items():
        assert concept.confidence >= 0.95
        assert concept.prior_p0 == 1.0

def test_fev_batch_2_cross_domain_relations():
    """Test physics concepts have relations to math concepts"""
    foundation = FEVFoundation()
    foundation.load_batch(MATH_BATCH_1)
    foundation.load_batch(PHYSICS_BATCH_2)
    
    # PHYS_001 (Newton's First Law) should relate to MATH_001
    phys_001 = foundation.get_concept("PHYS_001")
    assert "MATH_001" in phys_001.relations
    
    # PHYS_006 (E=mc²) should relate to PHYS_004 and MATH_002
    phys_006 = foundation.get_concept("PHYS_006")
    assert "PHYS_004" in phys_006.relations
    assert "MATH_002" in phys_006.relations
    
    # Verify cross-domain relations exist
    math_relations_count = 0
    for cid, concept in foundation.concepts.items():
        if concept.domain == "Physics":
            for rel in concept.relations:
                if rel.startswith("MATH_"):
                    math_relations_count += 1
    
    assert math_relations_count >= 5, "Should have at least 5 cross-domain relations"

def test_fev_batch_2_physics_laws():
    """Test specific physics laws are present"""
    foundation = FEVFoundation()
    foundation.load_batch(PHYSICS_BATCH_2)
    
    # Check Newton's Laws
    assert "PHYS_001" in foundation.concepts  # Newton's First
    assert "PHYS_002" in foundation.concepts  # Newton's Second
    assert "PHYS_003" in foundation.concepts  # Newton's Third
    
    # Check Conservation Laws
    assert "PHYS_004" in foundation.concepts  # Energy
    assert "PHYS_005" in foundation.concepts  # Momentum
    
    # Check Einstein E=mc²
    assert "PHYS_006" in foundation.concepts
    einstein = foundation.get_concept("PHYS_006")
    assert "E = mc²" in einstein.formal
    
    # Check Quantum concepts
    assert "PHYS_007" in foundation.concepts  # Heisenberg
    assert "PHYS_010" in foundation.concepts  # Schrödinger
