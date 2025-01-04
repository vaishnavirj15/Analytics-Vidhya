# Analytics-Vidhya
My approach to solve the problem statement shared by Analytics Vidhya on developing a search tool.
I have used two methods both the approach don't use LLM. 
1. The first tool uses web scraping to gather course data, then generates embeddings for course titles using the Hugging Face embedding model, and finally performs similarity searches using FAISS (Facebook AI Similarity Search). The user interface is built using Gradio, allowing easy interaction for searching free courses by simply typing keywords.
2. The second tool enables users to search for free courses available on Analytics Vidhya using keyword or category matching. The tool provides a user-friendly interface and uses fuzzy matching to find relevant courses based on user input.

RAG LINK: https://huggingface.co/spaces/rajvaishnavi455/assignment-analytics-vidhya
Fuzzy Matching: https://huggingface.co/spaces/rajvaishnavi455/analytics-vidya-free-course
