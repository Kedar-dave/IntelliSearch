import streamlit as st
from base import DocumentProcessor,Vectorizer

@st.cache_data
def main():
    data = DocumentProcessor()
    data.load_pdf("resume_data")
    st.session_state.vector = Vectorizer(data.pdfData)
    st.session_state.vector.load_index("resume_data")
    st.session_state.pdf = data.pdfData
    st.session_state.index = st.session_state.vector.embeddings
main()

def search_data(query,limit):
    st.divider()
    with st.spinner():
        results = st.session_state.vector.semantic_search(query,limit,0.3)
    display_data(query,results)

def display_data(query, results):
    st.subheader("Your Query: " + query)
    st.subheader(f"Files Found: {len(results)}")
    data = {
        "Number": [i+1 for i in range(len(results))],
        "Names":[st.session_state.pdf[res[0]]['name'] for res in results],
        "Score":[res[1] for res in results]
    }
    print(f"No of Results:{len(data['Names'])}")
    col1, col2, col3 = st.columns([1,1,1])
    with st.container():
        with col1:
            st.subheader("Pdf Name")
        with col2:
            st.subheader("Link")
        with col3:
            st.subheader("Score")
    with st.container():
        for number, name, score in zip(data["Number"],data["Names"], data["Score"]):
            file_path =f"https://github.com/Kedar-dave/IntelliDocSearch/tree/main/resume-dataset/{name}"
            with col1:
                st.markdown(str(number) + ":: " + name + " -------->")
                
            with col2:
            
                st.link_button(str(number) + "::"+"Open", file_path)
                
            with col3:
                st.write(f"{score:0,.3f}")
                


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
    with col3:
        search = st.button('🔍', type="secondary")
        cancel = st.button("❌")
    limit = st.number_input("Search Results Limit",50,2000,placeholder="Search Limit",
                                    label_visibility="collapsed")

if search==True and cancel==False and bool(query)==True:
    print(f"Query:{query}")
    search_data(query,limit)
