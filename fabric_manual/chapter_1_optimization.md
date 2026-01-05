# FABRIC Technical Manual - Vol 1
# Chapter 1: Distributed Optimization Theory

## 1.1 Introduction to Federated Optimization

Federated Learning (FL) fundamentally differs from traditional distributed optimization due to specific constraints:
1.  **Massively Distributed**: $K$ can be $10^6+$.
2.  **Non-IID Data**: $\mathcal{D}_k \nsim \mathcal{P}$.
3.  **Unbalanced Data**: $n_k$ varies by orders of magnitude.
4.  **Limited Communication**: Communication is the bottleneck, not compute.

We model the problem as:
$$ \min_{w \in \mathbb{R}^d} f(w) \quad \text{where} \quad f(w) \triangleq \sum_{k=1}^K p_k F_k(w) $$
$$ F_k(w) \triangleq \frac{1}{n_k} \sum_{i \in \mathcal{D}_k} \ell(w; x_i, y_i) $$

Here, $p_k \ge 0$ and $\sum_k p_k = 1$. Usually $p_k = n_k/N$.

## 1.2 Mathematical Assumptions

To provide guarantees, we assume specific properties of the loss function $F_k$.

### Assumption 1: L-Smoothness
Each local objective $F_k$ is $L$-smooth:
$$ ||\nabla F_k(v) - \nabla F_k(w)|| \le L ||v - w||, \quad \forall v, w $$
This implies a quadratic upper bound on the function growth:
$$ F_k(v) \le F_k(w) + \langle \nabla F_k(w), v - w \rangle + \frac{L}{2}||v - w||^2 $$

### Assumption 2: $\mu$-Strong Convexity
Each local objective $F_k$ is $\mu$-strongly convex:
$$ F_k(v) \ge F_k(w) + \langle \nabla F_k(w), v - w \rangle + \frac{\mu}{2}||v - w||^2 $$
This implies a quadratic lower bound.

### Assumption 3: Bounded Variance
The stochastic gradients $g_k(w) = \nabla F_k(w; \xi)$ have bounded variance $\sigma_k^2$:
$$ \mathbb{E}[||g_k(w) - \nabla F_k(w)||^2] \le \sigma_k^2 $$

### Assumption 4: Bounded Gradient Divergence (Non-IID Measure)
The deviation of local gradients from the global gradient is bounded by $\kappa$:
$$ ||\nabla F_k(w) - \nabla f(w)|| \le \kappa $$
This quantifies the "Non-IID-ness". If data is IID, $\mathbb{E}[\nabla F_k] = \nabla f$, so this bound relates to sampling noise. In Non-IID, it relates to distribution shift.

## 1.3 Convergence Analysis of FedAvg

We analyze **FedAvg** with partial participation.
Let $\mathcal{S}_t$ be the set of $K \cdot C$ clients sampled at round $t$.

**Update Rule**:
$$ w_{t+1} \leftarrow w_t - \eta \sum_{k \in \mathcal{S}_t} \frac{n_k}{N} \sum_{\tau=1}^E g_k(w_{t, \tau}) $$

### Theorem 1: Convergence Rate (Convex Case)
Let $\eta_t = \frac{2}{\mu(t+\gamma)}$. For $\mu$-strongly convex functions, FedAvg converges to the global optimum $w^*$ with expected error:
$$ \mathbb{E}[f(w_T)] - f(w^*) \le \mathcal{O}\left(\frac{L}{\gamma + T}\right) + \mathcal{O}\left(\frac{\sum p_k^2 \sigma_k^2 + \kappa^2}{\mu^2 T}\right) $$

**Proof Sketch**:
1.  **One Step Bound**: We expand $||w_{t+1} - w^*||^2$.
2.  **Decomposition**: The term splits into a "gradient descent" reduction part and a "variance" addition part.
3.  **Client Drift**: The term involving $E$ (local epochs) introduces a drift error. The local model $w_{t, \tau}^k$ moves towards the local optimum $w_k^*$. The distance $||w_{t, \tau}^k - w_t||$ is bounded by $\mathcal{O}(\eta E G)$.
4.  **Aggregation**: Averaging reduces variance by factor $N$, but the bias from client drift remains $\mathcal{O}(\eta^2 E^2 G^2)$.

### 1.4 The Effect of Heavy-Tailed Noise
In differential privacy, we add noise $z \sim \mathcal{N}(0, B^2 \sigma^2)$.
This increases the effective variance $\hat{\sigma}^2 = \sigma_{data}^2 + \sigma_{DP}^2$.
The convergence slows down:
$$ T_{DP} \approx T_{clean} \cdot \left(1 + \frac{\sigma_{DP}^2}{\sigma_{data}^2}\right) $$
To maintain utility, we must increase $N$ (clients per round) or $T$ (rounds).

## 1.5 Adaptive Optimization (FedAdam, FedYogi)
To combat heterogeneity, we can apply Adam-style momentum at the **server** level.
$$ m_{t+1} \leftarrow \beta_1 m_t + (1-\beta_1) \Delta w_t $$
$$ v_{t+1} \leftarrow \beta_2 v_t + (1-\beta_2) \Delta w_t^2 $$
$$ w_{t+1} \leftarrow w_t - \eta \frac{m_{t+1}}{\sqrt{v_{t+1}} + \epsilon} $$
FABRIC supports this via the `Server` class extensibility.

---

*(End of Chapter 1 - Distributed Optimization Theory)*
