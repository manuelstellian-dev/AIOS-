"""
FEV (Fractal Edge Vectors) - Foundation Concepts
Batch 1: Mathematics Domain (10 concepts)
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import json

@dataclass
class FEVConcept:
    """Single FEV concept"""
    id: str
    domain: str
    topic: str
    formal: str
    relations: List[str]
    confidence: float
    source: str
    prior_p0: float

class FEVFoundation:
    """FEV Foundation - stores and manages concepts"""
    
    def __init__(self):
        self.concepts: Dict[str, FEVConcept] = {}
    
    def add_concept(self, concept: FEVConcept):
        """Add concept to foundation"""
        self.concepts[concept.id] = concept
    
    def load_batch(self, batch_data: List[Dict]):
        """Load batch of concepts"""
        for data in batch_data:
            concept = FEVConcept(**data)
            self.add_concept(concept)
    
    def get_concept(self, cid: str) -> Optional[FEVConcept]:
        """Get concept by ID"""
        return self.concepts.get(cid)

# Batch 1: Math Domain (10 concepts)
MATH_BATCH_1 = [
    {
        "id": "MATH_001",
        "domain": "Mathematics",
        "topic": "Axiom of Reflexivity",
        "formal": "∀x: x = x",
        "relations": [],
        "confidence": 1.0,
        "source": "Peano Axioms",
        "prior_p0": 1.0
    },
    {
        "id": "MATH_002",
        "domain": "Mathematics",
        "topic": "Pythagorean Theorem",
        "formal": "a² + b² = c² (right triangle)",
        "relations": ["MATH_001"],
        "confidence": 1.0,
        "source": "Euclidean Geometry",
        "prior_p0": 1.0
    },
    {
        "id": "MATH_003",
        "domain": "Mathematics",
        "topic": "Commutative Property",
        "formal": "a + b = b + a",
        "relations": ["MATH_001"],
        "confidence": 1.0,
        "source": "Algebra",
        "prior_p0": 1.0
    },
    {
        "id": "MATH_004",
        "domain": "Mathematics",
        "topic": "Associative Property",
        "formal": "(a + b) + c = a + (b + c)",
        "relations": ["MATH_003"],
        "confidence": 1.0,
        "source": "Algebra",
        "prior_p0": 1.0
    },
    {
        "id": "MATH_005",
        "domain": "Mathematics",
        "topic": "Distributive Property",
        "formal": "a(b + c) = ab + ac",
        "relations": ["MATH_003", "MATH_004"],
        "confidence": 1.0,
        "source": "Algebra",
        "prior_p0": 1.0
    },
    {
        "id": "MATH_006",
        "domain": "Mathematics",
        "topic": "Zero Property",
        "formal": "a × 0 = 0",
        "relations": ["MATH_001"],
        "confidence": 1.0,
        "source": "Arithmetic",
        "prior_p0": 1.0
    },
    {
        "id": "MATH_007",
        "domain": "Mathematics",
        "topic": "Identity Property",
        "formal": "a × 1 = a",
        "relations": ["MATH_001"],
        "confidence": 1.0,
        "source": "Arithmetic",
        "prior_p0": 1.0
    },
    {
        "id": "MATH_008",
        "domain": "Mathematics",
        "topic": "Prime Numbers",
        "formal": "p > 1 ∧ divisible only by 1 and p",
        "relations": ["MATH_001"],
        "confidence": 1.0,
        "source": "Number Theory",
        "prior_p0": 1.0
    },
    {
        "id": "MATH_009",
        "domain": "Mathematics",
        "topic": "Euler's Identity",
        "formal": "e^(iπ) + 1 = 0",
        "relations": ["MATH_001"],
        "confidence": 1.0,
        "source": "Complex Analysis",
        "prior_p0": 1.0
    },
    {
        "id": "MATH_010",
        "domain": "Mathematics",
        "topic": "Fundamental Theorem of Calculus",
        "formal": "∫[a,b] f'(x)dx = f(b) - f(a)",
        "relations": ["MATH_001"],
        "confidence": 1.0,
        "source": "Calculus",
        "prior_p0": 1.0
    }
]
