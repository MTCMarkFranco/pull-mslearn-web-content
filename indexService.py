import os
import time
from azure.ai.vision.imageanalysis import ImageAnalysisClient as AzureImageAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from models.webContent import webContent
from openai import AzureOpenAI
from azure.search.documents.indexes.models import (
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch,
    SearchIndex,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    VectorSearchAlgorithmConfiguration
)

class indexService:
    def __init__(self):
        self.key = os.getenv('SEARCH_KEY')
        self.search_endpoint = os.getenv('SEARCH_ENDPOINT')
        self.search_index = os.getenv('SEARCH_INDEX')
        self.index_client = SearchIndexClient(endpoint=self.search_endpoint, credential=AzureKeyCredential(self.key))
        self.search_client = SearchClient(endpoint=self.search_endpoint, index_name=self.search_index,credential=AzureKeyCredential(self.key))
        self.openai_key=os.getenv('AZURE_OPENAI_API_KEY')
        self.openai_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
        self.openai_api_version=os.getenv('OPENAI_API_VERSION')
        self.openai_embedding_model=os.getenv('OPENAI_EMBEDDING_MODEL')
        self.azure_openai_embedding_dimensions = int(os.getenv('AZURE_OPENAI_EMBEDDING_DIMENSIONS'))
        self.azureopenai_client = AzureOpenAI(
                                    api_key=os.getenv('AZURE_OPENAI_KEY'),  
                                    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
                                    api_version=os.getenv('OPENAI_API_VERSION')
                                    )
        
        try:
            # Check if the index exists
            self.index_client.get_index(self.search_index)
            
            # Check if there are records in the index
            result = self.search_client.search("*", top=1)
            records_exist = False
            for _ in result:
                records_exist = True
                break
                
            if records_exist:
                print(f"Records found in index {self.search_index}. Deleting all records...")
                self.delete_all_documents()
                
        except Exception as e:
            print(f"Index {self.search_index} does not exist. Creating index...")
            self.create_index()

    def create_index(self):
        
        fields = [
            SimpleField(name="chunk_id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
            SimpleField(name="parent_id", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
            SearchableField(name="url", type=SearchFieldDataType.String),
            SearchableField(name="chunk_title", type=SearchFieldDataType.String,filterable=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchableField(name="type", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="category", 
                            type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                            filterable=True,
                            analyzer_name="standard.lucene", 
                            facetable=True,collection=True),            
            SearchField(name="vectorized_content", 
                        type=SearchFieldDataType.Collection(SearchFieldDataType.Single), 
                        searchable=True,
                        vector_search_dimensions=self.azure_openai_embedding_dimensions,  
                        vector_search_profile_name="myHnswProfile",hidden=False), 
        
            
                ]
                    
        # Configure the vector search configuration  
        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="myHnsw"
                )
            ],
            profiles=[
                VectorSearchProfile(
                    name="myHnswProfile",
                    algorithm_configuration_name="myHnsw",
                    vectorizer_name="myVectorizer"
                )
            ],
        vectorizers=[
            AzureOpenAIVectorizer(
                vectorizer_name="myVectorizer",
                parameters=AzureOpenAIVectorizerParameters(
                    resource_url=self.openai_endpoint,  # Azure OpenAI endpoint URL
                    deployment_name=self.openai_embedding_model,
                    model_name=self.openai_embedding_model,
                    api_key=self.openai_key
                )
                
            )
        ]
        )        
        
        # Create the semantic configuration with the prioritized fields
        semantic_config = SemanticConfiguration(
            name="my-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="chunk_title"),
                keywords_fields=[SemanticField(field_name="category"),
                                 SemanticField(field_name="url")],
                content_fields=[SemanticField(field_name="content")]
            )
        )

        # Create the semantic settings with the configuration
        semantic_search = SemanticSearch(configurations=[semantic_config])

        # Create the search index with the semantic settings
        index = SearchIndex(name=self.search_index, fields=fields,
                            vector_search=vector_search, 
                            semantic_search=semantic_search)
        result = self.index_client.create_or_update_index(index)
        # wait for the index to be created
        time.sleep(10) 
        print(f"Created index: {result.name}")

    def write_to_index(self, webcontent: webContent) -> str:
        try:
            
            # Check if all required values are present in webcontent
            required_fields = ['url', 'content', 'type', 'category']
            for field in required_fields:
                if not getattr(webcontent, field, None):
                    raise ValueError(f"Missing required field: {field}")

            documents = []
            for key, content in webcontent.content.items():
                document = {
                    "chunk_id": str(hash(webcontent.url + key)),
                    "parent_id": str(hash(webcontent.url)),
                    "url": webcontent.url,
                    "chunk_title": key,
                    "content": content,
                    "type": webcontent.type,
                    "category": webcontent.category,
                    "vectorized_content": webcontent.content_embeddings[key]  # Add vectorized content
                }
                documents.append(document)
            
            self.search_client.upload_documents(documents=documents)
            print(f"Writing to index for {webcontent.url}")
        except Exception as e:
            print(f"An error occurred: {e}")
            
    def delete_all_documents(self):
        """
        Delete all documents from the index without deleting the index itself.
        Uses a wildcard query to find all documents and then issues a delete operation.
        """
        try:
            print(f"Retrieving all document keys from index {self.search_index}...")
            
            # Get all document keys from the index
            results = self.search_client.search("*", select="chunk_id", include_total_count=True)
            
            # Check if there are documents to delete
            total_count = results.get_count()
            if total_count == 0:
                print(f"No documents found in index {self.search_index}")
                return
                
            print(f"Found {total_count} documents to delete")
            
            # Collect all document keys
            doc_keys = []
            for result in results:
                doc_keys.append({"chunk_id": result["chunk_id"]})
            
            # Delete documents in batches
            batch_size = 1000
            for i in range(0, len(doc_keys), batch_size):
                batch = doc_keys[i:i+batch_size]
                actions = [{"@search.action": "delete", **key} for key in batch]
                
                # Upload actions to delete documents
                result = self.search_client.upload_documents(actions)
                print(f"Deleted batch of {len(batch)} documents. Succeeded: {result.succeeded_count}, Failed: {result.failed_count}")
            
            print(f"Successfully deleted all documents from index {self.search_index}")
            
        except Exception as e:
            print(f"Error deleting all documents: {e}")
            print("Attempting fallback method...")
            
            try:
                # Fallback approach if the standard delete operation fails
                print(f"Deleting index {self.search_index}...")
                self.index_client.delete_index(self.search_index)
                print(f"Index {self.search_index} deleted successfully.")
                
                # Wait a moment for the deletion to complete
                time.sleep(5)
                
                # Recreate the index
                print(f"Recreating index {self.search_index}...")
                self.create_index()
                print(f"All documents successfully removed from index {self.search_index}")
            except Exception as inner_e:
                print(f"Error using fallback method: {inner_e}")