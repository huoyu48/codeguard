import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

class KnowledgeBase:
    def __init__(self, persist_dir: str = "./chroma_data"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedder = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="coding_standards",
            embedding_function=self.embedder,  # type: ignore
        )
    def load_documents(self,file_path:str):
        """加载编码规范文档到数据库"""
        with open(file_path, "r") as f:
            text = f.read()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50
        )
        chunks = splitter.split_text(text)
        self.collection.add(
            documents=chunks,
            ids=[f"doc_{i}" for i in range(len(chunks))],
        )

    def search(self, query: str, top_k: int = 5) -> list[str]:
        """检索与代码片段最相关的规范条目"""
        results = self.collection.query(
            query_texts=[query], n_results=top_k
        )
        return results["documents"][0]  # type: ignore
                            