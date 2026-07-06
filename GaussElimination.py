import streamlit as st
import sympy as sp
from sympy import Matrix, symbols, Eq, linsolve

# Title
st.title("Gaussian Elimination Step-by-Step Solver")
st.write("Enter the coefficients for each equation and solve the system using row reduction.")

# Input: Number of equations and variables
num_eq = st.number_input("Number of equations", min_value=2, max_value=5, value=2, step=1)
num_vars = st.number_input("Number of variables", min_value=2, max_value=5, value=2, step=1)

# Initialize symbols
symbol_list = symbols([f'x{i+1}' for i in range(num_vars)])

# Input: Coefficients for each equation
st.subheader("Enter the coefficients for each equation:")
equations = []
A = []
B = []
for i in range(num_eq):
    cols = st.columns(num_vars + 1)  # +1 for the constant term
    coeffs = []
    for j in range(num_vars):
        coeffs.append(cols[j].number_input(f"Coefficient of x{j+1}", value=1.0, step=0.1, key=f"eq{i}_var{j}"))
    constant = cols[num_vars].number_input(f"Constant term", value=1.0, step=0.1, key=f"eq{i}_const")
    equations.append(Eq(sum(coeffs[k] * symbol_list[k] for k in range(num_vars)), constant))
    A.append(coeffs)
    B.append(constant)

# Display the system of equations
st.subheader("System of Equations:")
for eq in equations:
    st.latex(f"{sp.pretty(eq)}")

# Solve the system using Gaussian elimination
if st.button("Solve using Gaussian Elimination"):
    st.subheader("Step-by-Step Row Reduction to RREF:")

    # Create coefficient matrix A_mat
    A_mat = Matrix(A)

    # Create constant matrix B_mat as a column vector
    B_mat = Matrix([B]).T  # Transpose to make it a column vector

    # Check if the shapes are compatible
    if A_mat.shape[0] != B_mat.shape[0]:
        st.error("Error: The number of equations and constants must match.")
    else:
        # Form the augmented matrix [A|B]
        augmented = A_mat.col_join(B_mat)
        st.write("1. Augmented Matrix:")
        st.latex(f"\\left[\\begin{{matrix}}{augmented.to_string()}\\end{{matrix}}\\right]")

        # Perform Gaussian elimination to RREF
        rref, pivot_cols = augmented.rref()

        st.write("2. Reduced Row-Echelon Form (RREF):")
        st.latex(f"\\left[\\begin{{matrix}}{rref.to_string()}\\end{{matrix}}\\right]")

        # Analyze the RREF
        st.subheader("Analysis of RREF:")

        # Check for no solution
        no_solution = False
        for row in rref:
            if all(x == 0 for x in row[:-1]) and row[-1] != 0:
                no_solution = True
                break

        if no_solution:
            st.write("The system has **no solution** (inconsistent system).")
            st.write("Reason: There is a row of the form [0 0 ... 0 | b] where b ≠ 0.")

        else:
            # Check for infinitely many solutions
            free_vars = [var for i, var in enumerate(symbol_list) if i not in pivot_cols]
            if free_vars:
                st.write("The system has **infinitely many solutions**.")
                st.write("Reason: There is at least one free variable (no pivot in its column).")
                st.write(f"Free variable(s): {', '.join([f'{var}' for var in free_vars])}")

                # General solution
                st.write("### General Solution:")
                solution = linsolve((A_mat, B_mat), symbol_list)
                if solution:
                    general_solution = solution.args[0]
                    st.latex(f"{sp.pretty(general_solution)}")

                    # Allow user to input values for free variables
                    st.write("Choose values for the free variables to find a particular solution:")
                    particular_solution = general_solution.copy()
                    for var in free_vars:
                        val = st.number_input(f"Enter a value for {sp.pretty(var)}:", value=0.0, step=0.1, key=f"free_var_{var}")
                        particular_solution = particular_solution.subs(var, val)
                    st.write("### Particular Solution:")
                    st.latex(f"{sp.pretty(particular_solution)}")
            else:
                st.write("The system has a **unique solution**.")
                st.write("Reason: Every variable has a leading 1 (pivot) in its column.")

                # Unique solution
                st.write("### Solution:")
                solution = linsolve((A_mat, B_mat), symbol_list)
                if solution:
                    for sol in solution:
                        st.latex(f"{sp.pretty(sol)}")
