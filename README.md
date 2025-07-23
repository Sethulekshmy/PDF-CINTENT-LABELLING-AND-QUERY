# 📄 PDF Content Labeling and Query Interface



This project provides an intelligent and interactive tool to extract, label, and query content from PDF documents using local AI models. The application is built with Streamlit for the frontend and uses LLMs (via Ollama) for content labeling and answering user queries.

---

## Objective

- Extract text, images, and table-like structures from PDF files.
- Label content using natural language processing (e.g., Title, Header, Table).
- Provide a query interface that allows users to ask questions about the document content.
- Support local model execution using the Ollama framework.

---

## Approach

### 1. PDF Parsing and Content Extraction
- Uses PyMuPDF (`fitz`) to extract:
  - Text from each page
  - Embedded images
  - Basic metadata (author, title, number of pages, etc.)
  - Table-like text blocks using heuristic analysis

### 2. Content Labeling
- Extracted content is summarized and sent to a local LLM.
- The model categorizes content into:
  - Title
  - Header
  - Paragraph
  - List
  - Table
  - Image

### 3. Query Interface
- Users can interactively ask questions about a specific page.
- The question, along with the relevant content, is passed to the LLM.
- The model returns precise answers in context.


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

