import streamlit as st
import pandas as pd
import numpy as np
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import PyPDF2
from docx import Document  
import plotly.express as px
import base64
from io import BytesIO
from collections import Counter
import kaleido.plotly as kaleido

# Functions for file reading
def read_txt(file):
    return file.getvalue().decode("utf-8")

def read_docx(file):
    doc = Document(file)
    return " ".join([para.text for para in doc.paragraphs])

def read_pdf(file):
    pdf = PyPDF2.PdfReader(file)
    return " ".join([page.extract_text() for page in pdf.pages])

# Function to filter out stopwords
def filter_stopwords(text, additional_stopwords=[]):
    words = text.split()
    all_stopwords = STOPWORDS.union(set(additional_stopwords))
    filtered_words = [word for word in words if word.lower() not in all_stopwords]
    return " ".join(filtered_words)

# Function to create download link for plot
def get_image_download_link(buffered, format_):
    image_base64 = base64.b64encode(buffered.getvalue()).decode()
    return f'<a href="data:image/{format_};base64,{image_base64}" download="wordcloud.{format_}">Download Plot as {format_}</a>'

# Function to generate a download link for a DataFrame
def get_table_download_link(df, filename, file_label):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{file_label}</a>'

# Streamlit code

st.set_page_config(page_title="Word Cloud Generator", page_icon=":memo:", layout="wide")
st.title('Your Word Cloud :sunglasses:')
st.subheader("📁 ***Upload a PDF, Docx or Text file to generate a word cloud***")
uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "docx"])

if uploaded_file:
    st.sidebar.markdown("[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Imad-Jan)")
    file_size_mb = uploaded_file.size / (1024 * 1024)
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": f"{file_size_mb:.2f} MB"}
    st.table(file_details)

    # Check the file type and read the file
    if uploaded_file.type == "text/plain":
        text = read_txt(uploaded_file)
    elif uploaded_file.type == "application/pdf":
        text = read_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = read_docx(uploaded_file)
    else:
        st.write("This file type is not supported.")
        text = ""

    # Generate word count table
    words = text.split()
    word_count = pd.DataFrame({'Word': words}).groupby('Word').size().reset_index(name='Count').sort_values('Count', ascending=False)

    # Sidebar: Checkbox and Multiselect box for stopwords
    use_standard_stopwords = st.sidebar.checkbox("Use standard stopwords?", True)
    top_words = word_count['Word'].head(50).tolist()
    additional_stopwords = st.sidebar.multiselect("Additional stopwords:", sorted(top_words))

    if use_standard_stopwords:
        all_stopwords = STOPWORDS.union(set(additional_stopwords))
    else:
        all_stopwords = set(additional_stopwords)

    text = filter_stopwords(text, all_stopwords)

    if text:
        # Word Cloud dimensions
        width = st.sidebar.slider("Select Word Cloud Width", 400, 2000, 1200, 50)
        height = st.sidebar.slider("Select Word Cloud Height", 200, 2000, 800, 50)

        #theme drop_down
        color_theme = st.sidebar.selectbox("Select Color Theme:", ("Color 🌈", "Mono-Chrome 🌚", "Pastel 🌸", "Cool ❄️","Rainbow 🌈", "Ocean 🌊", "Terrain 🏞️", "Gist Earth 🌍", "Jet ✈️"))
        colormap = 'viridis'  # Default to a color theme
        if color_theme == "Mono-Chrome 🌚":
          colormap = 'gray'
        elif color_theme == "Pastel 🌸":
             colormap = 'Pastel1' 
        elif color_theme == "Cool ❄️":
            colormap = 'cool' 
        elif color_theme == "Rainbow 🌈":
            colormap = 'rainbow'
        elif color_theme == "Ocean 🌊":
            colormap = 'ocean'
        elif color_theme == "Terrain 🏞️":
            colormap = 'terrain' 
        elif color_theme == "Gist Earth 🌍":
            colormap = 'gist_earth'  
        elif color_theme == "Jet ✈️":
            colormap = 'jet'  


            
        # Custom color palette for word cloud
        st.sidebar.subheader("Customize Word Cloud Color Palette")
        background_color = st.sidebar.color_picker("Select Background Color", "#FFFFFF")
        custom_theme = {
           
            "backgroundColor": background_color,
            "font": "sans serif"
        }
        with st.sidebar:
            st.markdown('---')
            st.markdown("""
                #### Let's connect: [Imad Jan 💼](https://www.linkedin.com/in/imad-jan-205759262/)
                """)
        
    st.container()
    with st.container():
        st.subheader("Generated Word Cloud")     
        # Define the colormap based on the selected color theme
        wordcloud = WordCloud(width=width, height=height,  colormap=colormap, collocations=False, background_color=background_color, max_words=200, contour_width=3, contour_color=None).generate(text)
       
        fig, ax = plt.subplots(figsize=(width/100, height/100))  # Convert pixels to inches for figsize
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
   
        st.image(wordcloud.to_array(), use_column_width=True)
        
        # Save plot functionality
        resolution = st.slider("Select Resolution", 100, 500, 300, 50)
        format_ = st.selectbox("Select file format to save the plot", ["png", "jpeg", "svg", "pdf"])
        #Download word-cloud-image
        if st.button(f"Download as {format_}"):
            buffered = BytesIO()
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.savefig(buffered, format=format_, dpi=resolution)
            st.markdown(get_image_download_link(buffered, format_), unsafe_allow_html=True)

        # Create tabs for visualization types (Bar Chart and Pie Chart)
        st.header("Visualize Your Data")
        viz_tabs = st.tabs(["**📊 Bar Chart**","       ", "**🥧 Pie Chart**", "     ", "**🔠 Words Count Table**"])

        # First Tab: Bar Chart
        with viz_tabs[0]:
            n = st.slider("Select N for top N most frequent words", 1, 50, 10, 1)
            top_n_words = word_count.head(n)
            fig = px.bar(top_n_words, x="Word", y="Count", color="Word", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(title=f"Top {n} Most Frequent Words (Bar Chart)")
            st.plotly_chart(fig)
    
            # Download plot functionality
            if st.button("Download Plot as High Resolution Image"):
                buffered = BytesIO()
                fig.write_image(buffered, format=format_, width=1200, height=800, scale=resolution/100)
                st.markdown(get_image_download_link(buffered, format_), unsafe_allow_html=True)
    
        # Second Tab: Pie Chart
        with viz_tabs[2]:
            fig2 = px.pie(top_n_words, values="Count", names="Word", color="Word", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig2.update_layout(title=f"Top {n} Most Frequent Words (Pie Chart)")
            st.plotly_chart(fig2, use_container_width=True)
        # Download plot functionality
            if st.button("Download Pie Chart as High Resolution Image"):
                        buffered = BytesIO()
                        fig2.write_image(buffered, format="png", width=1200, height=800, scale=2)
                        st.markdown(get_image_download_link(buffered, "png"), unsafe_allow_html=True)
        #3rd tab
        with viz_tabs[4]:
             # Word count table
             st.subheader("Word Count Table")
             st.dataframe(word_count)
             st.markdown(get_table_download_link(word_count, "word_count.csv", "Download Word Count Table"), unsafe_allow_html=True)           
            # End of Streamlit app
           
        

else:
        st.write("No text found in the uploaded file.")
