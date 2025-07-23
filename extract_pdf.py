import streamlit as st
import fitz
import ollama
import os
import base64
from io import BytesIO
from PIL import Image

# --- Page Config ---
st.set_page_config(page_title="PDF CONTENT LABELLING", layout="wide")
st.title("📄 Enhanced PDF Content Analyzer")

# --- Cartoon Bird Welcome Section ---
col1, col2 = st.columns([1, 4])
with col1:
    bird_img = Image.open("cartoon_bird.png")
    st.image(bird_img, width=120)
with col2:
    st.markdown("""
    ### 🕊️  Welcome to the Smart PDF Content Labeller
    📋 This powerful app extracts 📑 text, 🖼️ images, and 📊 tables from your PDF —then uses fast, local AI models 🧠 to label, analyze, and organize everything for you
    
    👉 Upload a PDF below to get started!
    """)

# --- Ollama Client Setup ---
def check_ollama_connection():
    try:
        models = ollama.list()
        if not models['models']:
            st.error("❌ No Ollama models found. Please run: `ollama pull llama3.2:1b`")
            return False
        return True
    except Exception as e:
        st.error(f"❌ Ollama connection failed: {e}")
        return False

# --- PDF Content Extraction ---
def extract_content_from_pdf(pdf_file):
    content_by_page = {}
    progress_bar = st.progress(0)
    status_text = st.empty()
    try:
        with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
            total_pages = len(doc)
            for i, page in enumerate(doc):
                status_text.text(f"Processing page {i+1} of {total_pages}...")
                progress_bar.progress((i + 1) / total_pages)

                page_content = {'text': '', 'images': [], 'tables': []}
                text = page.get_text()
                if text.strip():
                    page_content['text'] = text.strip()

                # Images
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        if pix.n - pix.alpha < 4:
                            img_data = pix.tobytes("png")
                            page_content['images'].append({
                                'index': img_index + 1,
                                'size': f"{pix.width}x{pix.height}",
                                'data': base64.b64encode(img_data).decode()
                            })
                        pix = None
                    except:
                        pass

                # Tables
                lines = text.split('\n')
                potential_tables = []
                current_table = []
                for line in lines:
                    if '\t' in line or len(line.split()) > 4:
                        current_table.append(line.strip())
                    else:
                        if len(current_table) > 2:
                            potential_tables.append('\n'.join(current_table))
                        current_table = []
                if len(current_table) > 2:
                    potential_tables.append('\n'.join(current_table))

                page_content['tables'] = potential_tables
                if page_content['text'] or page_content['images'] or page_content['tables']:
                    content_by_page[f"Page {i+1}"] = page_content
    except Exception as e:
        st.error(f"❌ Error extracting content from PDF: {e}")
        return {}
    finally:
        progress_bar.empty()
        status_text.empty()
    return content_by_page

# --- Description Creator ---
def create_content_description(page_content):
    description = []
    if page_content['text']:
        description.append(f"TEXT CONTENT:\n{page_content['text']}")
    if page_content['images']:
        description.append(f"\nIMAGES FOUND: {len(page_content['images'])} images")
        for img in page_content['images']:
            description.append(f"- Image {img['index']}: Size {img['size']}")
    if page_content['tables']:
        description.append(f"\nTABLES FOUND: {len(page_content['tables'])} tables")
        for i, table in enumerate(page_content['tables'], 1):
            description.append(f"\nTable {i}:\n{table}")
    return '\n'.join(description)

# --- Labeling Function ---
def label_pdf_content(content_by_page, model_name="llama3.2:1b"):
    labeled_content = {}
    progress_bar = st.progress(0)
    status_text = st.empty()
    try:
        total_pages = len(content_by_page)
        with open("output_log.txt", "w", encoding="utf-8") as log_file:
            for i, (page, content) in enumerate(content_by_page.items()):
                status_text.text(f"Labeling {page}...")
                progress_bar.progress((i + 1) / total_pages)

                try:
                    full_content = create_content_description(content)
                    prompt = f"""Label and categorize this PDF page content:

{full_content}

Provide clear labels like: Title, Header, Paragraph, Image, Table, List, etc."""
                    response = ollama.chat(
                        model=model_name,
                        messages=[{'role': 'user', 'content': prompt}],
                        options={'temperature': 0.3}
                    )

                    labeled_text = response['message']['content']
                    labeled_content[page] = {
                        'original': content,
                        'labeled': labeled_text,
                        'full_content': full_content
                    }
                    log_file.write(f"{page}\nPROMPT:\n{prompt}\n\nRESPONSE:\n{labeled_text}\n\n")

                except Exception as e:
                    error_msg = f"Error labeling page: {e}"
                    labeled_content[page] = {
                        'original': content,
                        'labeled': error_msg,
                        'full_content': full_content
                    }
                    log_file.write(f"{page}\n{error_msg}\n\n")
    except Exception as e:
        st.error(f"❌ Error during labeling: {e}")
    finally:
        progress_bar.empty()
        status_text.empty()
    return labeled_content

# --- Answering Questions ---
def answer_question(page_data, question, model_name="llama3.2:1b"):
    try:
        prompt = f"""Answer based on this PDF page content:

{page_data['full_content']}

Question: {question}

Provide a clear, specific answer."""
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {e}"

# --- Continue only if Ollama works ---
if not check_ollama_connection():
    st.stop()

# --- Model selection ---
try:
    models = ollama.list()
    model_names = [model['name'] for model in models['models']]
    selected_model = st.selectbox("Select Model", model_names, index=0)
    st.success(f"✅ Using: {selected_model}")
except:
    selected_model = "llama3.2:1b"
    st.info(f"Using default: {selected_model}")

# --- Upload PDF ---
uploaded_pdf = st.file_uploader("📤 Upload your PDF here", type="pdf")

if uploaded_pdf:
    st.subheader("🔍 Extracting Content...")
    content_by_page = extract_content_from_pdf(uploaded_pdf)
    if not content_by_page:
        st.error("❌ No content extracted.")
        st.stop()

    st.success(f"✅ Extracted {len(content_by_page)} pages!")

    total_images = sum(len(content['images']) for content in content_by_page.values())
    total_tables = sum(len(content['tables']) for content in content_by_page.values())

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pages", len(content_by_page))
    with col2:
        st.metric("Images", total_images)
    with col3:
        st.metric("Tables", total_tables)

    st.subheader("🤖 Labeling Content...")
    labeled_output = label_pdf_content(content_by_page, selected_model)

    if labeled_output:
        st.success("✅ Labeling completed!")
        page_keys = list(labeled_output.keys())
        selected_page = st.selectbox("📄 Select Page", page_keys)

        if selected_page:
            page_data = labeled_output[selected_page]

            st.subheader("🧾 Labeled Content")
            with st.expander("🔎 View Labeled Output"):
                lines = page_data['labeled'].split('\n')
                for line in lines:
                    line_lower = line.lower()
                    if line_lower.startswith("title"):
                        st.markdown(f"### 🏷️ **{line}**")
                    elif line_lower.startswith("header"):
                        st.markdown(f"#### 📌 **{line}**")
                    elif line_lower.startswith("paragraph"):
                        st.markdown(f"✏️ {line}")
                    elif line_lower.startswith("image"):
                        st.markdown(f"🖼️ {line}")
                    elif line_lower.startswith("table"):
                        st.markdown(f"📊 {line}")
                    elif line_lower.startswith("list"):
                        st.markdown(f"🔢 {line}")
                    else:
                        st.markdown(line)

            if page_data['original']['images']:
                st.subheader("🖼️ Images on this page")
                for img in page_data['original']['images']:
                    img_bytes = base64.b64decode(img['data'])
                    st.image(img_bytes, caption=f"Image {img['index']} ({img['size']})")

            st.subheader("💬 Ask Questions")

# --- Q&A History ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

for chat in st.session_state.chat_history:
    st.chat_message("user").markdown(chat["question"])
    st.chat_message("assistant").markdown(chat["answer"])

user_input = st.chat_input("Ask another question.")

if user_input and uploaded_pdf:
    with st.spinner("Thinking..."):
        response = answer_question(page_data, user_input, selected_model)
        st.session_state.chat_history.append({
            "question": user_input,
            "answer": response
        })
        st.chat_message("user").markdown(user_input)
        st.chat_message("assistant").markdown(response)

st.sidebar.info("")
