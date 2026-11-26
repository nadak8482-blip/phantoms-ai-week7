import chromadb
from pypdf import PdfReader

pdf_path = "Database Assignment 2.pdf"
reader = PdfReader(pdf_path)

pages_data = []
for page_index, page in enumerate(reader.pages, start=1):
    extracted_text = page.extract_text() or ""
    cleaned_text = " ".join(extracted_text.split())
    if cleaned_text:
        pages_data.append({
            "page": page_index,
            "source": pdf_path,
            "text": cleaned_text
        })


def split_with_overlap(text, chunk_size, overlap):
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")
    chunks = []
    start = 0
    step = chunk_size - overlap
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(chunk_text)
        start += step
    return chunks


configs = {
    "small": {"chunk_size": 140, "overlap": 30},
    "medium": {"chunk_size": 500, "overlap": 100},
    "large": {"chunk_size": 1500, "overlap": 250}
}

client = chromadb.PersistentClient(path="./chroma_chunking_db")

for config_name, params in configs.items():
    collection_name = f"db_assign_chunks_{config_name}"
    existing_names = [c.name for c in client.list_collections()]
    if collection_name in existing_names:
        client.delete_collection(name=collection_name)

    collection = client.get_or_create_collection(name=collection_name)

    all_docs = []
    all_ids = []
    all_metas = []

    counter = 1
    for item in pages_data:
        page_chunks = split_with_overlap(
            item["text"],
            params["chunk_size"],
            params["overlap"]
        )
        for chunk_idx, chunk_str in enumerate(page_chunks, start=1):
            all_docs.append(chunk_str)
            all_ids.append(f"{config_name}_p{item['page']}_c{chunk_idx}_{counter}")
            all_metas.append({
                "source": item["source"],
                "page": item["page"],
                "config": config_name
            })
            counter += 1

    if all_docs:
        collection.add(
            documents=all_docs,
            ids=all_ids,
            metadatas=all_metas
        )
    print(f"Configuration '{config_name}': stored {len(all_docs)} chunks.")

questions = [
    "What is the Primary Key in the given unnormalized table?",
    "Why does the table satisfy 1NF?",
    "Why is partial dependency impossible in this table when checking 2NF?",
    "What are the three database anomalies mentioned when storing JobTitle directly?",
    "Which attribute acts as a Foreign Key in the Employees table after redesigning for 3NF?",
    "How does JobID relate to JobTitle in the original table, and how is that relationship separated in the 3NF redesign?",
    "Which employees have JobID J01, what are their salaries, and how are they represented in the normalized 3NF tables?",
    "How does moving from the original table to the 3NF schema solve data repetition and update problems?",
    "How do you write a SQL query using a LEFT JOIN and window functions to rank employees by salary per department?",
    "What are the best practices for configuring Kubernetes autoscaling policies for a high-traffic microservice?"
]

for config_name in configs:
    collection = client.get_collection(name=f"
