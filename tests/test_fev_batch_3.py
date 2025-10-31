"""Test FEV Batch 3 (Biology Domain)"""
import pytest
from venom.fev.concepts import FEVFoundation, BIOLOGY_BATCH_3, MATH_BATCH_1, PHYSICS_BATCH_2

def test_fev_batch_3_loading():
    """Test batch 3 loads correctly with 10 biology concepts"""
    foundation = FEVFoundation()
    foundation.load_batch(BIOLOGY_BATCH_3)
    
    assert len(foundation.concepts) == 10
    assert "BIO_001" in foundation.concepts
    assert "BIO_010" in foundation.concepts
    
    # Verify all concepts are from Biology domain
    for cid, concept in foundation.concepts.items():
        assert concept.domain == "Biology"

def test_fev_batch_3_confidence():
    """Test all biology concepts have high confidence"""
    foundation = FEVFoundation()
    foundation.load_batch(BIOLOGY_BATCH_3)
    
    for cid, concept in foundation.concepts.items():
        assert concept.confidence >= 0.95
        assert concept.prior_p0 == 1.0

def test_fev_batch_3_cross_domain_relations():
    """Test biology concepts have relations to math and physics concepts"""
    foundation = FEVFoundation()
    foundation.load_batch(MATH_BATCH_1)
    foundation.load_batch(PHYSICS_BATCH_2)
    foundation.load_batch(BIOLOGY_BATCH_3)
    
    # BIO_001 (DNA) should relate to MATH_001 and PHYS_004
    bio_001 = foundation.get_concept("BIO_001")
    assert "MATH_001" in bio_001.relations
    assert "PHYS_004" in bio_001.relations
    
    # BIO_010 (Hardy-Weinberg) should relate to MATH_001, MATH_002, and BIO_003
    bio_010 = foundation.get_concept("BIO_010")
    assert "MATH_001" in bio_010.relations
    assert "MATH_002" in bio_010.relations
    assert "BIO_003" in bio_010.relations
    
    # Verify cross-domain relations exist
    math_relations_count = 0
    physics_relations_count = 0
    for cid, concept in foundation.concepts.items():
        if concept.domain == "Biology":
            for rel in concept.relations:
                if rel.startswith("MATH_"):
                    math_relations_count += 1
                elif rel.startswith("PHYS_"):
                    physics_relations_count += 1
    
    assert math_relations_count >= 5, "Should have at least 5 Math cross-domain relations"
    assert physics_relations_count >= 3, "Should have at least 3 Physics cross-domain relations"

def test_fev_batch_3_30_total_concepts():
    """Test that all 3 batches together give 30 concepts"""
    foundation = FEVFoundation()
    foundation.load_batch(MATH_BATCH_1)
    foundation.load_batch(PHYSICS_BATCH_2)
    foundation.load_batch(BIOLOGY_BATCH_3)
    
    # Should have exactly 30 concepts total
    assert len(foundation.concepts) == 30
    
    # Verify concept distribution
    math_count = sum(1 for c in foundation.concepts.values() if c.domain == "Mathematics")
    physics_count = sum(1 for c in foundation.concepts.values() if c.domain == "Physics")
    biology_count = sum(1 for c in foundation.concepts.values() if c.domain == "Biology")
    
    assert math_count == 10
    assert physics_count == 10
    assert biology_count == 10
