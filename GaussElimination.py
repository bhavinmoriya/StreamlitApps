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
        try:
            sol_x1 = sp.solve(eq1, x)[0]
            st.latex(f"{sp.pretty(x)} = {sp.pretty(sol_x1)}")

            # Substitute into eq2
            st.write(f"2. Substitute {sp.pretty(x)} into the second equation:")
            eq2_sub = eq2.subs(x, sol_x1)
            st.latex(f"{sp.pretty(eq2_sub)}")

            # Solve for x2
            st.write(f"3. Solve for {sp.pretty(y)}:")
            try:
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
            except IndexError:
                # Infinitely many solutions
                st.write("The system has infinitely many solutions.")
                st.write("### General Solution:")
                st.latex(f"{sp.pretty(x)} = {sp.pretty(sol_x1)}")
                st.write("Choose a value for y to find a particular solution:")
                y_val = st.number_input("Enter a value for y:", value=0.0, step=0.1)
                sol_x_particular = sol_x1.subs(y, y_val)
                st.latex(f"{sp.pretty(x)} = {sp.pretty(sol_x_particular)}")
        except IndexError:
            st.write("The system has no unique solution (either no solution or infinitely many).")

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
