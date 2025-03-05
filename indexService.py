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
            self.index_client.get_index(self.search_index)
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