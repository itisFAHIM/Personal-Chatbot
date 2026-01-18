import os
import chromadb
from sentence_transformers import SentenceTransformer
from django.conf import settings


DB_PATH = os.path.join(settings.BASE_DIR, "chroma_db")
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name="project_code")


embed_model = SentenceTransformer('all-MiniLM-L6-v2')

def index_project_code():
    """
    Scans the entire F:\Fahm_Code_Korbi folder and saves it to the vector DB.
    """
    base_dir = settings.BASE_DIR
    
   
    ignore_dirs = ['venv', '__pycache__', '.git', 'chroma_db', 'db.sqlite3']
    allowed_exts = ['.py', '.html', '.css', '.js', '.md']

    documents = []
    metadatas = []
    ids = []

    print("🚀 Starting Codebase Indexing...")
    

    for root, dirs, files in os.walk(base_dir):
       
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in allowed_exts):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    
                    if not content.strip(): continue

                   
                    rel_path = os.path.relpath(file_path, base_dir)
                    
                    documents.append(content)
                    metadatas.append({"source": rel_path})
                    ids.append(rel_path)
                    
                    print(f"📄 Indexed: {rel_path}")

                except Exception as e:
                    print(f"❌ Error reading {file}: {e}")

    
    if documents:
        
        try:
            collection.delete(where={}) 
        except:
            pass
            
     
        batch_size = 50
        for i in range(0, len(documents), batch_size):
            end = i + batch_size
            
            
            embeddings = embed_model.encode(documents[i:end]).tolist()
            
            collection.add(
                embeddings=embeddings,
                documents=documents[i:end],
                metadatas=metadatas[i:end],
                ids=ids[i:end]
            )
            print(f"✅ Processed batch {i} to {end}")

    return f"Successfully indexed {len(documents)} files!"

def search_codebase(query, n_results=3):
    """
    Searches the database for code relevant to the query.
    """

    query_embedding = embed_model.encode([query]).tolist()
    
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    
    context_text = ""
    for i in range(len(results['documents'][0])):
        filename = results['metadatas'][0][i]['source']
        content = results['documents'][0][i]
        context_text += f"\n\n--- RELEVANT FILE FOUND: {filename} ---\n{content}\n"
    
    return context_text