# 📊 Portfolio Optimizer (Black-Litterman + PyPortfolioOpt)

This project implements a quantitative portfolio optimization model using:

- Black-Litterman
- Robust covariance (Ledoit-Wolf)
- Sharpe maximization
- Discrete allocation

# 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/m-m-legend/analise-carteira.git
cd analise-carteira
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

### 4. Access in browser

```
http://127.0.0.1:5000
```

---

### 💡 Notes

* Python 3.9+ is required
* The application fetches data via the internet (Yahoo Finance API)
* The first run may take longer due to data download

------------------------------------------------------------------------

# 🧠 Core Concepts

## 🔹 Portfolio

Represents what you **already own**.

Format:

    TICKER: quantity

Example:

    PETR4.SA: 12
    ITSA4.SA: 2

✔️ Used for:
- Calculating current value
- Defining rebalancing

------------------------------------------------------------------------

## 🔹 Universe

Represents the set of assets the model **can choose from**.

Example:

    PETR4.SA
    VALE3.SA
    IVVB11.SA
    AAPL34.SA

✔️ Rules:
- Every asset in the portfolio **must be in the universe**
- The model only allocates among assets in the universe

------------------------------------------------------------------------

## 🔹 Views

Return expectations (Black-Litterman)

Format:

    TICKER: expected return

Example:

    PETR4.SA: 0.16
    NVDC34.SA: 0.18

✔️ Interpretation:
- Influence the model
- Do not guarantee high weight (risk still matters)

------------------------------------------------------------------------

# 📊 Model Outputs

## 🟦 Weights

Ideal (theoretical) allocation

- Percentage of capital
- Result of optimization

------------------------------------------------------------------------

## 🟨 Rebalancing

Practical allocation

- Quantity of assets to hold
- Considers real-world constraints

------------------------------------------------------------------------

## 🟩 Diversification

Average correlation score

- Shows assets less correlated with your current portfolio
- Used for **exploration**, not direct decision-making

------------------------------------------------------------------------

# 🔗 Relationship Between Components

| Component | Role |
|------------|----------|
| Portfolio  | Current state |
| Universe   | Decision space |
| Views      | Investor opinion |
| Weights    | Ideal result |
| Rebalancing| Execution |
| Diversification| Exploration |
------------------------------------------------------------------------

# ❓ FAQ

## Do I need to be in the universe to be in the portfolio?

✔️ Yes.

If an asset is not in the universe:
- It will not be considered in the optimization
- It may be ignored in rebalancing

------------------------------------------------------------------------

# 🚀 Usage Examples

## 📌 Example 1 (Brazil + International)

### Portfolio

    PETR4.SA: 10
    VALE3.SA: 5
    IVVB11.SA: 2

### Universe

    PETR4.SA
    VALE3.SA
    ITUB4.SA
    IVVB11.SA
    AAPL34.SA
    MSFT34.SA

### Views

    PETR4.SA: 0.17
    AAPL34.SA: 0.15

------------------------------------------------------------------------

## 📌 Example 2 (Income focus + diversification)

### Portfolio

    MXRF11.SA: 10
    HGLG11.SA: 5
    PETR4.SA: 5

### Universe

    MXRF11.SA
    HGLG11.SA
    XPLG11.SA
    TRXF11.SA
    PETR4.SA
    IVVB11.SA

### Views

    TRXF11.SA: 0.12
    XPLG11.SA: 0.11
    IVVB11.SA: 0.14

------------------------------------------------------------------------

# 🧠 Ideal Workflow

1. Define current portfolio
2. Define universe
3. Insert views
4. Run model
5. Execute rebalancing
6. Use diversification to test new assets

# ⚙️ Fine-Tuning the Model (Advanced Parameters)

This section explains how to control model behavior through:

- Views (expected returns)
- Tau (Black-Litterman confidence)
- Weight Bounds (allocation limits)

---

# 🧠 1. Views (Return Expectations)

## 🔹 What are they?

They are your **opinions about expected returns of specific assets**.

Format:

    TICKER: return

Example:

    PETR4.SA: 0.16
    NVDC34.SA: 0.18

---

## 🔹 How to interpret

- 0.16 = 16% per year expected
- Can be based on:
  - Valuation
  - Macro scenario
  - Personal conviction

---

## 🔹 Impact on the model

| Intensity | Result |
|------------|----------|
| Weak      | Small adjustment in weights |
| Moderate   | Noticeable tilt |
| Strong      | Concentration in the asset |

---

## 🔹 Rule of thumb

- Use **spread over CDI**:

    rf + premium

Example:

    rf = 0.1465 (CDI)

    PETR4: rf + 0.02
    NVDC34: rf + 0.035

---

## 🔥 Insight

Views **do not control the model alone**.

👉 They compete with risk (covariance)

---

# ⚖️ 2. Tau (τ) — Confidence in the Model

## 🔹 What is it?

Black-Litterman parameter that controls:

> How much to trust views vs market

---

## 🔹 Typical values

| Tau | Behavior |
|-----|-------------|
| 0.01 | Conservative (almost ignores views) |
| 0.03 | Balanced |
| 0.05 | More aggressive |
| 0.1+ | Very aggressive |

---

## 🔹 Impact

| Low Tau | High Tau |
|----------|---------|
| Equal weight dominates | Views dominate |
| Diversified portfolio | Concentrated portfolio |
| Lower risk of error | Higher risk / higher conviction |

---

## 🔹 Rule of thumb

- Solid default:

    tau = 0.03

- For more aggressiveness:

    tau = 0.05

---

## 🔥 Insight

Tau is the **volume of your opinion**.

👉 Views = direction  
👉 Tau = intensity  

---

# 📊 3. Weight Bounds

## 🔹 What is it?

Optimizer constraint:

    weight_bounds = (min, max)

Example:

    (0, 0.2)

---

## 🔹 Interpretation

- 0 → no shorting
- 0.2 → maximum 20% per asset

---

## 🔹 Impact

| Low limit | High limit |
|-------------|------------|
| More diversified portfolio | More concentrated portfolio |
| Lower risk | Higher risk |
| Lower return potential | Higher return potential |

---

## 🔹 Examples

### Conservative

```python
weight_bounds = (0, 0.1)
```

👉 Highly diversified

---

### Balanced

```python
weight_bounds = (0, 0.2)
```

👉 Good risk/return balance

---

### Aggressive

```python
weight_bounds = (0, 0.3)
```

👉 Allows strong convictions

---

# 🔗 Parameter Interaction

These three elements work together:

| Parameter | Function |
|----------|--------|
| Views | Defines direction |
| Tau | Defines strength |
| Bounds | Defines physical limits |

---

## 🔥 Practical Example

### Scenario 1 (Conservative)

- Moderate views
- tau = 0.01
- bounds = (0, 0.2)

👉 Result:
- Close to equal weight
- Low concentration

---

### Scenario 2 (Strong conviction)

- High views
- tau = 0.05
- bounds = (0, 0.3)

👉 Result:
- Concentration in a few assets
- High risk / high return

---

# 🧠 Recommended Strategy

## Step-by-step:

1. Start with:

    tau = 0.03  
    bounds = (0, 0.2)

2. Adjust views carefully

3. Only then:
   - increase tau
   - increase bounds

---

# 🚨 Common Mistakes

## ❌ 1. Views too high

    NVDC34: 0.30

👉 Result:
- Overfitting
- Distorted portfolio

---

## ❌ 2. Tau too high

    tau = 0.1

👉 Result:
- Model becomes "pure guesswork"

---

## ❌ 3. Bounds too tight

    (0, 0.05)

👉 Result:
- Rigid model

---

# Model Summary

The model is a system of balance:

👉 Covariance → risk  
👉 Views → opinion  
👉 Tau → confidence  
👉 Bounds → discipline  

You do not directly "control" the outcome.

👉 You control the system behavior.

------------------------------------------------------------------------

# 🔥 Final Insight

You do not choose the portfolio directly.

👉 You define the universe + views  
👉 The model chooses the optimal portfolio

# ⚠️ Final Disclaimer

This project does not constitute investment advice and is not responsible for any results. It is strictly **experimental**.
