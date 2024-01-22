
import pandas as pd
import streamlit as st
from icecream import ic
from base import DocumentProcessor,Vectorizer
data = DocumentProcessor()
data.load_pdf("resume_data")
st.session_state.vector = Vectorizer(data.pdfData)
st.session_state.vector.load_index("resume_data")
st.session_state.pdf = data.pdfData
st.session_state.index = st.session_state.vector.embeddings
st.title("Search Your PDF 📝")
query = ''
expanderText = ''
col1, col2, col3 = st.columns([ 3, 6, 1])
cancel = False
with col1:
    st.subheader("Query:")
    st.subheader("Result Limit:")
with col2:
    with st.container():
        query = st.text_input("Enter Query", placeholder="Enter Query",
                              label_visibility="collapsed", key="query")
        expanderText = "Your Query: " + query
    with col3:
        search = st.button('🔍', type="secondary")
        cancel = st.button("❌")
    limit = st.number_input("Search Results Limit",50,2000,placeholder="Search Limit",
                                label_visibility="collapsed")
def search_data():
    st.subheader(expanderText)
    st.divider()
    with st.spinner():
        results = st.session_state.vector.semantic_search(query,limit,0.3)
    display_data(results)

def display_data(results):
    st.subheader(f"Files Found:{len(results)}")
    data = {
    "Name": [st.session_state.pdf[res[0]]['name'] for res in results],
    'Score': [res[1] for res in results],
    }
    df = pd.DataFrame(data)
    st.table(df)

if search and not cancel:
    search_data()



    

