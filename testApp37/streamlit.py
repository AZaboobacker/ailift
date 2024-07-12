import streamlit as st
import random

# Function to generate business names
def generate_business_names(keyword, style, number):
    prefix = ["Tech", "Inno", "Biz", "Smart", "Next", "Future", "Bright", "Prime", "Vision", "Peak"]
    suffix = ["Solutions", "Hub", "Works", "Labs", "Studio", "Ventures", "Group", "Systems", "Dynamics", "Network"]
    
    names = []
    for _ in range(number):
        name = f"{random.choice(prefix)}{keyword}{random.choice(suffix)}"
        if style == "Fun":
            name = f"{name}ify"
        elif style == "Professional":
            name = f"{name} Corp"
        elif style == "Modern":
            name = f"{name} 2.0"
        names.append(name)
    return names

# Streamlit app
st.title("Business Name Generator")
st.write("Generate business names based on your preferences.")

# User inputs
keyword = st.text_input("Enter a keyword:", "")
style = st.selectbox("Select a style:", ["Classic", "Fun", "Professional", "Modern"])
number = st.number_input("Number of names to generate:", min_value=1, max_value=10, value=5)

if st.button("Generate Names"):
    if keyword:
        names = generate_business_names(keyword, style, number)
        st.write("Here are your generated business names:")
        for name in names:
            st.write(f"- {name}")
    else:
        st.error("Please enter a keyword to generate names.")

# Run the Streamlit app
if __name__ == '__main__':
    st.set_page_config(page_title="Business Name Generator")
    st.markdown("<style>.main {background-color: #f0f0f0;}</style>", unsafe_allow_html=True)
