import streamlit as st
import numpy as np

st.title("Matrix Diagonalization Checker")

# --- Input: Matrix dimensions ---
n = st.number_input("Enter the size of the square matrix (n x n):", min_value=1, max_value=10, value=2, step=1)

# --- Input: Matrix entries as a grid ---
st.subheader(f"Enter the {n}x{n} matrix:")
matrix = np.zeros((n, n))
for i in range(n):
    cols = st.columns(n)
    for j in range(n):
        matrix[i, j] = cols[j].number_input(
            f"Row {i+1}, Col {j+1}", 
            value=1.0 if i == j else 0.0,  # Default: Identity matrix
            key=f"matrix_{i}_{j}"
        )

# --- Check if matrix is diagonalizable ---
def is_diagonalizable(matrix, tol=1e-6):
    try:
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        # Check if eigenvectors matrix is invertible (full rank)
        if np.linalg.matrix_rank(eigenvectors) == matrix.shape[0]:
            return True, eigenvalues, eigenvectors
        else:
            return False, eigenvalues, eigenvectors
    except np.linalg.LinAlgError:
        return False, None, None

# --- Diagonalize the matrix ---
def diagonalize(matrix, tol=1e-6):
    diagonalizable, eigenvalues, eigenvectors = is_diagonalizable(matrix, tol)
    if diagonalizable:
        D = np.diag(eigenvalues)
        P = eigenvectors
        P_inv = np.linalg.inv(P)
        # Verify: P @ D @ P_inv ≈ original matrix
        reconstructed = P @ D @ P_inv
        is_correct = np.allclose(reconstructed, matrix, atol=tol)
        return D, P, P_inv, is_correct
    else:
        return None, None, None, False

# --- Output ---
st.subheader("Results")

# Always compute eigenvalues/eigenvectors
_, eigenvalues, eigenvectors = is_diagonalizable(matrix)

if eigenvalues is not None:
    st.write("**Eigenvalues:**")
    st.write(eigenvalues)
    st.write("**Eigenvectors (columns):**")
    st.write(eigenvectors)

# Check diagonalizability
D, P, P_inv, is_correct = diagonalize(matrix)

if D is not None:
    st.success("✅ The matrix is diagonalizable!")
    st.write("**Diagonal matrix (D):**")
    st.write(D)
    st.write("**Matrix of eigenvectors (P):**")
    st.write(P)
    st.write("**Inverse of P (P⁻¹):**")
    st.write(P_inv)
    if is_correct:
        st.info("✔ Verification: P @ D @ P⁻¹ ≈ original matrix (within numerical precision).")
    else:
        st.warning("⚠ Verification failed. Check numerical precision or matrix input.")
else:
    st.error("❌ The matrix is **not diagonalizable** (insufficient linearly independent eigenvectors).")

# --- Theoretical note ---
with st.expander("📌 Why is this matrix (not) diagonalizable?"):
    st.write("""
    A matrix is diagonalizable if and only if it has **n linearly independent eigenvectors** (where n is the matrix size).
    - If eigenvalues are repeated, check the geometric multiplicity (number of eigenvectors for each eigenvalue).
    - If the geometric multiplicity < algebraic multiplicity for any eigenvalue, the matrix is **not diagonalizable**.
    """)

linkedin_url = "https://www.linkedin.com/in/bhavin-moriya-ph-d-b0b88b2/"
github_url = "https://github.com/bhavinmoriya"

st.markdown("## Connect with me")

col1, col2 = st.columns(2)

with col1:
    st.link_button("🔗 Follow on LinkedIn", linkedin_url)

with col2:
    st.link_button("💻 Follow on GitHub", github_url)
