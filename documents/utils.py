from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_openai import ChatOpenAI
import os
import re
import unicodedata

embeddings = SentenceTransformerEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")

def get_vectorstore():
    return Chroma(
        collection_name="documents",
        embedding_function=embeddings,
        host="chroma",
        port=8000,
    )

def chunk_text(text, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_text(text)

def store_chunks(document_id, chunks):
    vectorstore = get_vectorstore()
    metadatas = [{"document_id": document_id} for _ in chunks]
    vectorstore.add_texts(chunks, metadatas=metadatas)

def normalize_query(text):
    text = unicodedata.normalize("NFKC", text)

    # Arabic characters → Persian equivalents
    text = text.replace("ي", "ی")
    text = text.replace("ك", "ک")

    # Remove zero-width / invisible characters
    text = text.replace("\u200c", " ")
    text = text.replace("\u200d", "")
    text = text.replace("\ufeff", "")

    # Collapse repeated whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def answer_question(question, k=5):
    question = normalize_query(question)
    # Step 1: retrieve the most relevant chunks from Chroma
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(question, k=k)

    # Step 2: build a prompt combining the question + retrieved chunks
    context = "\n\n".join([doc.page_content for doc in results])
    prompt = f"""Answer the question based only on the context below. If the answer isn't in the context, say you don't know.

Context:
{context}

Question: {question}

Answer:"""

    # Step 3: send it to the LLM and get the answer back
    llm = ChatOpenAI(
    model="nvidia/nemotron-3-nano-30b-a3b:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    temperature=0,
    )
    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "sources": [doc.metadata for doc in results],
    }

def delete_document_chunks(document_id):
    vectorstore = get_vectorstore()

    records = vectorstore.get(
        where={"document_id": document_id}
    )

    ids = records.get("ids", [])

    if ids:
        vectorstore.delete(ids=ids)

