"""
Entropy Model - Torch-based inference for threat scoring
Simple Linear(1, 1) model with Sigmoid activation
Infers threat score bounded in [0, 1] from anomaly count

Model: torch.nn.Linear(1, 1) with Sigmoid
Input: total_anoms (anomalies from features + genome risk)
Output: threat_score in [0, 1]
"""
import torch
import torch.nn as nn
from typing import Optional
import math


class EntropyModel(nn.Module):
    """
    Simple neural network model for threat/entropy inference
    Uses Torch Linear(1, 1) + Sigmoid to predict threat score
    
    Architecture: Input(1) -> Linear(1, 1) -> Sigmoid -> Output(1)
    """
    
    def __init__(self, ml_weight: float = 0.12):
        """
        Initialize entropy inference model
        
        Args:
            ml_weight: Initial ML weight for the model (default 0.12)
        """
        super(EntropyModel, self).__init__()
        
        # Simple Linear(1, 1) model as specified
        self.model = nn.Linear(1, 1)
        
        # Initialize weight with ml_weight
        self.model.weight.data.fill_(ml_weight)
        self.model.bias.data.fill_(0.0)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.to(self.device)
        
        self.ml_weight = ml_weight
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network
        
        Args:
            x: Input tensor of shape (batch_size, 1) - total anomalies
            
        Returns:
            Threat score predictions of shape (batch_size, 1) bounded in [0, 1]
        """
        # Linear transformation followed by Sigmoid
        return torch.sigmoid(self.model(x))
    
    def infer_threat(self, total_anoms: int) -> float:
        """
        Infer threat score from total anomaly count
        
        Args:
            total_anoms: Total number of anomalies (features + genome risk)
            
        Returns:
            Threat score bounded in [0, 1]
        """
        # Convert anomalies to tensor
        x = torch.tensor([[float(total_anoms)]], dtype=torch.float32, device=self.device)
        
        # Inference with no gradient
        with torch.no_grad():
            threat_score = self.forward(x)
            
        return threat_score.item()
    
    def update_weight(self, new_ml_weight: float):
        """
        Update the ML weight of the model
        
        Args:
            new_ml_weight: New weight value to set
        """
        self.ml_weight = new_ml_weight
        self.model.weight.data.fill_(new_ml_weight)
    
    def train_step(self, total_anoms: int, target_threat: float, 
                   optimizer: torch.optim.Optimizer) -> float:
        """
        Perform one training step using MSE loss
        
        Args:
            total_anoms: Input anomaly count
            target_threat: Target threat score
            optimizer: Optimizer instance
            
        Returns:
            Training loss (MSE)
        """
        x = torch.tensor([[float(total_anoms)]], dtype=torch.float32, device=self.device)
        target = torch.tensor([[target_threat]], dtype=torch.float32, device=self.device)
        
        # Forward pass
        pred = self.forward(x)
        
        # Compute MSE loss
        loss = nn.functional.mse_loss(pred, target)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        return loss.item()
    
    def get_weight(self) -> float:
        """Get current model weight"""
        return self.model.weight.data.item()
    
    def get_bias(self) -> float:
        """Get current model bias"""
        return self.model.bias.data.item()
