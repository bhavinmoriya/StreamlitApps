# file: streamlit_trainer.py
import time
import random
import numpy as np
import polars as pl
import streamlit as st

def gen_question(level):
    if level == 1:
        a = random.randint(10, 30)
        b = random.choice([9, 11])
    elif level == 2:
        a = random.randint(20, 70)
        b = random.choice([11, 19, 21])
    else:
        a = random.randint(40, 99)
        b = random.choice([19, 25, 49, 99])
    return a, b, a * b

def run_session(n=20):
    level = 2
    records = []
    st.session_state.records = records
    st.session_state.current_question = 0
    st.session_state.level = level

    if "records" not in st.session_state:
        st.session_state.records = []

    if st.session_state.current_question < n:
        a, b, ans = gen_question(st.session_state.level)
        st.session_state.current_a = a
        st.session_state.current_b = b
        st.session_state.current_ans = ans
        st.session_state.start_time = time.time()

        st.write(f"### Question {st.session_state.current_question + 1}/{n}")
        st.write(f"**{a} x {b} = ?**")

        user_input = st.text_input("Your answer:", key=f"input_{st.session_state.current_question}")

        if user_input:
            try:
                user_ans = int(user_input)
                latency = time.time() - st.session_state.start_time
                correct = user_ans == st.session_state.current_ans

                st.session_state.records.append({
                    "a": st.session_state.current_a,
                    "b": st.session_state.current_b,
                    "correct": correct,
                    "latency": latency,
                    "level": st.session_state.level
                })

                if correct:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Wrong! The answer was {st.session_state.current_ans}.")

                # Adaptive logic
                if correct and latency < 3:
                    st.session_state.level = min(3, st.session_state.level + 1)
                elif not correct:
                    st.session_state.level = max(1, st.session_state.level - 1)

                st.session_state.current_question += 1
                st.rerun()
            except ValueError:
                st.warning("Please enter a valid number.")
    else:
        df = pl.DataFrame(st.session_state.records)
        st.balloons()
        st.write("## 🎉 Session Complete!")

        st.write("### Session Stats")
        st.write(f"**Accuracy:** {df['correct'].mean():.2%}")
        st.write(f"**Avg Latency:** {df['latency'].mean():.2f} seconds")

        st.write("### By Level")
        level_stats = df.group_by("level").agg([
            pl.col("correct").mean().alias("accuracy"),
            pl.col("latency").mean().alias("latency")
        ])
        st.dataframe(level_stats.to_pandas())

        # Export data
        csv = df.write_csv()
        st.download_button(
            label="Download Session Data",
            data=csv,
            file_name="math_trainer_session.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    st.title("🧠 Math Trainer")
    st.write("Answer the multiplication questions as fast as you can!")
    n_questions = st.slider("Number of questions:", 5, 50, 20)
    if st.button("Start Session"):
        run_session(n_questions)
