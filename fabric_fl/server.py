import numpy as np
from typing import List, Dict, Any
from .security import PostQuantumCrypto, HomomorphicEncryption
from .aggregation import SecureWeightedAverage, TrimmedMean

class FLServer:
    """
    Federated Learning Server.
    Orchestrates the training rounds, aggregates updates, and maintains the global model.
    """
    
    def __init__(self, 
                 global_model_params: np.ndarray, 
                 pqc: PostQuantumCrypto, 
                 he: HomomorphicEncryption,
                 aggregation_strategy: str = "secure_sum"):
        self.global_model = global_model_params
        self.pqc = pqc
        self.he = he
        self.clients = {}
        
        # Aggregation Strategies
        self.secure_aggregator = SecureWeightedAverage(he)
        self.robust_aggregator = TrimmedMean(trim_ratio=0.2) # Example 20% trim
        self.strategy = aggregation_strategy

    def register_client(self, client_id: str, public_key: bytes):
        """Registers a client with their PQC public key."""
        self.clients[client_id] = {'pk': public_key}
        # print(f"[Server] Registered client {client_id}")

    def verify_update(self, update_data: Dict[str, Any]) -> bool:
        """
        Verifies the digital signature of the update using PQC.
        """
        client_id = update_data['client_id']
        payload = update_data['payload']
        signature = update_data['signature']
        client_pk = update_data['public_key'] # In real scenario, look up registered key
        
        return self.pqc.verify(payload, signature, client_pk)

    def aggregate_updates(self, updates_payloads: List[Dict[str, Any]]):
        """
        Aggregates updates from clients based on the selected strategy.
        """
        valid_updates = []
        for update in updates_payloads:
            if self.verify_update(update):
                # Deserialize payload
                if self.strategy == "secure_sum":
                    # Keep encrypted
                    enc_vec = self.he.deserialize(update['payload'])
                    valid_updates.append(enc_vec)
                elif self.strategy == "trimmed_mean":
                    # Decrypt first (Server must see values for Robust Aggregation)
                    # Note: secure_mode=False or Server has Decrypt capability in this simulation context
                    # In this simulation, we assume server CAN decrypt if needed for Robustness check
                    enc_vec = self.he.deserialize(update['payload'])
                    dec_vec = self.he.decrypt_vector(enc_vec)
                    valid_updates.append(np.array(dec_vec))
        
        if not valid_updates:
            print("[Server] No valid updates received.")
            return
        
        # Perform Aggregation
        aggregated_result = None
        if self.strategy == "secure_sum":
            # Sum encrypted vectors
            encrypted_sum = self.secure_aggregator.aggregate(valid_updates)
            # Decrypt result *only* (Global Model Update)
            decrypted_sum = self.he.decrypt_vector(encrypted_sum)
            # Average (divide by N)
            aggregated_result = np.array(decrypted_sum) / len(valid_updates)
            
        elif self.strategy == "trimmed_mean":
            aggregated_result = self.robust_aggregator.aggregate(valid_updates)
            
        # Update Global Model
        if aggregated_result is not None:
            self.global_model += aggregated_result
            # print("[Server] Global model updated.")
            
    def get_global_model(self):
        return self.global_model
