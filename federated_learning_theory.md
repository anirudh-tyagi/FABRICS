# FABRIC: Secure & Robust Federated Learning Architecture
## Theoretical Foundations, Machine Learning Algorithms, and Mathematics

This document serves as the "Master Theory" whitepaper. It details the comprehensive mathematical framework of the FABRIC Federated Learning system, ranging from the fundamental Machine Learning algorithms to the advanced Cryptographic protocols.

---

## 1. Machine Learning Algorithms: Theory & Math

Federated Learning is, at its core, distributed optimization. Here we define the specific algorithms used by the clients.

### 1.1 Linear Regression (The Prototype Model)

The simulation currently uses Linear Regression, the "Hello World" of ML, ideal for proving convergence properties.

**Theory**: We model the relationship between input vectors $x \in \mathbb{R}^d$ and target scalars $y \in \mathbb{R}$ as a linear combination.
**Model**: $\hat{y} = w^T x + b$
**Parameters**: $\theta = \{w, b\}$

**Loss Function (Mean Squared Error - MSE)**:
We minimize the squared difference between predictions and actuals.
$$ J(\theta) = \frac{1}{2m} \sum_{i=1}^m (\hat{y}^{(i)} - y^{(i)})^2 $$

**Gradient Descent Derivation**:
To update weights, we compute the partial derivative of the cost function w.r.t parameters using the Chain Rule.
$$ \frac{\partial J}{\partial w} = \frac{1}{m} \sum_{i=1}^m (\hat{y}^{(i)} - y^{(i)}) x^{(i)} $$
$$ \frac{\partial J}{\partial b} = \frac{1}{m} \sum_{i=1}^m (\hat{y}^{(i)} - y^{(i)}) $$

**Update Rule**:
$$ w := w - \alpha \frac{\partial J}{\partial w} $$
where $\alpha$ is the learning rate.

### 1.2 Deep Neural Networks (Supported Design)

While the prototype uses Linear Regression, the `train()` method in `FLClient` supports generalized Deep Learning via **Backpropagation**.

**Forward Propagation**:
For layer $l$, with activation function $\phi$ (e.g., ReLU):
$$ z^{[l]} = W^{[l]} a^{[l-1]} + b^{[l]} $$
$$ a^{[l]} = \phi(z^{[l]}) $$

**Backward Propagation (The Learning Engine)**:
We propagate the error $\delta$ backwards from the output layer $L$.
$$ \delta^{[L]} = \nabla_a \mathcal{L} \odot \phi'(z^{[L]}) $$
For hidden layers $l$:
$$ \delta^{[l]} = ((W^{[l+1]})^T \delta^{[l+1]}) \odot \phi'(z^{[l]}) $$

**Gradients**:
$$ \frac{\partial \mathcal{L}}{\partial W^{[l]}} = \delta^{[l]} (a^{[l-1]})^T $$

In FABRIC, these gradients are what comprise the **Update** payload.

---

## 2. Federated Optimization

### 2.1 The Federated Problem
We wish to minimize a global objective $f(w)$ which is a weighted average of local objectives $F_k(w)$:
$$ \min_{w} f(w) = \sum_{k=1}^K p_k F_k(w) $$
where $p_k = \frac{n_k}{N}$.

### 2.2 Federated Averaging (FedAvg) Mathematical Proof
FedAvg approximates a global SGD step by averaging individual SGD steps.
Instead of: $w_{t+1} = w_t - \eta \sum p_k \nabla F_k(w_t)$ (Global SGD),
FedAvg does: $w_{t+1}^k = w_t - \eta \nabla F_k(w_t)$ (Local), then $w_{t+1} = \sum p_k w_{t+1}^k$.

These are mathematically equivalent for linear functions and convex approximations for non-linear ones. FABRIC relies on this convergence property.

---

## 3. Privacy Mathematics: Differential Privacy

We use the **Gaussian Mechanism** to formally guarantee privacy.

**Goal**: Make the output of the client indistinguishable whether any specific data point $(x, y)$ was used or not.

**Algorithm**:
1.  **Sensitivity Bounding**: We define strict bounds on the gradient norm.
    $$ \bar{g} = g / \max(1, \frac{||g||_2}{C}) $$
    This forces the sensitivity $S_f \le C$.
2.  **Noise Injection**:
    $$ \mathcal{M}(D) = f(D) + \mathcal{N}(0, S_f^2 \sigma^2) $$

**Privacy Loss Analysis**:
For noise scale $\sigma \ge 1$ and appropriate $C$, the mechanism is $(\epsilon, \delta)$-DP. The privacy budget accumulates over rounds (composition theorems), which is why we must balance noise level vs. model utility.

---

## 4. Cryptographic Mathematics (Under the Hood)

### 4.1 Homomorphic Encryption: CKKS
The CKKS scheme allows us to add encrypted numbers: $\text{Enc}(x) + \text{Enc}(y) = \text{Enc}(x+y)$.

**The Ring**: Computations happen in a polynomial ring $\mathcal{R}_q = \mathbb{Z}_q[X] / (X^N + 1)$.
**Encoding**: A vector of real numbers $z \in \mathbb{C}^{N/2}$ is encoded into a plaintext polynomial $m(X)$ via Canonical Embeddings.
**Encryption**:
$$ c = (c_0, c_1) = (v \cdot s + m + e, -v) $$
where $s$ is the secret key, $v$ is a random polynomial (RLWE sample), and $e$ is error.
**Addition**:
Component-wise addition of polynomials:
$$ c_{add} = (c_0 + c'_0, c_1 + c'_1) $$
When decrypted with $s$, the errors add up ($e + e'$) but remain small enough to be discarded during decoding unless they overflow.

### 4.2 Post-Quantum: Lattice Cryptography
**MLWE (Module Learning With Errors)**:
Given a matrix $A$ over a ring and a vector $t = As + e$, finding $s$ is computationally infeasible, even for quantum computers using Shor's algorithm.
- **Kyber**: Uses MLWE for Key Encapsulation.
- **Dilithium**: Uses MLWE/SIS for Signatures.
FABRIC uses these problems as the "Hardness Assumption" foundation.

---

## 5. Robust Statistics: Trimmed Mean

When the "blind trust" of Homomorphic Encryption is effectively essentially trading robustness for privacy, we offer **Trimmed Mean**.

**Statistical Reasoning**:
The mean has a **breakdown point** of 0. One single value can move the mean arbitrarily.
$$ \bar{x} = \frac{1}{N} \sum x_i $$
If $x_k \to \infty$, then $\bar{x} \to \infty$.

The **Trimmed Mean** removes the top and bottom $\beta$-quantiles.
$$ \mu_{tm} = \frac{1}{N - 2k} \sum_{i=k+1}^{N-k} x_{(i)} $$
where $x_{(i)}$ are the sorted observations.
This estimator is **Robust**. It ignores the behavior of the $\beta \%$ most extreme clients, assuming they are attackers (poisoning).
