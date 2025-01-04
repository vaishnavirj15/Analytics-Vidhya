import requests
from bs4 import BeautifulSoup
import pandas as pd
from rapidfuzz import process, fuzz
import gradio as gr

# Step 1: Scrape data from the Analytics Vidhya free courses page
page_url = "https://courses.analyticsvidhya.com/pages/all-free-courses"
response = requests.get(page_url)
response.raise_for_status()

html_parser = BeautifulSoup(response.content, 'html.parser')

course_data = []

# Extract details of each course
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

# Step 2: Create a DataFrame
course_df = pd.DataFrame(course_data)

# Step 3: Function to search courses with fuzzy matching
def fetch_courses(user_query):
    query = user_query.lower()

    # Perform fuzzy matching against course names and categories
    name_matches = process.extract(
        query, 
        course_df['course_name'].str.lower(), 
        scorer=fuzz.partial_ratio, 
        limit=10
    )
    category_matches = process.extract(
        query, 
        course_df['course_category'].str.lower(), 
        scorer=fuzz.partial_ratio, 
        limit=10
    )

    # Combine matching indices
    matched_indices = set(
        idx for match, score, idx in name_matches + category_matches if score > 50
    )
    matched_courses = course_df.iloc[list(matched_indices)]

    # Generate HTML output for the results
    if not matched_courses.empty:
        output_html = '<div class="search-results">'
        for _, course in matched_courses.iterrows():
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

# Step 4: New Gradio Interface design
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
"""

# Gradio Interface
tool_interface = gr.Interface(
    fn=fetch_courses,
    inputs=gr.Textbox(label="Search for Free Courses", placeholder="Type keywords like 'Data Science' or 'Python'"),
    outputs=gr.HTML(label="Search Results"),
    title="Free Course Finder",
    description="Quickly find free courses available on Analytics Vidhya by keyword or category.",
    css=custom_style,
    examples=[
        ["Machine Learning"],
        ["Business Analytics"],
        ["Python Programming"],
        ["Deep Learning"]
    ]
)

if __name__ == "__main__":
    tool_interface.launch()
