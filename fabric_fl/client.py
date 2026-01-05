import numpy as np
import copy
from typing import List, Tuple
from .security import PostQuantumCrypto, HomomorphicEncryption, SecretSharing

class FLClient:
    """
    Federated Learning Client.
    Performs local training, applies Differential Privacy, and securely shares updates.
    """
    
    def __init__(self, 
                 client_id: str, 
                 data: np.ndarray, 
                 labels: np.ndarray,
                 pqc: PostQuantumCrypto,
                 he: HomomorphicEncryption):
        self.client_id = client_id
        self.data = data
        self.labels = labels
        self.pqc = pqc
        self.he = he
        
        # Generate Client Keys
        self.kem_pk, self.kem_sk = self.pqc.generate_kem_keypair()
        self.sig_pk, self.sig_sk = self.pqc.generate_sig_keypair()
        
        # Model Parameters (Local)
        self.model_params = None

    def set_model(self, model_params: np.ndarray):
        """Updates local model with global model."""
        self.model_params = copy.deepcopy(model_params)

    def train(self, epochs: int = 1, lr: float = 0.01):
        """
        Simulates local training (Gradient Descent).
        For prototype, we assume a simple linear model: y = w*x + b
        """
        if self.model_params is None:
            raise ValueError("Model parameters not set.")
            
        # Simplified Training: Linear Regression Gradient Descent
        # model_params is [weights, bias] flattened
        # Assumes data is (N, D) and labels (N,)
        
        n_samples, n_features = self.data.shape
        w = self.model_params[:-1]
        b = self.model_params[-1]
        
        for _ in range(epochs):
            # Forward
            preds = self.data.dot(w) + b
            error = preds - self.labels
            
            # Gradient
            dw = (2/n_samples) * self.data.T.dot(error)
            db = (2/n_samples) * np.sum(error)
            
            # Update
            w -= lr * dw
            b -= lr * db
            
        new_params = np.append(w, b)
        update_vector = new_params - self.model_params
        
        return update_vector

    def apply_dp(self, update_vector: np.ndarray, epsilon: float, max_grad_norm: float) -> np.ndarray:
        """
        Applies Differential Privacy to the update vector.
        1. Norm Clipping
        2. Gaussian Noise addition
        """
        # 1. Norm Clipping
        total_norm = np.linalg.norm(update_vector)
        clip_coef = max_grad_norm / (total_norm + 1e-6)
        if clip_coef < 1:
            update_vector = update_vector * clip_coef
            
        # 2. Add Noise (Gaussian Mechanism)
        # Scale noise by sensitivity (max_grad_norm) and epsilon
        # Improved logic needed for strict privacy accounting, this is a simplified version
        sigma = max_grad_norm * np.sqrt(2 * np.log(1.25 / 1e-5)) / epsilon # Approx formula
        noise = np.random.normal(0, sigma, update_vector.shape)
        
        return update_vector + noise

    def prepare_update(self, update_vector: np.ndarray, secure_mode: bool = True):
        """
        Encrypts and signs the update vector.
        """
        # Encrypt with HE Public Key (managed by HE Context)
        if secure_mode:
            encrypted_update = self.he.encrypt_vector(update_vector.tolist())
            # Serialize for transmission (mock or real)
            payload = self.he.serialize(encrypted_update)
        else:
            payload = update_vector.tobytes()

        # Sign the payload
        signature = self.pqc.sign(payload, self.sig_sk)
        
        return {
            "client_id": self.client_id,
            "payload": payload,
            "signature": signature,
            "public_key": self.sig_pk # Send PK for verification (simulated PKI)
        }
