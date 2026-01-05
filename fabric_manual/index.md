# FABRIC: Secure Federated Learning System
## Technical Manual & Reference Guide

**Version**: 1.0.0
**Date**: 2026-01-05

This manual provides an exhaustive technical breakdown of the FABRIC system. It is divided into four volumes covering Theory, Cryptography, Privacy, and Software Implementation.

## Table of Contents

### [Volume 1: Distributed Optimization Theory](./chapter_1_optimization.md)
*Deep dive into the mathematics of Federated Learning.*
- Problem Formulation & Loss Functions
- Lipschitz Smoothness & Strong Convexity
- Convergence Analysis of FedAvg
- Impact of Non-IID Data & Client Drift
- Adaptive Optimization (FedAdam/Yogi)

### [Volume 2: Cryptographic Foundations](./chapter_2_cryptography.md)
*Detailed analysis of the security protocols.*
- Ring Learning With Errors (RLWE)
- Cyclotomic Polynomial Rings & Number Theoretic Transforms
- CKKS Homomorphic Encryption Scheme (Encoding, Addition, Modulus Switching)
- Post-Quantum Crypto (Module-LWE, Kyber, Dilithium)

### [Volume 3: Privacy, Robustness & Threat Models](./chapter_3_privacy.md)
*Analysis of defense mechanisms.*
- Differential Privacy: Definitions & Gaussian Mechanism Proofs
- Sensitive Analysis & Clipping
- Robust Statistics: Breakdown Points of Mean vs. Median
- Trimmed Mean Estimator
- Gradient Inversion Attacks (Deep Leakage)

### [Volume 4: System Implementation & API](./chapter_4_implementation.md)
*Software engineering reference.*
- Package `fabric_fl` Architecture
- Class References (Client, Server, Aggregator)
- Data Packet Structures
- Simulation Hyperparameters

---

**Executive Summary**
FABRIC combines valid Distributed Optimization theory with state-of-the-art Privacy Enhancing Technologies (PETs). By layering Homomorphic Encryption over Differentially Private updates, verified by Post-Quantum Signatures, it achieves a "Defense-in-Depth" posture suitable for high-assurance environments.
