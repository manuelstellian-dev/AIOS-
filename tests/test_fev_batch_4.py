"""Test FEV Batch 4 (Chemistry Domain) - Completes 40 total concepts!"""
import pytest
from venom.fev.concepts import (
    FEVFoundation, 
    MATH_BATCH_1, 
    PHYSICS_BATCH_2, 
    BIOLOGY_BATCH_3,
    CHEMISTRY_BATCH_4
)

def test_fev_batch_4_loading():
    """Test batch 4 loads correctly with 10 chemistry concepts"""
    foundation = FEVFoundation()
    foundation.load_batch(CHEMISTRY_BATCH_4)
    
    assert len(foundation.concepts) == 10
    assert "CHEM_001" in foundation.concepts
    assert "CHEM_010" in foundation.concepts
    
    # Verify all concepts are from Chemistry domain
    for cid, concept in foundation.concepts.items():
        assert concept.domain == "Chemistry"

def test_fev_batch_4_confidence():
    """Test all chemistry concepts have high confidence"""
    foundation = FEVFoundation()
    foundation.load_batch(CHEMISTRY_BATCH_4)
    
    for cid, concept in foundation.concepts.items():
        assert concept.confidence >= 0.95
        assert concept.prior_p0 == 1.0

def test_fev_batch_4_cross_domain_relations():
    """Test chemistry concepts have relations to all other domains"""
    foundation = FEVFoundation()
    foundation.load_batch(MATH_BATCH_1)
    foundation.load_batch(PHYSICS_BATCH_2)
    foundation.load_batch(BIOLOGY_BATCH_3)
    foundation.load_batch(CHEMISTRY_BATCH_4)
    
    # CHEM_002 (Atomic Structure) should relate to PHYS_007 and MATH_001
    chem_002 = foundation.get_concept("CHEM_002")
    assert "PHYS_007" in chem_002.relations
    assert "MATH_001" in chem_002.relations
    
    # CHEM_009 (Organic Chemistry) should relate to BIO_001 and BIO_002
    chem_009 = foundation.get_concept("CHEM_009")
    assert "CHEM_004" in chem_009.relations
    assert "BIO_001" in chem_009.relations
    assert "BIO_002" in chem_009.relations
    
    # Verify cross-domain relations exist
    math_relations_count = 0
    physics_relations_count = 0
    biology_relations_count = 0
    
    for cid, concept in foundation.concepts.items():
        if concept.domain == "Chemistry":
            for rel in concept.relations:
                if rel.startswith("MATH_"):
                    math_relations_count += 1
                elif rel.startswith("PHYS_"):
                    physics_relations_count += 1
                elif rel.startswith("BIO_"):
                    biology_relations_count += 1
    
    assert math_relations_count >= 3, "Should have at least 3 Math cross-domain relations"
    assert physics_relations_count >= 3, "Should have at least 3 Physics cross-domain relations"
    assert biology_relations_count >= 2, "Should have at least 2 Biology cross-domain relations"

def test_fev_batch_4_40_total_concepts():
    """Test that all 4 batches together give 40 concepts total - COMPLETE KNOWLEDGE GRAPH!"""
    foundation = FEVFoundation()
    foundation.load_batch(MATH_BATCH_1)
    foundation.load_batch(PHYSICS_BATCH_2)
    foundation.load_batch(BIOLOGY_BATCH_3)
    foundation.load_batch(CHEMISTRY_BATCH_4)
    
    # Should have exactly 40 concepts total (10 per domain)
    assert len(foundation.concepts) == 40
    
    # Verify concept distribution across all 4 domains
    math_count = sum(1 for c in foundation.concepts.values() if c.domain == "Mathematics")
    physics_count = sum(1 for c in foundation.concepts.values() if c.domain == "Physics")
    biology_count = sum(1 for c in foundation.concepts.values() if c.domain == "Biology")
    chemistry_count = sum(1 for c in foundation.concepts.values() if c.domain == "Chemistry")
    
    assert math_count == 10, "Should have 10 Math concepts"
    assert physics_count == 10, "Should have 10 Physics concepts"
    assert biology_count == 10, "Should have 10 Biology concepts"
    assert chemistry_count == 10, "Should have 10 Chemistry concepts"
    
    # Verify complete knowledge graph with all domains
    domains = set(c.domain for c in foundation.concepts.values())
    assert domains == {"Mathematics", "Physics", "Biology", "Chemistry"}
