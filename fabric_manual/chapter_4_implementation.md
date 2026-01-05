# FABRIC Technical Manual - Vol 4
# Chapter 4: System Implementation & API Reference

## 4.1 Package Structure `fabric_fl`

```
fabric_fl/
├── __init__.py         # Package initialization
├── security.py         # PQC, HE, SecretSharing classes
├── client.py           # FLClient logic
├── server.py           # FLServer and Aggregator logic
├── aggregation.py      # Mathematical aggregation strategies
└── simulation.py       # Verification testbench
```

## 4.2 Class Reference: `FLClient`

The client is the edge worker.

### `__init__(self, client_id, data, labels, pqc, he)`
Initializes security contexts.
- Generates generic Kyber keypair `(pk, sk)` via `pqc.generate_kem_keypair()`.
- Generates Dilithium signing keys via `pqc.generate_sig_keypair()`.

### `train(self, epochs=1, lr=0.01)`
Performs local SGD.
- **Input**: `self.model_params` (synced from server).
- **Process**:
    - Iterate `epochs` times.
    - Compute gradient $\nabla \mathcal{L}$.
    - Update $w \leftarrow w - \eta \nabla \mathcal{L}$.
- **Output**: Delta vector $\Delta w$.

### `apply_dp(self, update_vector, epsilon, max_grad_norm)`
- Clips vector: $v' = v / \max(1, ||v||/C)$.
- Adds noise: $v'' = v' + \mathcal{N}(0, \sigma^2)$.

## 4.3 Class Reference: `FLServer`

The central coordinator.

### `aggregate_updates(self, updates_payloads)`
Core logic loop.
1.  **Verify**: Iterates payloads, verifies `pqc.verify(payload, signature)`.
2.  **Route**:
    - If `strategy == 'secure_sum'`, passes encrypted vectors to `SecureWeightedAverage`.
    - If `strategy == 'trimmed_mean'`, simulates trusted execution environment decryption, then passes to `TrimmedMean`.
3.  **Apply**: Updates `self.global_model`.

## 4.4 Class Reference: `HomomorphicEncryption` (Wrapper)

Wraps `tenseal` functionality.

### `encrypt_vector(self, vector)`
- Creates a `tenserl.ckks_vector`.
- Automatically handles encoding (Canonical Embedding) and scale management.

### `pad_vector(self, vector, target_size)`
(Internal helper)
CKKS batches operations into slots ($N/2$). If input vector is smaller, we pad with zeros to maximize throughput and allow SIMD operations.

## 4.5 Data Packet Structure

The communication protocol uses standard Python dictionaries (JSON-serializable barring the bytes).

```json
{
    "client_id": "client_01",
    "public_key": "<bytes: Dilithium PK>",
    "payload": "<bytes: Serialized CKKS Ciphertext>",
    "signature": "<bytes: Dilithium Signature of payload>",
    "metadata": {
        "data_size": 100,
        "clipping_norm": 1.0
    }
}
```

## 4.6 Simulation Parameters

The provided `simulation.py` runs with the following hyperparameters:
- **Clients**: 3
- **Data Distribution**: Synthetic Linear $y = 2x + 1 + \mathcal{N}(0, 0.1)$. IID.
- **Local Epochs**: 5
- **Learning Rate**: 0.1
- **DP Epsilon**: 1.0
- **DP Norm**: 1.0
- **Security**: Mocked PQC/HE contexts (for portability) maintaining interface compatibility with real libraries.

---

*(End of Chapter 4 - Implementation)*
