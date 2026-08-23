def main():
    print("Hello from streamlitapps!")


if __name__ == "__main__":
    main()

linkedin_url = "https://www.linkedin.com/in/bhavin-moriya-ph-d-b0b88b2/"
github_url = "https://github.com/bhavinmoriya"

st.markdown("## Connect with me")

col1, col2 = st.columns(2)

with col1:
    st.link_button("🔗 Follow on LinkedIn", linkedin_url)

with col2:
    st.link_button("💻 Follow on GitHub", github_url)

linkedin_url = "https://www.linkedin.com/in/bhavin-moriya-ph-d-b0b88b2/"
github_url = "https://github.com/bhavinmoriya"
youtube_url = "https://www.youtube.com/@bhavinmoriya9216"
st.markdown("## Connect with me")

col1, col2, col3 = st.columns(3)

with col1:
    st.link_button("🔗 Follow on LinkedIn", linkedin_url)

with col2:
    st.link_button("💻 Follow on GitHub", github_url)

with col3:
    st.link_button("🔗 Subscribe on YouTube", youtube_url)
