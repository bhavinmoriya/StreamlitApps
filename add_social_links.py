import os

# Lines to add
lines_to_add = [
    '\n',
    'linkedin_url = "https://www.linkedin.com/in/bhavin-moriya-ph-d-b0b88b2/"\n',
    'github_url = "https://github.com/bhavinmoriya"\n',
    '\n',
    'st.markdown("## Connect with me")\n',
    '\n',
    'col1, col2 = st.columns(2)\n',
    '\n',
    'with col1:\n',
    '    st.link_button("🔗 Follow on LinkedIn", linkedin_url)\n',
    '\n',
    'with col2:\n',
    '    st.link_button("💻 Follow on GitHub", github_url)\n',
]

# Get all .py files in the current directory (excluding this script)
py_files = [f for f in os.listdir() if f.endswith('.py') and f != 'add_social_links.py']

# Add lines to each file
for file in py_files:
    with open(file, 'r+') as f:
        content = f.read()
        # Check if all lines are already present
        if not all(line in content for line in lines_to_add):
            f.seek(0, 2)  # Move to the end of the file
            f.write(''.join(lines_to_add))
            print(f"✅ Added social links to {file}")
        else:
            print(f"⏭️  Skipped {file} (already contains the lines)")
