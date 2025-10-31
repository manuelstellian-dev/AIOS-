"""Test FEV Batch 1 (Math Domain)"""
import pytest
from venom.fev.concepts import FEVFoundation, MATH_BATCH_1

def test_fev_batch_1_loading():
    """Test batch 1 loads correctly"""
    foundation = FEVFoundation()
    foundation.load_batch(MATH_BATCH_1)
    
    assert len(foundation.concepts) == 10
    assert "MATH_001" in foundation.concepts
    assert "MATH_010" in foundation.concepts

def test_fev_batch_1_confidence():
    """Test all concepts have high confidence"""
    foundation = FEVFoundation()
    foundation.load_batch(MATH_BATCH_1)
    
    for cid, concept in foundation.concepts.items():
        assert concept.confidence >= 0.95
        assert concept.prior_p0 == 1.0

def test_fev_batch_1_relations():
    """Test concept relations"""
    foundation = FEVFoundation()
    foundation.load_batch(MATH_BATCH_1)
    
    # MATH_002 should relate to MATH_001
    math_002 = foundation.get_concept("MATH_002")
    assert "MATH_001" in math_002.relations
