import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient as AzureImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI, completions
from typing import List
import json
from models import categories

class llmToolsService:
    def __init__(self):
        self.azureopenai_client = AzureOpenAI(
                                    api_key=os.getenv('AZURE_OPENAI_KEY'),  
                                    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
                                    api_version=os.getenv('OPENAI_API_VERSION')
                                    )
        self.completions_model = os.getenv('COMPLETIONS_MODEL')
        self.embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL')
        self.azure_openai_embedding_dimensions = int(os.getenv('AZURE_OPENAI_EMBEDDING_DIMENSIONS'))

    def categorize_content(self, content: str, url: str, type: str) -> categories:
        try:    
            query = f"Categorize the content: {content} and url: {url} and type: {type}"

            systemprompt = f"""
            
            you are an expert at categorizing content. You will be given content and a url and you must return the most relevant categories of the content. 
            
            If the content does not fit any of these categories, return: ['MISC']
                        
            The content can be a description of image or an article.

            IMPORTANT: Only return relevant categories or ['MISC'], nothing else except the category in the form of a Json Array of Strings
            IMPORTANT: When identifying categories, try to suggest as few categories as possible, keeping the relevancy high.
            
            Select only from the categories below. they are as follows:

            Infrastructure
            Architecture
            Security
            Networking
            Compliance
            Integration
            Data
            Operation
            Backup
            Licenses
            Logging
            Exception Handling
            AI and Machine Learning
            Analytics
            Compute
            Containers
            Developer Tools
            DevOps
            Hybrid Cloud
            Identity
            IoT
            Messaging
            Monitoring
            Storage
            Web
            Migration
            Virtual Desktop Infrastructure
            Resiliency
            Disaster Recovery
            Scaling
            Performance
            """
                        
            completion = self.azureopenai_client.chat.completions.create( 
                        model=self.completions_model,
                        max_tokens=1200,
                        temperature=0.4,
                        messages=[
                             {"role": "system", "content": systemprompt},
                             {"role": "user", "content": query }],
                        top_p=0.95,  
                        frequency_penalty=0,  
                        presence_penalty=0,
                        stop=None,  
                        stream=False,
                        response_format= { "type": "json_object"}
                        )
            
            
            # Assuming completion.choices[0].message.content contains the JSON string
            json_string = completion.choices[0].message.content

            data = json.loads(json_string)
            categories_obj=data["categories"]
                                        
            return categories_obj
        except Exception as e:
            print(f"An error occurred: {e}")
            return ["MISC"]


    def get_image_detailed_decription_from_llm(self, keywords: str, imageUrl: str) -> str:
        try:    
            query = f"analyze the attached image and use the following keywords to help you perform your functions: {keywords}"

            systemprompt = f"""
                        You are an image processor. Your task is to analyze an image and provide a detailed description based on given keywords. 
                        For general images, describe what the image depicts in natural language, incorporating the provided keywords. 
                        If the image is an architecture diagram, explain the flows between components and identify the architecture pattern being conveyed.
            """
                        # As a second step, generate compliant Mermaid script markdown to recreate the diagram. Do not use parentheses to denote comments or 
                        # aliases, as this symbol is dedicated to a Mermaid script character. 
                        # Additionally, avoid using parentheses in labels within the Mermaid script to ensure compliance.
            
                        
            completion = self.azureopenai_client.chat.completions.create( 
                        model=self.completions_model,
                        max_tokens=800,
                        temperature=0.7,
                        messages=[
                            {"role": "system", "content": systemprompt},
                            {"role": "user", "content": 
                                [
                                   {
                                    "type": "text",
                                    "text":  query
                                   },
                                   {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"{imageUrl}"
                                    }
                                }
                                ] }],
                        top_p=0.95,  
                        frequency_penalty=0,  
                        presence_penalty=0,
                        stop=None,  
                        stream=False,
                        response_format= { "type": "text"}
                        )
            
            
            # Assuming completion.choices[0].message.content contains the JSON string
            return completion.choices[0].message.content

        except Exception as e:
            print(f"An error occurred: {e}")
            return f"Error Processing Image: {imageUrl}"
            
    def vectorize_chunk(self, chunk: str) -> List[float]:
        try:
            response = self.azureopenai_client.embeddings.create(
                input=chunk,
                model=self.embedding_model,
                dimensions=self.azure_openai_embedding_dimensions,
                encoding_format="float"
            )
            
            embedding = response.data[0].embedding
            return embedding
        except Exception as e:
            print(f"An error occurred during vectorization: {e}")
            return []

