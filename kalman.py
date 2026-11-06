# app.py — A simple Streamlit app introducing the Kalman filter
# Run with:  streamlit run app.py
# Install:   pip install streamlit numpy plotly

import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Kalman Filter Intro", page_icon="📊", layout="wide")


# ----------------------------- Kalman filter -----------------------------

@st.cache_data
def simulate(signal_choice, n_steps, noise_std, seed):
    """Generate a noisy measurement series from a known true signal."""
    if signal_choice == "constant":
        true_fn = lambda t: np.ones_like(t, dtype=float) * 1.0
    elif signal_choice == "sine":
        true_fn = lambda t: np.sin(t / 12.0) * 2.0
    else:  # ramp
        true_fn = lambda t: t * 0.02
    rng = np.random.default_rng(seed)
    t = np.arange(n_steps)
    true = true_fn(t)
    measurements = true + rng.normal(0, noise_std, size=n_steps)
    return t, true, measurements


def kalman_1d(measurements, process_var, measurement_var, est_init, err_init):
    """
    Simple 1D Kalman filter (predict + update) for a scalar state.

    Parameters
    ----------
    measurements : array of z (observations)
    process_var  : Q, process (motion) noise variance — how much the true
                   state is expected to change per step
    measurement_var : R, sensor noise variance
    est_init     : initial state estimate
    err_init     : initial estimate uncertainty (variance)
    """
    n = len(measurements)
    est = np.zeros(n)          # filtered estimates
    err = np.zeros(n)          # estimate uncertainty
    gain = np.zeros(n)         # Kalman gain K

    e, P = est_init, err_init
    for k in range(n):
        # --- Predict: state stays the same (random-walk model)
        P = P + process_var

        # --- Update: blend prediction with measurement
        K = P / (P + measurement_var)
        e = e + K * (measurements[k] - e)
        P = (1 - K) * P

        est[k], err[k], gain[k] = e, P, K
    return est, err, gain


# ------------------------------- UI ---------------------------------------

st.title("📊 Introducing the Kalman Filter")
st.write(
    "The Kalman filter combines a **prediction** of a system's state with a "
    "**noisy measurement** of it, weighting both by how much it trusts each. "
    "The result is a smooth, optimal estimate. Play with the sliders below to see it in action."
)

with st.sidebar:
    st.header("⚙️ Simulation settings")
    n_steps = st.slider("Number of time steps", 50, 500, 200, 10)
    seed = st.number_input("Random seed", 0, 999, 42)
    noise_std = st.slider("Measurement noise std (sensor)", 0.1, 5.0, 1.0, 0.1)
    show_true = st.checkbox("Show true signal", True)

    st.header("🎛️ Kalman filter tuning")
    process_var = st.slider(
        "Process noise Q (how fast the state can change)",
        0.001, 1.0, 0.01, 0.001, format="%.3f",
    )
    use_auto_init = st.checkbox("Auto-initialise from first measurement", True)
    est_init = 0.0 if use_auto_init else st.number_input("Initial estimate", -10.0, 10.0, 0.0)
    err_init = st.slider("Initial uncertainty", 0.1, 20.0, 5.0, 0.1)

# Example signal: a constant plus a sine wiggle
signal_choice = st.radio(
    "True signal to track",
    ["Constant value (classic demo)", "Sine wave", "Ramp (drift)"],
    horizontal=True,
)

signal_key = {"Constant value (classic demo)": "constant", "Sine wave": "sine", "Ramp (drift)": "ramp"}[signal_choice]

t, true, meas = simulate(signal_key, n_steps, noise_std, seed)

if use_auto_init:
    est_init = meas[0]

est, err, gain = kalman_1d(meas, process_var, noise_std**2, est_init, err_init)

# ------------------------------- Plots ------------------------------------

col1, col2 = st.columns([3, 1])

with col1:
    fig = go.Figure()
    if show_true:
        fig.add_trace(go.Scatter(x=t, y=true, name="True state", line=dict(color="green", width=2)))
    fig.add_trace(go.Scatter(x=t, y=meas, mode="markers", name="Measurements (noisy)",
                             marker=dict(size=4, color="lightblue")))
    fig.add_trace(go.Scatter(x=t, y=est, name="Kalman estimate", line=dict(color="red", width=3)))
    # ±2σ confidence band
    fig.add_trace(go.Scatter(
        x=t, y=est + 2*np.sqrt(err), mode="lines", line=dict(width=0),
        showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=t, y=est - 2*np.sqrt(err), mode="lines", line=dict(width=0),
        fill="tonexty", fillcolor="rgba(255,0,0,0.15)", name="95% confidence"))
    fig.update_layout(
        height=450, xaxis_title="Time step", yaxis_title="Value",
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    rmse_raw = np.sqrt(np.mean((meas - true) ** 2))
    rmse_kal = np.sqrt(np.mean((est - true) ** 2))
    st.metric("Raw measurement RMSE", f"{rmse_raw:.3f}")
    st.metric("Kalman estimate RMSE", f"{rmse_kal:.3f}")
    st.metric("Final Kalman gain K", f"{gain[-1]:.3f}")
    st.caption(
        "Lower RMSE = better tracking. The Kalman gain (0–1) says how much the "
        "filter trusts the new measurement versus its prediction."
    )

# ------------------------------- Theory -----------------------------------

with st.expander("📚 How it works (the two equations)"):
    st.markdown(
        """
Each step has two phases:

**1. Predict** — assume the state barely changes (random walk):

$$\\hat{x}_{k|k-1} = \\hat{x}_{k-1}, \\qquad P_{k|k-1} = P_{k-1} + Q$$

**2. Update** — blend prediction with the measurement $z_k$:

$$K_k = \\frac{P_{k|k-1}}{P_{k|k-1} + R}, \\qquad \\hat{x}_k = \\hat{x}_{k|k-1} + K_k (z_k - \\hat{x}_{k|k-1}), \\qquad P_k = (1-K_k) P_{k|k-1}$$

- $Q$ (process noise): how much you expect the true state to move per step.
  Too low → the filter lags behind real changes. Too high → it follows the noise.
- $R$ (measurement noise): the sensor's variance. Noisier sensor → smaller gain.
- $K$ (Kalman gain): 0 means "trust my prediction", 1 means "trust the sensor".
  It adapts automatically: uncertain states soak up measurements, confident ones don't.
        """
    )

with st.expander("💡 Try these experiments"):
    st.markdown(
        """
1. **Noisy sensor:** crank measurement noise up — the estimate stays smooth.
2. **Slow vs fast signal:** with the sine wave, lower Q until the filter visibly lags, then raise it.
3. **Trust exercise:** set Q near zero and watch the confidence band shrink and the gain → 0.
4. **Cold start:** uncheck auto-initialise with a wrong initial estimate and large uncertainty —
   the filter converges quickly anyway.
        """
    )

st.info(
    "This is the 1-D scalar case. The full Kalman filter generalises to vectors/matrices "
    "($\\mathbf{x}$, $\\mathbf{P}$, $\\mathbf{F}$, $\\mathbf{H}$, $\\mathbf{Q}$, $\\mathbf{R}$), "
    "but the predict–update–gain logic is exactly what you see here."
)
