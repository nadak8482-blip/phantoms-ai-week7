import glob
import json
import os
import chromadb
from pypdf import PdfReader


# ==========================================
# 1. إعدادات التقطيع والـ Retrieval (عدّلها حسب أفضل نتيجة وصلت لها في D2)
# ==========================================
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
TOP_K = 4

SYSTEM_PROMPT = """أنت مساعد تقني دقيق يعتمد حصرياً على السياق المرفق (Context) المستخرج من المستند.
التزم بالقواعد التالية بدقة تامة:
1. أجب فقط من المعلومات الموجودة صراحةً في مقاطع Context المرقّمة أدناه.
2. يُمنع منعاً باتاً استخدام معلوماتك الخارجية أو التخمين أو استنتاج أي معلومة غير مذكورة في Context.
3. إذا لم تكن الإجابة موجودة بوضوح في Context، اكتب بالحرف: "مش موجود في المستند" بدون تأليف أو إضافة.
4. عند وجود الإجابة، اذكر المصدر في نهاية الإجابة بصيغة: (المصدر: <اسم الملف>، صفحة <رقم الصفحة>).
"""

SAMPLE_QUERIES = [
    "What is the main topic or objective of this document?",
    "Summarize the key concepts discussed in the document.",
    "What database or storage architecture is mentioned?",
    "How are data models, tables, or entities structured?",
    "What are the main challenges, limitations, or trade-offs?",
    "What methods, algorithms, or workflows are described?",
    "What examples or use cases are provided?",
    "What rules, constraints, or best practices are highlighted?",
    "How is performance, indexing, or querying handled?",
    "What conclusions or recommendations are given?",
]


def find_pdf_file(search_dirs: list[str] | None = None) -> str:
    """يبحث عن ملف PDF في المجلد الحالي أو المجلدات الأب مثل nada أو مجلد W7D3."""
    if search_dirs is None:
        search_dirs = [".", "..", "../.."]

    for directory in search_dirs:
        pdfs = sorted(glob.glob(os.path.join(directory, "*.pdf")))
        if pdfs:
            return pdfs[0]

    raise FileNotFoundError(
        "لم يتم العثور على أي ملف PDF. تأكد من وضع ملف الـ PDF في مجلد المشروع."
    )


def extract_pages(pdf_path: str) -> list[tuple[int, str]]:
    reader = PdfReader(pdf_path)
    pages = []
    for page_num, page in enumerate(reader.pages, start=1):
        cleaned_text = " ".join((page.extract_text() or "").split())
        if cleaned_text:
            pages.append((page_num, cleaned_text))

    if not pages:
        raise ValueError("تم العثور على ملف PDF ولكن لا يحتوي على نص قابل للاستخراج.")
    return pages


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    step = max(chunk_size - overlap, 1)

    while start < len(text):
        end = min(start + chunk_size, len(text))
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= text:
            break
        start += step

    return chunks


def build_chroma_collection(pdf_path: str, chunk_size: int, overlap: int):
    source_name = os.path.basename(pdf_path)
    pages = extract_pages(pdf_path)

    ids, documents, metadatas = [], [], []
    chunk_counter = 0

    for page_num, page_text in pages:
        for piece in chunk_text(page_text, chunk_size=chunk_size, overlap=overlap):
            ids.append(f"chunk_{chunk_counter}")
            documents.append(piece)
            metadatas.append(
                {
                    "source": source_name,
                    "page": page_num,
                    "chunk_index": chunk_counter,
                }
            )
            chunk_counter += 1

    client = chromadb.Client()
    collection_name = "w7d3_rag_chunks"
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass

    collection = client.create_collection(name=collection_name)
    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return collection, source_name, len(documents)


def format_context(docs: list[str], metas: list[dict]) -> str:
    formatted_blocks = []
    for idx, (doc, meta) in enumerate(zip(docs, metas), start=1):
        src = meta.get("source", "unknown.pdf")
        page = meta.get("page", "?")
        formatted_blocks.append(f"[مقطع {idx} | المصدر: {src} | الصفحة: {page}]\n{doc}")
    return "\n\n".join(formatted_blocks)


def call_gemini(system_prompt: str, user_prompt: str, model_name: str = "gemini-2.5-flash") -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return (
            "[تنبيه: متغير البيئة GEMINI_API_KEY غير مضبوط. اضبطه لتوليد إجابة LLM الفعلية.]"
        )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
            ),
        )
        return (response.text or "").strip()
    except Exception as exc:
        return f"[خطأ أثناء استدعاء Gemini API]: {exc}"


def ask_with_rag(question: str, collection, top_k: int) -> dict:
    results = collection.query(query_texts=[question], n_results=top_k)
    docs = results["documents"][0] if results.get("documents") and results["documents"][0] else []
    metas = results["metadatas"][0] if results.get("metadatas") and results["metadatas"][0] else []
    dists = results["distances"][0] if results.get("distances") and results["distances"][0] else []

    context_str = format_context(docs, metas)
    user_prompt = (
        f"Context:\n{context_str}\n\n"
        f"السؤال:\n{question}\n\n"
        f"أجب بالاعتماد على Context فقط واذكر المصدر."
    )
    answer = call_gemini(SYSTEM_PROMPT, user_prompt)

    sources = [
        {
            "source": m.get("source"),
            "page": m.get("page"),
            "chunk_index": m.get("chunk_index"),
            "distance": round(float(d), 4),
        }
        for m, d in zip(metas, dists)
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": docs,
    }


def ask_without_rag(question: str) -> str:
    return call_gemini(
        "أجب عن السؤال بدقة وإيجاز من معلوماتك العامة.",
        question,
    )


def main():
    pdf_path = find_pdf_file()
    collection, source_name, total_chunks = build_chroma_collection(
        pdf_path=pdf_path,
        chunk_size=CHUNK_SIZE,
        overlap=CHUNK_OVERLAP,
    )

    print(f"المستند: {source_name} | عدد القطع المفهرسة: {total_chunks} | top_k={TOP_K}\n")

    rag_results = []
    for i, question in enumerate(SAMPLE_QUERIES, start=1):
        res = ask_with_rag(question, collection=collection, top_k=TOP_K)
        rag_results.append(res)

        top_src = res["sources"][0] if res["sources"] else {}
        print(f"Q{i:02d}: {question}")
        print(f"الإجابة: {res['answer']}")
        print(
            f"أقرب مصدر مسترجع: {top_src.get('source')} | صفحة {top_src.get('page')} | "
            f"chunk #{top_src.get('chunk_index')} | distance={top_src.get('distance')}"
        )
        print("-" * 70)

    print("\n=== مقارنة 3 أسئلة بدون RAG ===")
    no_rag_results = []
    for q in SAMPLE_QUERIES[:3]:
        no_rag_ans = ask_without_rag(q)
        no_rag_results.append({"question": q, "no_rag_answer": no_rag_ans})
        print(f"السؤال: {q}")
        print(f"بدون RAG: {no_rag_ans}")
        print("-" * 70)

    output_data = {
        "config": {
            "source": source_name,
            "chunk_size": CHUNK_SIZE,
            "overlap": CHUNK_OVERLAP,
            "top_k": TOP_K,
            "total_chunks": total_chunks,
        },
        "rag_10_queries": rag_results,
        "no_rag_3_queries": no_rag_results,
    }

    with open("rag_evaluation_output.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print("\nتم حفظ جميع المخرجات في rag_evaluation_output.json")


if __name__ == "__main__":
    main()
