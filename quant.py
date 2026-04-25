# file: streamlit_trainer.py
import time
import random
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

def reset_session():
    st.session_state.records = []
    st.session_state.current_question = 0
    st.session_state.level = 2
    st.session_state.session_started = True

def run_session(n=20):
    if "session_started" not in st.session_state:
        reset_session()

    if st.session_state.current_question < n:
        if "current_a" not in st.session_state:
            a, b, ans = gen_question(st.session_state.level)
            st.session_state.current_a = a
            st.session_state.current_b = b
            st.session_state.current_ans = ans
            st.session_state.start_time = time.time()

        st.write(f"### Question {st.session_state.current_question + 1}/{n}")
        st.write(f"**{st.session_state.current_a} x {st.session_state.current_b} = ?**")

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
        reset_session()
        run_session(n_questions)
    elif "session_started" in st.session_state:
        run_session(n_questions)
