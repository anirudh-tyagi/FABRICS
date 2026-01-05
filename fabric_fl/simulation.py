import numpy as np
import sys
import os

# Ensure we can import fabric_fl
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fabric_fl.security import PostQuantumCrypto, HomomorphicEncryption
from fabric_fl.client import FLClient
from fabric_fl.server import FLServer

def run_simulation():
    print("="*50)
    print("FABRIC Federated Learning System Simulation")
    print("="*50)

    # 1. Setup Security Infrastructure
    print("\n[Init] Setting up Security Contexts...")
    pqc = PostQuantumCrypto() # Dilithium / Kyber
    he = HomomorphicEncryption() # CKKS
    print("  > PQC and HE Contexts initialized.")

    # 2. Setup Data (Linear Regression: y = 2x + 1)
    # Global Model Init: [weight=0.0, bias=0.0]
    initial_model = np.array([0.0, 0.0])
    
    # 3. Instantiate Server
    server = FLServer(initial_model, pqc, he, aggregation_strategy="secure_sum")
    print(f"\n[Server] Initialized with strategy: {server.strategy}")
    print(f"  > Initial Model: {server.get_global_model()}")

    # 4. Instantiate Clients
    n_clients = 3
    clients = []
    print(f"\n[Clients] Instantiating {n_clients} clients...")
    for i in range(n_clients):
        # Generate synthetic data
        X = np.random.rand(10, 1) # 10 samples
        noise = np.random.normal(0, 0.1, (10, 1))
        y = 2 * X + 1 + noise
        
        client = FLClient(f"client_{i+1}", X, y.flatten(), pqc, he)
        clients.append(client)
        server.register_client(client.client_id, client.sig_pk)
        print(f"  > {client.client_id} registered.")

    # 5. Training Round
    print("\n[Round 1] Starting Training Round...")
    
    # a. Broadcast Model
    global_model = server.get_global_model()
    
    updates = []
    for client in clients:
        # b. Client Update
        client.set_model(global_model)
        update_vec = client.train(epochs=5, lr=0.1)
        
        # c. Apply Privacy (DP)
        update_vec_dp = client.apply_dp(update_vec, epsilon=1.0, max_grad_norm=1.0)
        
        # d. Encrypt & Sign
        payload = client.prepare_update(update_vec_dp, secure_mode=True)
        updates.append(payload)
        
        # Check raw update for logging (not seen by server)
        # print(f"  > {client.client_id} computed update (raw): {update_vec}")

    # 6. Aggregation
    print("\n[Server] Aggregating Updates...")
    server.aggregate_updates(updates)
    
    # 7. Results
    new_model = server.get_global_model()
    print(f"\n[Result] Updated Global Model: {new_model}")
    print("  > Target Model: [2.0, 1.0]")
    
    # Verification assertions
    assert len(new_model) == 2
    assert new_model[0] != 0.0, "Model weight should have updated"
    assert new_model[1] != 0.0, "Model bias should have updated"
    
    print("\n[Success] Simulation completed successfully. System is operational.")

if __name__ == "__main__":
    run_simulation()
