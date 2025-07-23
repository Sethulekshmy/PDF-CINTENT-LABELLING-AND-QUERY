# 📄 PDF Content Labeling and Query Interface

This project provides an intelligent and interactive solution to extract, label, and query PDF documents using AI models. It uses **Streamlit** for the frontend UI and **LLM-based processing** to interpret and answer user queries on PDF content and metadata.

---

## Objective

- Extract and label content (text/images/metadata) from PDF documents.
- Provide a user-friendly interface for querying PDF contents using natural language.
- Deliver relevant and accurate answers using a large language model (LLM).

---

##  Approach

### 1. **PDF Parsing and Content Extraction**
- The application uses **PyMuPDF (fitz)** to extract:
  - Raw text
  - Page structure
  - Embedded images
  - Metadata (author, title, number of pages, etc.)

### 2. **Content Labeling**
- After extracting raw data, content is semantically categorized as:
  - Headings
  - Paragraphs
  - Tables
  - Figures
  - References
- This is done with the help of an LLM.

### 3. **Query Interface with LLM**
- User queries entered through the UI are passed to an LLM (e.g., via `ollama`, OpenAI, etc.).
- The model interprets the query in the context of the extracted PDF content and returns the answer.

 Setup Instructions
1. Clone this Repository

git clone https://github.com/your-username/pdf-content-labeller.git
cd pdf-content-labeller
2.Install Requirements
pip install -r requirements.txt

3.streamlit run app.py


## Usage

Start the app using streamlit run app.py.

Upload a PDF using the uploader widget.

View:

Extracted pages, images, and tables.

Labelled content by the LLM.

Ask questions about any page using the chat interface.

See chat history and download full prompt/response logs in output_log.txt.

