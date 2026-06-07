import logging
import streamlit as st
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain.vectorstores.utils import filter_complex_metadata
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title
from langchain.schema import Document
import tempfile
import os
from langchain.retrievers import BM25Retriever 
from langchain.retrievers import EnsembleRetriever
# from db_utils import log_interaction
from dotenv import load_dotenv  # ADD THIS
from langchain_openai import ChatOpenAI  
load_dotenv() 
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatPDF:
    def __init__(self):
        self.vector_store = None
        self.retriever = None
        self.chain = None
    
    def __init__(self):

        self.model = ChatOpenAI(
            model="deepseek-chat", 
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),  # Your API key
            base_url="https://api.deepseek.com/v1",  # OpenRouter endpoint
            default_headers={
                "HTTP-Referer": "http://localhost:5000",  # Optional: Your site URL
                "X-Title": "RAG Assistant",  # Optional: Your app name
            }
        )
        self.prompt = PromptTemplate.from_template(
            """
            You are a hospital SOP assistant.

            Your job is to read the provided context and return a clear, structured SOP (Standard Operating Procedure).

            Instructions:
            - Extract only relevant information from the context.
            - Present the answer as step-by-step instructions.
            - Keep it simple, clear, and practical.
            - Use bullet points or numbered steps.
            - Do not add any information not present in the context.
            - Never invent information, if the answer is not found, say: "Missing from provided context."

            If the Question contains anything other than the healthcare SOP, immediately answer:
            "I can only help with Medical SOP queries."

            OR

            If the Question asks for any personal medical advice like what medicine to take etc, immediately answer:
            "I cannot help with medical advice."

            For simple factual questions, give a short 1-2 sentence answer.

            Format:
            - Title (if applicable)
            - Steps / Instructions
            - Notes (if any)

            Question: {question}

            Context:
            {context}

            Answer:
                        """
                        
        )
        logger.info("ChatPDF initialized")

    def classify_query(self, query: str) -> dict:
        query_lower = query.lower()
        
        factual_patterns = [
            "what is", "SOP for", "when was", "when should", "date", "time", "duration",
            "dosage", "dose", "frequency", "how many", "how much",
            "vital signs", "normal range", "reference range",
            "patient id", "bed number", "room number",
            "lab value", "test result", "report value",
            "exactly", "specific", "measurement"
        ]
        
        analysis_patterns = [
            "why", "reason", "cause", "indication", "contraindication",
            "complication", "risk", "benefit",
            "diagnosis", "differential", "assessment",
            "interpret", "interpretation", "clinical reasoning",
            "justification", "rationale",
            "when to escalate", "severity", "priority"
        ]
        
        process_patterns = [
            "how to", "steps", "procedure", "protocol", "workflow",
            "admission process", "discharge process",
            "triage", "screening", "assessment process",
            "management", "treatment plan", "care plan",
            "guidelines", "sop", "instructions",
            "what to do if", "in case of", "handling",
            "requirements", "criteria"
        ]
        
        if any(pattern in query_lower for pattern in factual_patterns):
            return {
                "type": "factual",
                "k_value": 8,
                "description": "Factual extraction - focused retrieval"
            }
        elif any(pattern in query_lower for pattern in analysis_patterns):
            return {
                "type": "analysis", 
                "k_value": 22,
                "description": "Clinical analysis - comprehensive retrieval"
            }
        elif any(pattern in query_lower for pattern in process_patterns):
            return {
                "type": "process",
                "k_value": 15,
                "description": "Process/protocol - moderate retrieval"
            }
        else:
            return {
                "type": "general",
                "k_value": 18,
                "description": "General query - balanced retrieval"
            }

    def create_dynamic_retriever(self, k_value: int):
        """Create retriever with dynamic k values based on query type"""
        
        # Adjust k values proportionally
        similarity_k = k_value
        mmr_k = max(int(k_value * 0.8), 5)  # Slightly less for MMR
        keyword_k = max(int(k_value * 0.8), 5)  # Match MMR
        mmr_fetch_k = k_value * 3  # Keep fetch_k ratio
        
        logger.info(f"Creating dynamic retriever with similarity_k={similarity_k}, mmr_k={mmr_k}, keyword_k={keyword_k}")
        
        # Enhanced temporal-aware retriever setup with dynamic k
        similarity_retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": similarity_k}
        )

        # MMR for diversity
        mmr_retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": mmr_k,
                "fetch_k": mmr_fetch_k,
                "lambda_mult": 0.5
            }
        )

        # Create new keyword retriever with dynamic k
        # (We need to recreate this since BM25Retriever k is set at initialization)
        processed_chunks = []
        if hasattr(self, '_processed_chunks'):
            processed_chunks = self._processed_chunks
        else:
            # Fallback - recreate from vector store (less efficient but works)
            logger.warning("Processed chunks not cached, may affect performance")
            
        keyword_retriever = BM25Retriever.from_documents(processed_chunks) if processed_chunks else None
        if keyword_retriever:
            keyword_retriever.k = keyword_k

        # Create ensemble with available retrievers
        retrievers = [similarity_retriever, mmr_retriever]
        weights = [0.6, 0.4]
        
        if keyword_retriever:
            retrievers.append(keyword_retriever)
            weights = [0.5, 0.3, 0.2]
        
        return EnsembleRetriever(
            retrievers=retrievers,
            weights=weights
        )

    def ingest(self, pdf_file_path: str):
        if os.path.exists("./chroma_db"):
            logger.info("Vector DB found.")
            return
        try:
            logger.info(f"Loading and partitioning PDF: {pdf_file_path}")
            elements = partition_pdf(
                filename=pdf_file_path,
                strategy="hi_res",
                model_name="yolox"
                # infer_table_structure=True,
                # extract_images_in_pdf=True
            )
            logger.info(f"Partitioned into {len(elements)} elements")

            # Perform smart chunking
            chunks = chunk_by_title(
                elements=elements,
                max_characters=1500,
                overlap = 400,
                combine_text_under_n_chars=75,
                new_after_n_chars=1200
            )
            logger.info(f"Chunked into {len(chunks)} semantic chunks")

            # Convert ElementMetadata to dictionary for compatibility
            processed_chunks = []
            for chunk in chunks:
                metadata = {}
                if hasattr(chunk, 'metadata') and chunk.metadata:
                    # Convert ElementMetadata to dict
                    metadata_dict = chunk.metadata.to_dict() if hasattr(chunk.metadata, 'to_dict') else {}
                    # Filter to simple types (strings, numbers, etc.)
                    for key, value in metadata_dict.items():
                        if isinstance(value, (str, int, float, bool, type(None))):
                            metadata[key] = value
                        else:
                            metadata[key] = str(value)  # Convert complex types to string
                processed_chunks.append(Document(page_content=chunk.text, metadata=metadata))
            
            # Apply filter_complex_metadata
            processed_chunks = filter_complex_metadata(processed_chunks)

            # Cache processed chunks for dynamic retriever creation
            self._processed_chunks = processed_chunks

            # Create vector store
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
            # self.vector_store = Chroma.from_documents(documents=processed_chunks, embedding=embeddings)
            persist_dir = "./SOP_chromaDB"

            self.vector_store = Chroma.from_documents(
                documents=processed_chunks,
                embedding=embeddings,
                persist_directory=persist_dir
            )

            # IMPORTANT: actually save to disk
            self.vector_store.persist()
            logger.info("Vector store created")

            # Create initial retriever (will be replaced dynamically per query)
            self.retriever = self.create_dynamic_retriever(k_value=18)  # Default value

            logger.info("Dynamic retriever system initialized")

            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)
            self.chain = (
                {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
                | self.prompt
                | self.model
                | StrOutputParser()
            )
            logger.info("Chain created successfully")
        except Exception as e:
            logger.error(f"Error in ingest: {str(e)}")
            raise

    def load_vector_store(self):
        # Make the path absolute to the services folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        persist_dir = os.path.join(current_dir, "SOP_chromaDB")

        if not os.path.exists(persist_dir):
            logger.warning(f"Persistent DB not found at {persist_dir}")
            return False

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )

        self.vector_store = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings
        )

        self.retriever = self.create_dynamic_retriever(k_value=18)
        
        # Build the chain instantly!
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
            
        self.chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.model
            | StrOutputParser()
        )
        return True



    def ask(self, query: str):
        if not self.vector_store:
            logger.warning("No vector store found, PDF not ingested")
            return "Please, add a PDF document first."

        logger.info(f"Processing query: {query}")
        
        # Classify query and get optimal parameters
        classification = self.classify_query(query)
        logger.info(f"Query classified as: {classification['type']} - {classification['description']}")
        
        # Create dynamic retriever based on classification
        dynamic_retriever = self.create_dynamic_retriever(classification['k_value'])
        
        # Get relevant documents with optimized retrieval
        retrieved_docs = dynamic_retriever.get_relevant_documents(query)
        
        logger.info(f"Retrieved {len(retrieved_docs)} chunks for {classification['type']} query")
        for i, doc in enumerate(retrieved_docs):
            logger.info(
                f"Retrieved chunk {i} (score: {doc.metadata.get('score', 'N/A')}): {doc.page_content[:200]}..."
            )
        
      

        # Format documents
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        # Create chain with dynamic retriever
        chain = (
            {"context": lambda _: format_docs(retrieved_docs), "question": RunnablePassthrough()}
            | self.prompt
            | self.model
            | StrOutputParser()
        )
        
        # Get model answer
        answer = chain.invoke(query)

        # Try to capture doc_name (from first retrieved doc's metadata)
        doc_name = None
        if retrieved_docs and "source" in retrieved_docs[0].metadata:
            doc_name = os.path.basename(retrieved_docs[0].metadata["source"])

        # Log interaction with classification info
        # log_interaction(f"{query} [Type: {classification['type']}]", answer, doc_name)

        return answer

    def clear(self):
        self.vector_store = None
        self.retriever = None
        self.chain = None
        self._processed_chunks = None
        logger.info("Session cleared")
