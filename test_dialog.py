import streamlit as st
@st.dialog("Hello")
def my_dialog():
    st.write("World")
    if st.button("Close"):
        st.rerun()

st.write("Test")
if st.button("Open"):
    my_dialog()
