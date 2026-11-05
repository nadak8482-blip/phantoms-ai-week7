import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="phantoms_week7_collection"
)

documents = [
    "Python lists are mutable sequences that can store items of different types.",
    "Git branches let developers work on features without affecting the main code.",
    "A REST API exposes resources through HTTP methods like GET and POST.",
    "SQL JOINs combine rows from two tables based on a related column.",
    "Regular walking for thirty minutes a day improves heart health.",
    "Drinking enough water helps maintain energy and concentration.",
    "Sleep of seven to eight hours supports muscle recovery and memory.",
    "Stretching before exercise can reduce the risk of muscle injuries.",
    "To make rice fluffy, rinse it first and let it steam after cooking.",
    "Letting dough rest allows the gluten to relax and makes bread softer.",
    "Searing meat at high heat creates a flavorful brown crust.",
    "Adding salt to pasta water seasons the noodles from the inside."
]

ids = [
    "prog_1", "prog_2", "prog_3", "prog_4",
    "fit_1", "fit_2", "fit_3", "fit_4",
    "cook_1", "cook_2", "cook_3", "cook_4"
]

metadatas = [
    {"topic": "programming"},
    {"topic": "programming"},
    {"topic": "programming"},
    {"topic": "programming"},
    {"topic": "fitness"},
    {"topic": "fitness"},
    {"topic": "fitness"},
    {"topic": "fitness"},
    {"topic": "cooking"},
    {"topic": "cooking"},
    {"topic": "cooking"},
    {"topic": "cooking"}
]

existing_count = collection.count()
if existing_count == 0:
    collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )
    print("Successfully added documents to the collection.")
else:
    print("Collection already exists. Skipping addition to prevent duplication.")

queries = [
    "How do I store different kinds of values together in Python?",
    "How can I avoid hurting myself when working out?",
    "Why is my bread dense and hard?",
    "What is the best way to merge data from two database tables?",
    "How do I deploy a rocket to Mars?"
]

print("\n" + "-" * 50)
print("Running the Queries:")
print("-" * 50)

for i, query in enumerate(queries, 1):
    print
