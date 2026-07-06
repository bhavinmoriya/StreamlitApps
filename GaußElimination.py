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

    # Method 1: Substitution (for 2 equations)
    if num_eq == 2 and num_vars == 2:
        st.write("### Method: Substitution")
        x, y = symbols('x1 x2')
        eq1, eq2 = equations

        # Solve eq1 for x1
        st.write(f"1. Solve the first equation for {sp.pretty(x)}:")
        sol_x1 = sp.solve(eq1, x)[0]
        st.latex(f"{sp.pretty(x)} = {sp.pretty(sol_x1)}")

        # Substitute into eq2
        st.write(f"2. Substitute {sp.pretty(x)} into the second equation:")
        eq2_sub = eq2.subs(x, sol_x1)
        st.latex(f"{sp.pretty(eq2_sub)}")

        # Solve for x2
        st.write(f"3. Solve for {sp.pretty(y)}:")
        sol_y = sp.solve(eq2_sub, y)[0]
        st.latex(f"{sp.pretty(y)} = {sp.pretty(sol_y)}")

        # Substitute back to find x1
        st.write(f"4. Substitute {sp.pretty(y)} back into the expression for {sp.pretty(x)}:")
        sol_x = sol_x1.subs(y, sol_y)
        st.latex(f"{sp.pretty(x)} = {sp.pretty(sol_x)}")

        # Final solution
        st.write("### Final Solution:")
        st.latex(f"{sp.pretty(x)} = {sp.pretty(sol_x)}")
        st.latex(f"{sp.pretty(y)} = {sp.pretty(sol_y)}")

    # Method 2: Matrix Method (for any size)
    else:
        st.write("### Method: Matrix (Gaussian Elimination)")
        A = []
        B = []
        for eq in equations:
            coeffs = [eq.lhs.coeff(var) for var in symbol_list]
            A.append(coeffs)
            B.append(eq.rhs)

        A_mat = Matrix(A)
        B_mat = Matrix(B)
        st.write("1. Augmented Matrix:")
        augmented = A_mat.col_join(B_mat)
        st.latex(f"\\left[\\begin{{matrix}}{augmented.to_string()}\\end{{matrix}}\\right]")

        # Perform Gaussian elimination
        st.write("2. Perform Gaussian Elimination:")
        reduced = augmented.rref()
        st.latex(f"\\left[\\begin{{matrix}}{reduced[0].to_string()}\\end{{matrix}}\\right]")

        # Extract solution
        solution = linsolve((A_mat, B_mat), symbol_list)
        st.write("### Final Solution:")
        if solution:
            for sol in solution:
                st.latex(f"{sp.pretty(sol)}")
        else:
            st.write("No solution exists (inconsistent system).")

    # General solution using SymPy's solve
    st.write("### Verification using SymPy's `solve`:")
    solution = solve(equations, symbol_list)
    if solution:
        for var, val in solution.items():
            st.latex(f"{sp.pretty(var)} = {sp.pretty(val)}")
    else:
        st.write("No solution exists.")
