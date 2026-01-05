import numpy as np
import os
import secrets
from typing import List, Tuple, Any, Optional

# --- Post-Quantum Cryptography Wrapper ---
class PostQuantumCrypto:
    """
    Interface for Post-Quantum Cryptography (Kyber for KEM, Dilithium for Signatures).
    
    > [!NOTE]
    > In a production environment, this would wrap `liboqs` or `pqc` bindings.
    > identifying algorithms like 'Kyber512' and 'Dilithium2'.
    > Here, we provide a functional mock for protocol verification.
    """
    
    def __init__(self, kem_alg: str = "Kyber512", sig_alg: str = "Dilithium2"):
        self.kem_alg = kem_alg
        self.sig_alg = sig_alg

    def generate_kem_keypair(self) -> Tuple[bytes, bytes]:
        """Generates a public/private keypair for Key Encapsulation."""
        # Mocking keys
        pk = f"mock_kyber_pk_{secrets.token_hex(8)}".encode()
        sk = f"mock_kyber_sk_{secrets.token_hex(8)}".encode()
        return pk, sk

    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """
        Generates a shared secret and encapsulates it for the given public key.
        Returns (ciphertext, shared_secret).
        """
        # Mock encapsulation
        shared_secret = secrets.token_bytes(32)
        # In reality, ciphertext depends on pk and randomly generated secret
        ciphertext = f"mock_kyber_ct_for_{public_key.decode()}_{secrets.token_hex(4)}".encode()
        return ciphertext, shared_secret

    def decapsulate(self, ciphertext: bytes, private_key: bytes) -> bytes:
        """Decapsulates the shared secret using the private key."""
        # In a mock, we can't 'recover' the random secret without storage state or math.
        # For simulation, we assume the system orchestrator handles the consistency,
        # OR we embed the secret in the ciphertext for this mock to work statistically.
        # Let's simple-mock it:
        # NOTE: Real decapsulation would strictly use math.
        return b"mock_shared_secret_32bytes_value"

    def generate_sig_keypair(self) -> Tuple[bytes, bytes]:
        """Generates a public/private keypair for Signatures."""
        pk = f"mock_dilithium_pk_{secrets.token_hex(8)}".encode()
        sk = f"mock_dilithium_sk_{secrets.token_hex(8)}".encode()
        return pk, sk

    def sign(self, message: bytes, private_key: bytes) -> bytes:
        """Signs a message."""
        # Signature is a hash of message + sk (mock)
        return f"sig_{hash(message)}_{private_key.decode()}".encode()

    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verifies a signature."""
        # Mock verification always passes if signature looks corresponding (simple simulation)
        # In real PQC, this performs math check.
        return signature.startswith(b"sig_")


# --- Homomorphic Encryption Interface (CKKS) ---
class HomomorphicEncryption:
    """
    Interface for Homomorphic Encryption using CKKS scheme.
    Design assumes usage of `tenseal` library.
    """
    
    def __init__(self, context_params: dict = None):
        if context_params is None:
            # Standard CKKS params
            self.poly_modulus_degree = 8192
            self.coeff_mod_bit_sizes = [60, 40, 40, 60]
        self.context = self._create_context()

    def _create_context(self):
        """Creates TenSEAL context or Mock context."""
        try:
            import tenseal as ts
            context = ts.context(
                ts.SCHEME_TYPE.CKKS,
                poly_modulus_degree=self.poly_modulus_degree,
                coeff_mod_bit_sizes=self.coeff_mod_bit_sizes
            )
            context.global_scale = 2**40
            context.generate_galois_keys()
            return context
        except ImportError:
            # print("[WARNING] TenSEAL not found. Using MockHEContext.")
            return MockHEContext()

    def encrypt_vector(self, vector: List[float]):
        """Encrypts a list of floats."""
        if isinstance(self.context, MockHEContext):
            return self.context.encrypt(vector)
        import tenseal as ts
        return ts.ckks_vector(self.context, vector)

    def decrypt_vector(self, enc_vector) -> List[float]:
        """Decrypts an encrypted vector."""
        if isinstance(self.context, MockHEContext):
            return self.context.decrypt(enc_vector)
        return enc_vector.decrypt()
    
    def add(self, enc_vec1, enc_vec2):
        """Homomorphic addition."""
        return enc_vec1 + enc_vec2
    
    def serialize(self, enc_vector) -> bytes:
        """Serializes encrypted vector for network transmission."""
        if isinstance(self.context, MockHEContext):
            import pickle
            return pickle.dumps(enc_vector)
        return enc_vector.serialize()

    def deserialize(self, data: bytes):
        """Deserializes encrypted vector."""
        if isinstance(self.context, MockHEContext):
            import pickle
            return pickle.loads(data)
        import tenseal as ts
        return ts.ckks_vector_from(self.context, data)


class MockHEContext:
    """Mock context to simulate HE operations when TenSEAL is missing."""
    class MockVector:
        def __init__(self, data):
            self.data = np.array(data)
        def __add__(self, other):
            return MockHEContext.MockVector(self.data + other.data)
        def __sub__(self, other):
             return MockHEContext.MockVector(self.data - other.data)
        def __mul__(self, scalar):
             return MockHEContext.MockVector(self.data * scalar)
         
    def encrypt(self, vector):
        # We store plaintext but wrap it to simulate "encryption" object
        return self.MockVector(vector)
    
    def decrypt(self, mock_vector):
        return mock_vector.data.tolist()


# --- Shamir Secret Sharing ---
class SecretSharing:
    """
    Implementation of Shamir's Secret Sharing over finite fields.
    Used for Secure Aggregation (e.g. splitting a seed or private mask).
    """
    
    def __init__(self, prime: int = 2**521 - 1): # Mersenne prime
        self.prime = prime

    def split_secret(self, secret: int, n: int, k: int) -> List[Tuple[int, int]]:
        """
        Splits an integer secret into n shares, requiring k to reconstruct.
        Returns list of (index, share).
        """
        # f(x) = secret + a1*x + ... + ak-1*x^(k-1)
        coeffs = [secret] + [secrets.randbelow(self.prime) for _ in range(k - 1)]
        
        shares = []
        for i in range(1, n + 1):
            x = i
            y = sum([c * (x**exp) for exp, c in enumerate(coeffs)]) % self.prime
            shares.append((x, y))
        return shares

    def reconstruct_secret(self, shares: List[Tuple[int, int]]) -> int:
        """
        Reconstructs secret from k shares using Lagrange interpolation.
        """
        x_s, y_s = zip(*shares)
        k = len(shares)
        
        secret = 0
        for j in range(k):
            # L_j(0) = product( (0 - x_m)/(x_j - x_m) ) for m != j
            numerator = 1
            denominator = 1
            for m in range(k):
                if m == j:
                    continue
                numerator = (numerator * (0 - x_s[m])) % self.prime
                denominator = (denominator * (x_s[j] - x_s[m])) % self.prime
            
            # modular inverse
            lagrange_coeff = (numerator * pow(denominator, -1, self.prime)) % self.prime
            secret = (secret + y_s[j] * lagrange_coeff) % self.prime
            
        return secret
