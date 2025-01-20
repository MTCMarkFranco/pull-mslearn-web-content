import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient as AzureImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

from dotenv import load_dotenv

load_dotenv()

class deriveArticleCategory:
    def __init__(self):
        self.azureopenai_client = AzureOpenAI(
                                    api_key=os.getenv('AZURE_OPENAI_KEY'),  
                                    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
                                    api_version=os.getenv('OPENAI_API_VERSION')
                                    )

    def categorize_content(self, content: str, url: str, type: str) -> str:
            
            query = f"Categorize the content: {content} and url: {url} and type: {type}"

            systemprompt = f"""
            
            you are an expert at categorizing content. You will be given content and a url and you must return the categories of the content. The possible
            
            categories:

            Infrastructure
            Architecture
            Compliance
            Integration
            Networking
            Security
            Data
            Operation
            Backup
            Licenses
            Logging
            Exception Handling

            If the content does not fit any of these categories, return: MISC
            
            NOTE: The content can be a description of image or an article.

            IMPORTANT: ONly return the applicable categories or MISC, nothing else except the categories
            IMPORTA: Please return the categories in  JSON Format.
            """
            
            
            completion = self.azureopenai_client.chat.completions.create( 
                        model=os.getenv('COMPLETIONS_MODEL'),
                        max_tokens=1200,
                        temperature=0.4,
                        messages=[
                             {"role": "system", "content": systemprompt},
                             {"role": "user", "content": query }],
                        top_p=0.95,  
                        frequency_penalty=0,  
                        presence_penalty=0,
                        stop=None,  
                        stream=False  

                        )
            return completion.choices[0].message.content.strip(" \n")


