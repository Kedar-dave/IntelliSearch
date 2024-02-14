import streamlit as st
from base import DocumentProcessor, Vectorizer 
st.set_page_config(
    page_title="Search App",
    page_icon="📱",
    layout="wide",
)
@st.cache_resource
def cache():
    data_processor = DocumentProcessor()
    data_processor.load_pdf("resume_data")
    
    vectorizer = Vectorizer()
    vectorizer.load_index("resume_data")

    return data_processor, vectorizer

data_processor, vectorizer = cache()
st.session_state.data_processor = data_processor
st.session_state.vectorizer = vectorizer


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
    st.divider()
    with st.spinner():  
        results = st.session_state.vectorizer.semantic_search(query, limit, False)

    st.subheader("Your Query: " + query)
    st.subheader(f"Files Found: {len(results)}")
    data = {
        "Number": [i+1 for i in range(len(results))],
        "Names":[st.session_state.data_processor.pdfData[res[0]]['name'] for res in results],
        "Score":[res[1] for res in results]
    }
    print(f"Query:{query} " + f"Results:{len(data['Names'])}")
    col1, col2, col3 = st.columns([1,1,1])
    with st.container():
        with col1:
            st.subheader("Pdf Name")
        with col2:
            st.subheader("Link")
        with col3:
            st.subheader("Score")
    with open("queries.txt", "r") as file:
        global noQueries
        noQueries = int(file.read()) + 1
        fileName = str(noQueries) + ' ' + query
    with open(f"./log/{fileName}.txt", "w")as debugLogFile:
        debugLogFile.write("Query:" + query + "\n")
        debugLogFile.write("Number of Results:" + str(len(data["Names"])) + "\n")
        debugLogFile.write("Results:\n")
        with st.container():
            for number, name, score in zip(data["Number"],data["Names"], data["Score"]):
                file_path =f"https://github.com/Kedar-dave/IntelliDocSearch/tree/main/resume-dataset/{name}"
                with col1:
                    st.markdown(str(number) + ":: " + name + " -------->")
                with col2:
                    st.link_button(str(number) + "::"+"Open", file_path)
                
                with col3:
                    st.write(f"{score:0,.3f}")
                debugLogFile.write(file_path + f", Score:{score:0,.3f}" + "\n")
    with open("queries.txt", "w") as file:
        file.writelines(str(noQueries))

