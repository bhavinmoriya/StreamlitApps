import streamlit as st
import sympy as sp
from sympy import symbols, Eq, solve, Matrix, linsolve

# Title
st.title("System of Equations Solver with Step-by-Step Solution")
st.write("Enter the coefficients for each equation and solve the system step-by-step.")

# Input: Number of equations and variables
num_eq = st.number_input("Number of equations", min_value=2, max_value=5, value=2, step=1)
num_vars = st.number_input("Number of variables", min_value=2, max_value=5, value=2, step=1)

# Initialize symbols
symbol_list = symbols([f'x{i+1}' for i in range(num_vars)])

# Input: Coefficients for each equation
st.subheader("Enter the coefficients for each equation:")
equations = []
for i in range(num_eq):
    cols = st.columns(num_vars + 1)  # +1 for the constant term
    coeffs = []
    for j in range(num_vars):
        coeffs.append(cols[j].number_input(f"Coefficient of x{j+1}", value=1.0, step=0.1, key=f"eq{i}_var{j}"))
    constant = cols[num_vars].number_input(f"Constant term", value=1.0, step=0.1, key=f"eq{i}_const")
    equations.append(Eq(sum(coeffs[k] * symbol_list[k] for k in range(num_vars)), constant))

# Display the system of equations
st.subheader("System of Equations:")
for eq in equations:
    st.latex(f"{sp.pretty(eq)}")

# Solve the system
if st.button("Solve"):
    st.subheader("Step-by-Step Solution:")

    # Extract coefficients and constants
    A = []
    B = []
    for eq in equations:
        coeffs = [eq.lhs.coeff(var) for var in symbol_list]
        A.append(coeffs)
        B.append(eq.rhs)

    A_mat = Matrix(A)
    B_mat = Matrix([B])  # Ensure B is a column vector

    # Transpose B_mat to make it a column vector
    B_mat = B_mat.T

    # Check if the system is solvable
    if A_mat.shape[0] != B_mat.shape[0]:
        st.error("Error: The number of equations and constants must match.")
    else:
        st.write("### Method: Matrix (Gaussian Elimination)")
        st.write("1. Augmented Matrix:")
        augmented = A_mat.col_join(B_mat)
        st.latex(f"\\left[\\begin{{matrix}}{augmented.to_string()}\\end{{matrix}}\\right]")

        # Perform Gaussian elimination
        st.write("2. Perform Gaussian Elimination:")
        reduced = augmented.rref()
        st.latex(f"\\left[\\begin{{matrix}}{reduced[0].to_string()}\\end{{matrix}}\\right]")

        # Extract solution
        solution = linsolve((A_mat, B_mat), symbol_list)
        st.write("### Solution:")
        if not solution:
            st.write("No solution exists (inconsistent system).")
        else:
            # Check if the solution is parametric (infinitely many solutions)
            if len(solution) == 1 and any(sol.has(sp.Symbol) for sol in solution.args[0]):
                st.write("The system has infinitely many solutions.")
                st.write("### General Solution:")
                general_solution = solution.args[0]
                st.latex(f"{sp.pretty(general_solution)}")

                # Allow user to input values for free variables
                free_vars = [var for var in symbol_list if var in general_solution.free_symbols]
                if free_vars:
                    st.write("Choose values for the free variables to find a particular solution:")
                    particular_solution = general_solution.copy()
                    for var in free_vars:
                        val = st.number_input(f"Enter a value for {sp.pretty(var)}:", value=0.0, step=0.1, key=f"free_var_{var}")
                        particular_solution = particular_solution.subs(var, val)
                    st.write("### Particular Solution:")
                    st.latex(f"{sp.pretty(particular_solution)}")
            else:
                for sol in solution:
                    st.latex(f"{sp.pretty(sol)}")

    # General solution using SymPy's solve
    st.write("### Verification using SymPy's `solve`:")
    solution = solve(equations, symbol_list)
    if solution:
        if isinstance(solution, dict):
            for var, val in solution.items():
                st.latex(f"{sp.pretty(var)} = {sp.pretty(val)}")
        else:
            st.write("General solution:")
            st.latex(f"{sp.pretty(solution)}")
    else:
        st.write("No solution exists.")
