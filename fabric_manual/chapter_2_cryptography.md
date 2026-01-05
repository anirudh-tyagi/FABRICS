# FABRIC Technical Manual - Vol 2
# Chapter 2: Cryptographic Foundations

## 2.1 Ring Learning With Errors (RLWE)

The security of both our Homomorphic Encryption (CKKS) and Post-Quantum systems relies on the RLWE hardness assumption.

### 2.1.1 Algebraic Structure
We work over the cyclotomic ring $\mathcal{R} = \mathbb{Z}[X] / (X^N + 1)$ where $N$ is a power of 2 (e.g., 4096, 8192).
Operations are modulo a large integer $q$ (ciphertext modulus).
The space is $\mathcal{R}_q = \mathbb{Z}_q[X] / (X^N + 1)$.

**Why this ring?**
Multiplying polynomials in this ring corresponds to efficient convolution operations, implementable via **Number Theoretic Transform (NTT)** in $\mathcal{O}(N \log N)$ time, whereas standard matrix multiplication is $\mathcal{O}(N^{2.37})$.

### 2.1.2 The RLWE Distribution
Let $s(X) \in \mathcal{R}_q$ be a secret polynomial with small coefficients (e.g., ternary $\{-1, 0, 1\}$).
Let $a(X) \leftarrow \mathcal{U}(\mathcal{R}_q)$ be a uniform random polynomial.
Let $e(X) \leftarrow \chi$ be a small error polynomial drawn from a discrete Gaussian distribution.

An RLWE sample is the pair $(a, b)$ where:
$$ b(X) = a(X) \cdot s(X) + e(X) \pmod q $$

**Decision RLWE Problem**: Distinguish $(a, b)$ from $(a, u)$ where $u$ is uniform random.
**Search RLWE Problem**: Given many pairs $(a_i, b_i)$, recover $s$.

## 2.2 Homomorphic Encryption: CKKS Scheme

CKKS (Cheon-Kim-Kim-Song) is designed for **Approximate Arithmetic** over complex numbers.

### 2.2.1 Canonical Embedding
We need to map a vector $z \in \mathbb{C}^{N/2}$ to a polynomial.
The cyclotomic polynomial $\Phi_M(X) = X^N+1$ has $N$ primitive roots of unity $\zeta_j$.
The canonical embedding $\sigma: \mathcal{R} \to \mathbb{C}^N$ evaluates the polynomial at these roots:
$$ \sigma(m) = (m(\zeta_0), \dots, m(\zeta_{N-1})) $$
Using the inverse $\sigma^{-1}$, we encode data into the ring. $\Delta$ is a scaling factor (e.g., $2^{40}$) to preserve precision during integer rounding.
$$ m(X) = \lfloor \Delta \cdot \sigma^{-1}(z) \rceil $$

### 2.2.2 Encryption Algorithm
Given Public Key $pk = (b, a) = (-as+e, a)$:
1. Sample $v \leftarrow \{0, 1\}^N$ (ephemeral key), $e_0, e_1 \leftarrow \chi$ (errors).
2. Compute $c_0 = v \cdot b + m + e_0 \pmod q$.
3. Compute $c_1 = v \cdot a + e_1 \pmod q$.
Ciphertext $ct = (c_0, c_1)$.

### 2.2.3 Homomorphic Addition
Given $ct = (c_0, c_1)$ and $ct' = (c'_0, c'_1)$:
$$ ct_{add} = (c_0+c'_0 \pmod q, c_1+c'_1 \pmod q) $$
Correctness:
$$ [c_0+c'_0] + [c_1+c'_1]s = (c_0+c_1s) + (c'_0+c'_1s) \approx m + m' $$
The errors add up: $e_{new} = e + e'$.
If $||e_{new}|| < q/4$, decryption is successful.

### 2.2.4 Rescaling and Modulus Switching
In CKKS, multiplying two ciphertexts squares the scale factor $\Delta \to \Delta^2$.
To manage size, we use **Modulus Switching**:
Scale $ct \pmod q$ down to $ct' \pmod {q'}$ where $q' \approx q/\Delta$.
$$ c' = \lfloor \frac{q'}{q} c \rceil $$
This effectively divides the message (and noise) by $\Delta$, returning the scale to $\Delta$.

## 2.3 Post-Quantum Signatures: Dilithium (Module-LWE)

Dilithium acts on vectors of polynomials (Modules) rather than single ring elements.
Module $M = \mathcal{R}_q^k$.

### Scheme Logic
KeyGen:
$A \in \mathcal{R}_q^{k \times \ell}$.
$s_1 \in \mathcal{R}_q^\ell, s_2 \in \mathcal{R}_q^k$ (small secrets).
$t = As_1 + s_2$.
$pk = (A, t)$, $sk = (A, t, s_1, s_2)$.

Signing (Fiat-Shamir heuristics):
1. Sample masking vector $y$.
2. Compute $w_1 = \text{HighBits}(Ay)$.
3. Compute challenge $c = H(M || w_1)$.
4. Compute potentially signature $z = y + cs_1$.
5. Rejection Sampling: If $z$ is too large or creates security leaks, restart with new $y$.
Why Rejection? To make the distribution of $z$ independent of secret $s_1$.

---

*(End of Chapter 2 - Cryptographic Foundations)*
