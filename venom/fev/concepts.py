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

# Batch 2: Physics Domain (10 concepts)
PHYSICS_BATCH_2 = [
    {
        "id": "PHYS_001",
        "domain": "Physics",
        "topic": "Newton's First Law",
        "formal": "F_net = 0 → v = constant",
        "relations": ["MATH_001"],
        "confidence": 1.0,
        "source": "Classical Mechanics",
        "prior_p0": 1.0
    },
    {
        "id": "PHYS_002",
        "domain": "Physics",
        "topic": "Newton's Second Law",
        "formal": "F = ma",
        "relations": ["PHYS_001", "MATH_003"],
        "confidence": 1.0,
        "source": "Classical Mechanics",
        "prior_p0": 1.0
    },
    {
        "id": "PHYS_003",
        "domain": "Physics",
        "topic": "Newton's Third Law",
        "formal": "F_AB = -F_BA",
        "relations": ["PHYS_002"],
        "confidence": 1.0,
        "source": "Classical Mechanics",
        "prior_p0": 1.0
    },
    {
        "id": "PHYS_004",
        "domain": "Physics",
        "topic": "Conservation of Energy",
        "formal": "E_total = constant",
        "relations": ["MATH_001", "MATH_010"],
        "confidence": 1.0,
        "source": "Thermodynamics",
        "prior_p0": 1.0
    },
    {
        "id": "PHYS_005",
        "domain": "Physics",
        "topic": "Conservation of Momentum",
        "formal": "Σp_i = constant",
        "relations": ["PHYS_002", "MATH_001"],
        "confidence": 1.0,
        "source": "Classical Mechanics",
        "prior_p0": 1.0
    },
    {
        "id": "PHYS_006",
        "domain": "Physics",
        "topic": "Einstein's Mass-Energy Equivalence",
        "formal": "E = mc²",
        "relations": ["PHYS_004", "MATH_002"],
        "confidence": 1.0,
        "source": "Special Relativity",
        "prior_p0": 1.0
    },
    {
        "id": "PHYS_007",
        "domain": "Physics",
        "topic": "Heisenberg Uncertainty Principle",
        "formal": "Δx·Δp ≥ ℏ/2",
        "relations": ["MATH_001"],
        "confidence": 1.0,
        "source": "Quantum Mechanics",
        "prior_p0": 1.0
    },
    {
        "id": "PHYS_008",
        "domain": "Physics",
        "topic": "First Law of Thermodynamics",
        "formal": "ΔU = Q - W",
        "relations": ["PHYS_004"],
        "confidence": 1.0,
        "source": "Thermodynamics",
        "prior_p0": 1.0
    },
    {
        "id": "PHYS_009",
        "domain": "Physics",
        "topic": "Maxwell's Equations (Gauss's Law)",
        "formal": "∇·E = ρ/ε₀",
        "relations": ["MATH_010"],
        "confidence": 1.0,
        "source": "Electromagnetism",
        "prior_p0": 1.0
    },
    {
        "id": "PHYS_010",
        "domain": "Physics",
        "topic": "Schrödinger Equation",
        "formal": "iℏ∂ψ/∂t = Ĥψ",
        "relations": ["PHYS_007", "MATH_010"],
        "confidence": 1.0,
        "source": "Quantum Mechanics",
        "prior_p0": 1.0
    }
]

# Batch 3: Biology Domain (10 concepts)
BIOLOGY_BATCH_3 = [
    {
        "id": "BIO_001",
        "domain": "Biology",
        "topic": "DNA Structure",
        "formal": "Double helix: A-T, G-C base pairing",
        "relations": ["MATH_001", "PHYS_004"],
        "confidence": 1.0,
        "source": "Molecular Biology",
        "prior_p0": 1.0
    },
    {
        "id": "BIO_002",
        "domain": "Biology",
        "topic": "Central Dogma",
        "formal": "DNA → RNA → Protein",
        "relations": ["BIO_001", "MATH_003"],
        "confidence": 1.0,
        "source": "Molecular Biology",
        "prior_p0": 1.0
    },
    {
        "id": "BIO_003",
        "domain": "Biology",
        "topic": "Evolution by Natural Selection",
        "formal": "Variation + Selection + Inheritance → Evolution",
        "relations": ["MATH_008", "PHYS_004"],
        "confidence": 1.0,
        "source": "Evolutionary Biology",
        "prior_p0": 1.0
    },
    {
        "id": "BIO_004",
        "domain": "Biology",
        "topic": "Cell Theory",
        "formal": "All life from cells; cell is unit of life",
        "relations": ["MATH_001"],
        "confidence": 1.0,
        "source": "Cell Biology",
        "prior_p0": 1.0
    },
    {
        "id": "BIO_005",
        "domain": "Biology",
        "topic": "Mendel's Laws",
        "formal": "Segregation + Independent Assortment",
        "relations": ["BIO_001", "MATH_008"],
        "confidence": 1.0,
        "source": "Genetics",
        "prior_p0": 1.0
    },
    {
        "id": "BIO_006",
        "domain": "Biology",
        "topic": "Krebs Cycle",
        "formal": "Acetyl-CoA → CO₂ + ATP + NADH + FADH₂",
        "relations": ["PHYS_004", "PHYS_008"],
        "confidence": 1.0,
        "source": "Biochemistry",
        "prior_p0": 1.0
    },
    {
        "id": "BIO_007",
        "domain": "Biology",
        "topic": "Photosynthesis",
        "formal": "6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂",
        "relations": ["PHYS_004", "MATH_003"],
        "confidence": 1.0,
        "source": "Plant Biology",
        "prior_p0": 1.0
    },
    {
        "id": "BIO_008",
        "domain": "Biology",
        "topic": "Homeostasis",
        "formal": "Negative feedback maintains equilibrium",
        "relations": ["MATH_001", "PHYS_001"],
        "confidence": 1.0,
        "source": "Physiology",
        "prior_p0": 1.0
    },
    {
        "id": "BIO_009",
        "domain": "Biology",
        "topic": "Ecosystem Energy Flow",
        "formal": "Sun → Producers → Consumers → Decomposers",
        "relations": ["PHYS_004", "BIO_007"],
        "confidence": 1.0,
        "source": "Ecology",
        "prior_p0": 1.0
    },
    {
        "id": "BIO_010",
        "domain": "Biology",
        "topic": "Hardy-Weinberg Equilibrium",
        "formal": "p² + 2pq + q² = 1 (allele frequencies)",
        "relations": ["MATH_001", "MATH_002", "BIO_003"],
        "confidence": 1.0,
        "source": "Population Genetics",
        "prior_p0": 1.0
    }
]
