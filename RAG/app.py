import requests
from bs4 import BeautifulSoup
import pandas as pd
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import gradio as gr

# Step 1: Scrape data from Analytics Vidhya's free courses page
def scrape_courses():
    page_url = "https://courses.analyticsvidhya.com/pages/all-free-courses"
    response = requests.get(page_url)
    response.raise_for_status()

    html_parser = BeautifulSoup(response.content, 'html.parser')
    course_data = []

    # Extract course details
    for section in html_parser.find_all('div', class_='course-cards__container'):
        section_heading = section.find('h3', class_='section__heading')
        category_name = section_heading.get_text(strip=True) if section_heading else "Miscellaneous"

        for card in section.find_all('a', class_='course-card'):
            course_title = card.find('h3')
            course_image = card.find('img', class_='course-card__img')

            if course_title and course_image:
                title = course_title.get_text(strip=True)
                image_url = course_image['src']
                link = card['href']

                # Ensure full URL
                if not link.startswith('http'):
                    link = 'https://courses.analyticsvidhya.com' + link

                course_data.append({
                    'course_name': title,
                    'course_category': category_name,
                    'thumbnail': image_url,
                    'course_url': link
                })
    return pd.DataFrame(course_data)

# Step 2: Generate embeddings and create FAISS index using HuggingFace embeddings
def create_faiss_index(course_texts):
    try:
        # Load HuggingFace Embedding model
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # Add course metadata (index) for each course
        metadata = [{"index": idx} for idx in range(len(course_texts))]

        # Create FAISS vector store with metadata
        vector_store = FAISS.from_texts(course_texts, embeddings, metadatas=metadata)
        print("FAISS index created successfully!")
        return vector_store
    except Exception as e:
        print(f"Error during FAISS index creation: {str(e)}")
        return None

# Step 3: Define search function
def search_courses(user_query):
    if vector_store is None:
        return '<p class="error">Error: FAISS index not initialized. Please check the embedding setup.</p>'
    try:
        # Perform similarity search
        results = vector_store.similarity_search(user_query, k=10)
        if results:
            output_html = '<div class="search-results">'
            for result in results:
                course_idx = result.metadata['index']  # Access the index from metadata
                course = course_df.iloc[course_idx]
                output_html += f'''
                <div class="course-box">
                    <img src="{course['thumbnail']}" alt="{course['course_name']}" class="course-thumbnail"/>
                    <div class="course-details">
                        <h3>{course['course_name']}</h3>
                        <p><strong>Category:</strong> {course['course_category']}</p>
                        <a href="{course['course_url']}" target="_blank" class="view-course">Explore Course</a>
                    </div>
                </div>'''
            output_html += '</div>'
            return output_html
        else:
            return '<p class="no-matches">No matching courses found. Please refine your query.</p>'
    except Exception as e:
        return f'<p class="error">Error during search: {str(e)}</p>'

# Step 4: Initialize scraping, FAISS index, and Gradio interface
course_df = scrape_courses()
course_texts = course_df['course_name'].tolist()  # Texts for embeddings
vector_store = create_faiss_index(course_texts)

# Custom CSS for Gradio interface
custom_style = """
body {
    font-family: 'Roboto', sans-serif;
    background-color: #f7f9fc;
    margin: 0;
    padding: 0;
}
.search-results {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    justify-content: center;
}
.course-box {
    background-color: #fff;
    border: 1px solid #e3e3e3;
    border-radius: 8px;
    overflow: hidden;
    width: 300px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s;
}
.course-box:hover {
    transform: translateY(-5px);
}
.course-thumbnail {
    width: 100%;
    height: 150px;
    object-fit: cover;
}
.course-details {
    padding: 15px;
}
.course-details h3 {
    margin: 0 0 10px;
    font-size: 18px;
    color: #333;
}
.course-details p {
    margin: 0 0 15px;
    font-size: 14px;
    color: #555;
}
.view-course {
    display: inline-block;
    padding: 10px 20px;
    background-color: #007bff;
    color: #fff;
    text-decoration: none;
    border-radius: 5px;
    font-size: 14px;
}
.view-course:hover {
    background-color: #0056b3;
}
.no-matches {
    text-align: center;
    font-size: 16px;
    color: #666;
    margin: 20px 0;
}
.error {
    color: red;
    font-size: 16px;
    text-align: center;
    margin: 20px;
}
"""

# Gradio Interface
tool_interface = gr.Interface(
    fn=search_courses,
    inputs=gr.Textbox(label="Search for Free Courses", placeholder="Type keywords like 'Data Science' or 'Python'"),
    outputs=gr.HTML(label="Search Results"),
    title="Find Free Courses",
    description="Quickly find free courses avalable on Analytics Vidhya using this tool.",
    css=custom_style,
    examples=[ 
        ["Generative AI"],
        ["Business Analytics"],
        ["Python Programming"]
    ]
)

if __name__ == "__main__":
    tool_interface.launch()
