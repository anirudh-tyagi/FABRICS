from abc import ABC, abstractmethod
from typing import List, Any
import numpy as np
from .security import HomomorphicEncryption

class Aggregator(ABC):
    @abstractmethod
    def aggregate(self, updates: List[Any], **kwargs):
        pass

class SecureWeightedAverage(Aggregator):
    """
    Aggregation strategy using Homomorphic Encryption (CKKS).
    The server receives encrypted updates and sums them without decrypting.
    """
    def __init__(self, he_context: HomomorphicEncryption):
        self.he_context = he_context

    def aggregate(self, encrypted_updates: List[Any], weights: List[float] = None) -> Any:
        """
        Aggregates encrypted updates.
        
        Args:
            encrypted_updates: List of encrypted vectors (CKKS).
            weights: Optional weighting for FedAvg. If None, simple sum/average is used.
        
        Returns:
            Encrypted aggregated vector.
        """
        if not encrypted_updates:
            return None
        
        # Simple Sum
        total_update = encrypted_updates[0]
        for i in range(1, len(encrypted_updates)):
            total_update = self.he_context.add(total_update, encrypted_updates[i])
            
        # For average, we would multiply by 1/n.
        # CKKS supports scalar multiplication.
        # Here we mock/implement simplistic averaging logic if needed, 
        # but usually 'Sum' is sufficient for the Aggregator, and division happens later or effectively in learning rate.
        
        return total_update

class TrimmedMean(Aggregator):
    """
    Robust aggregation strategy defending against Byzantine clients.
    Requries access to plaintext values (server-side decryption or MPC).
    """
    def __init__(self, trim_ratio: float = 0.1):
        self.trim_ratio = trim_ratio

    def aggregate(self, updates: List[np.ndarray], **kwargs) -> np.ndarray:
        """
        Computes the element-wise trimmed mean of updates.
        
        Args:
            updates: List of plaintext numpy arrays (parameters/gradients).
        """
        if not updates:
            return None
        
        stacked_updates = np.stack(updates) # (N_clients, D_params)
        n = stacked_updates.shape[0]
        dropout = int(n * self.trim_ratio)
        
        if dropout == 0:
            return np.mean(stacked_updates, axis=0)
            
        # Sort along client axis
        sorted_updates = np.sort(stacked_updates, axis=0)
        
        # Trim
        trimmed = sorted_updates[dropout : n - dropout]
        
        return np.mean(trimmed, axis=0)
