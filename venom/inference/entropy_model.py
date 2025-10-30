"""
Entropy Model - Torch-based inference for entropy calculation
Infers entropy levels from system state for E flow
"""
import torch
import torch.nn as nn
from typing import Dict, Any, Optional
import numpy as np


class EntropyModel(nn.Module):
    """
    Neural network model for entropy inference
    Uses Torch to predict system entropy from flow states
    """
    
    def __init__(self, input_dim: int = 8, hidden_dim: int = 32):
        """
        Initialize entropy inference model
        
        Args:
            input_dim: Input feature dimension
            hidden_dim: Hidden layer dimension
        """
        super(EntropyModel, self).__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()  # Output entropy between 0 and 1
        )
        
        self.input_dim = input_dim
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.to(self.device)
        
        # Initialize with random weights
        self._initialize_weights()
        
    def _initialize_weights(self):
        """Initialize network weights"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.zeros_(m.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network
        
        Args:
            x: Input tensor of shape (batch_size, input_dim)
            
        Returns:
            Entropy predictions of shape (batch_size, 1)
        """
        return self.network(x)
    
    def infer_entropy(self, flow_states: Dict[str, Any]) -> float:
        """
        Infer entropy from flow states
        
        Args:
            flow_states: Dictionary containing states from R, B, E, O flows
            
        Returns:
            Inferred entropy value
        """
        # Extract features from flow states
        features = self._extract_features(flow_states)
        
        # Convert to tensor
        x = torch.tensor(features, dtype=torch.float32, device=self.device).unsqueeze(0)
        
        # Inference
        with torch.no_grad():
            entropy = self.forward(x)
            
        return entropy.item()
    
    def _extract_features(self, flow_states: Dict[str, Any]) -> np.ndarray:
        """
        Extract feature vector from flow states
        
        Args:
            flow_states: Dictionary with flow states
            
        Returns:
            Feature vector as numpy array
        """
        features = np.zeros(self.input_dim, dtype=np.float32)
        
        # Extract R flow features
        if "R" in flow_states:
            features[0] = flow_states["R"].get("recursion_depth", 0.0) / 100.0
            features[1] = flow_states["R"].get("reflection_state", 0.0)
            
        # Extract B flow features
        if "B" in flow_states:
            features[2] = flow_states["B"].get("balance", 0.0)
            features[3] = float(flow_states["B"].get("binary_state", 0))
            
        # Extract E flow features
        if "E" in flow_states:
            features[4] = flow_states["E"].get("entropy_level", 0.0)
            features[5] = flow_states["E"].get("energy_state", 0.0)
            
        # Extract O flow features
        if "O" in flow_states:
            features[6] = flow_states["O"].get("optimization_weight", 1.0) / 10.0
            features[7] = flow_states["O"].get("orchestration_factor", 0.0)
            
        return features
    
    def train_step(self, flow_states: Dict[str, Any], target_entropy: float, 
                   optimizer: torch.optim.Optimizer) -> float:
        """
        Perform one training step
        
        Args:
            flow_states: Input flow states
            target_entropy: Target entropy value
            optimizer: Optimizer instance
            
        Returns:
            Training loss
        """
        features = self._extract_features(flow_states)
        x = torch.tensor(features, dtype=torch.float32, device=self.device).unsqueeze(0)
        target = torch.tensor([[target_entropy]], dtype=torch.float32, device=self.device)
        
        # Forward pass
        pred = self.forward(x)
        
        # Compute loss
        loss = nn.functional.mse_loss(pred, target)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        return loss.item()
