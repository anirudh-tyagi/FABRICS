# FABRIC Technical Manual - Vol 3
# Chapter 3: Privacy, Robustness, and Threat Models

## 3.1 Formal Privacy Guarantees

We define privacy using the **Differential Privacy (DP)** framework.

### 3.1.1 Definition
A randomized mechanism $\mathcal{M}: \mathcal{D} \to \mathcal{R}$ satisfies $(\epsilon, \delta)$-DP if for any two adjacent datasets $D, D'$ differing by at most one record:
$$ \Pr[\mathcal{M}(D) \in S] \le e^\epsilon \Pr[\mathcal{M}(D') \in S] + \delta $$

### 3.1.2 The Gaussian Mechanism in Deep Learning
In Federated Learning, the query is the gradient $g(D) = \nabla F(w; D)$.
Since gradients are unbounded, we define the **Sensitivity** relative to a clipping bound $C$.

**Clipping Function**:
$$ \text{clip}(g, C) = g \cdot \min(1, \frac{C}{||g||_2}) $$
The sensitivity of $\sum \text{clip}(g_i, C)$ is exactly $C$.

**Mechanism**:
$$ \tilde{g} = \sum_{i=1}^n \text{clip}(g_i, C) + \mathcal{N}(0, \sigma^2 C^2 \mathbb{I}) $$

**Privacy Accounting (Moments Accountant)**:
We track the privacy loss random variable $L = \ln \frac{\Pr[\mathcal{M}(D)=o]}{\Pr[\mathcal{M}(D')=o]}$.
Standard composition theorems are loose. Using **Rényi Differential Privacy (RDP)** or **Moments Accountant**, we calculate the accumulation over $T$ rounds.
For sampling rate $q = L/N$ and noise $\sigma$, after $T$ steps, $\epsilon \approx q \sqrt{T}$.

## 3.2 Robust Aggregation Theory

We address the **Byzantine Threat Model** where a fraction $\alpha$ of clients send arbitrary malicious vectors.

### 3.2.1 Vulnerability of Mean
The empirical mean $\mu = \frac{1}{n} \sum x_i$ minimizes the squared error sum.
$$ \mu = \arg \min_m \sum ||x_i - m||^2 $$
If a single $x_i \to \infty$, the minimum shifts to $\infty$. The **Breakdown Point** is $1/n \to 0$.

### 3.2.2 Trimmed Mean Analysis
For 1D data, we remove the largest and smallest $\beta n$ points.
Breakdown point is $\beta$.
If attackers control $\alpha < \beta$ fraction, they are always removed.

**Convergence Rate of Trimmed Mean**:
$$ ||\text{TM}(X) - \mu|| \le \mathcal{O}\left(\frac{1}{\sqrt{n(1-2\beta)}}\right) + \text{Bias} $$
The bias depends on the asymmetry of the true distribution. For symmetric (Gaussian) noise, Trimmed Mean is unbiased. For Gradient distributions (often Heavy-Tailed), there is a bias-variance tradeoff.

### 3.2.3 Multi-Dimensional Robustness: Geometric Median
FABRIC's underlying architecture supports geometric robustness as a future extension.
$$ m_{geo} = \arg \min_m \sum_{i=1}^n ||x_i - m||_2 $$
Geometric Median has breakdown point 0.5. Computing it requires Weiszfeld's algorithm (iterative), which is hard to do homomorphically. This justifies our choice of **Coordinate-wise Trimmed Mean** as the default robust aggregator for the hybrid protocol.

## 3.3 Gradient Inversion Attacks (Deep Leakage)

**Theory**: Given gradients $\nabla w$ and the model $w$, an attacker optimizes a dummy input $x'$ to match the gradients.
$$ x^* = \arg \min_{x'} || \nabla F(w; x') - \nabla w ||^2 $$

**Reconstruction**:
1.  Initialize random dummy data $x' \sim \mathcal{N}(0, 1)$.
2.  Compute dummy gradient $\nabla'$.
3.  Update $x' \leftarrow x' - \eta \frac{\partial ||\nabla' - \nabla||^2}{\partial x'}$.
4.  Repeat until convergence.

**Defense**:
DP noise $(\sigma)$ acts as the primary defense.
If $\sigma$ is sufficient, the optimization landscape for the attacker becomes flat or overly noisy, preventing convergence to the true image $x$.
FABRIC's use of **Homomorphic Encryption** adds a layer of absolute defense against the server *performing* this attack, as the server never sees $\nabla w$ in plaintext (in Secure Mode).

---

*(End of Chapter 3 - Privacy and Robustness)*
