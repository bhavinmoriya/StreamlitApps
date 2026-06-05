**Correlation** and **causal inference** answer different questions.

| Question           | Correlation                                      | Causal Inference                             |
| ------------------ | ------------------------------------------------ | -------------------------------------------- |
| What does it ask?  | Do two variables move together?                  | Does changing X cause Y to change?           |
| Example            | Ice cream sales and drownings increase together. | Does selling more ice cream cause drownings? |
| Mathematical focus | Association                                      | Cause-and-effect                             |
| Easy or hard?      | Relatively easy                                  | Much harder                                  |
| Main danger        | Spurious relationships                           | Hidden confounders                           |

---

## Correlation

Correlation measures how strongly two variables are associated.

The most common measure is the Pearson correlation coefficient:

r=\frac{\mathrm{Cov}(X,Y)}{\sigma_X\sigma_Y}

where:

* (r=1): perfect positive relationship
* (r=0): no linear relationship
* (r=-1): perfect negative relationship

Example:

| Hours Studied | Exam Score |
| ------------- | ---------- |
| 1             | 55         |
| 2             | 62         |
| 3             | 70         |
| 4             | 78         |

These variables are positively correlated.

But correlation alone does **not** tell us why.

---

## Why Correlation ≠ Causation

Suppose we observe:

* Ice cream sales ↑
* Drownings ↑

Should we conclude:

> Ice cream causes drowning?

No.

A third variable exists:

**Temperature**

```
Temperature
    ↓
Ice Cream Sales

Temperature
    ↓
Drownings
```

Temperature is a **confounder**.

---

## Causal Inference

Causal inference asks:

> What would happen if I intervened?

Example:

* If I give a patient a drug, does recovery improve?
* If a company increases advertising by €1000, how much extra revenue results?
* If a government lowers taxes, what happens to employment?

This requires estimating a **counterfactual**:

> What would have happened if the treatment had not occurred?

The challenge is that we never observe both realities simultaneously.

---

## A Financial Example

Suppose:

| Month | Marketing Spend | Revenue |
| ----- | --------------- | ------- |
| 1     | 1000            | 10000   |
| 2     | 2000            | 14000   |
| 3     | 3000            | 18000   |

Correlation is strong.

But maybe:

* Marketing increased because demand was already rising.
* Holiday season drove both marketing and revenue.

Thus:

```
Marketing ↔ Revenue
```

does not imply

```
Marketing → Revenue
```

---

## How Statisticians Infer Causality

### 1. Randomized Controlled Trials (Gold Standard)

Randomly assign:

* Treatment group
* Control group

Randomization balances hidden factors.

Example:

* Half of users see a new website design.
* Half see the old design.

Difference in outcomes can be interpreted causally.

---

### 2. Observational Methods

When experiments are impossible, we use:

* Regression adjustment
* Matching
* Instrumental variables
* Difference-in-differences
* Regression discontinuity
* Propensity scores
* Causal forests

These attempt to remove confounding bias.

---

## The Language of Modern Causal Inference

A common framework comes from Judea Pearl.

Correlation asks:

[
P(Y \mid X)
]

"What do we observe when X is present?"

Causality asks:

[
P(Y \mid do(X))
]

"What happens when we force X to occur?"

That little **do()** operator is the key distinction.

---

## Python Demonstration

A classic simulation:

```python
import numpy as np
import polars as pl

np.random.seed(42)

temperature = np.random.normal(25, 5, 1000)

ice_cream_sales = 50 + 3 * temperature + np.random.normal(0, 5, 1000)

drownings = 2 + 0.2 * temperature + np.random.normal(0, 1, 1000)

df = pl.DataFrame({
    "temperature": temperature,
    "ice_cream_sales": ice_cream_sales,
    "drownings": drownings,
})

print(
    df.select(
        pl.corr("ice_cream_sales", "drownings")
    )
)
```

You'll find a strong correlation between ice cream sales and drownings even though **ice cream has no causal effect** in the data-generating process.

---

## Feynman-style intuition

Think of correlation as:

> "Whenever I see smoke, I often see fire."

Think of causality as:

> "If I create smoke, will that create fire?"

Those are fundamentally different questions.

A large part of modern statistics, econometrics, machine learning, and quantitative finance is figuring out when observed relationships are merely correlations and when they represent genuine causal mechanisms.
