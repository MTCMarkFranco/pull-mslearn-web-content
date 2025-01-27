import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from imageAnalysisService import imageAnalysisService
from models.webContent import webContent
from llmToolsService import llmToolsService
from indexService import indexService
import tiktoken

class htmlContentService:
    def __init__(self,endpoint, key):
        self.visited = set()
        self.image_client = imageAnalysisService(endpoint=endpoint, key=key)
        self.llm_client = llmToolsService()
        self.index_service = indexService()
        self.chunk_size = int(os.getenv('CHUNK_SIZE'))
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def pull_content(self, url, recursive=False):
        
        currentWebContent = webContent()
        soup = BeautifulSoup("", 'html.parser')
        content_chunks = {}
        vectorized_content_chunks = {}
        full_document_text = ""
            
        if url in self.visited:
            return
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return

        self.visited.add(url)
        print(f"Processing: {url}")
        
        # If we have an image just process the image using computer vision and
        # obviously no search for child links
               
        content_type = response.headers['Content-Type']

        if content_type.startswith("image/svg"): # not supported by service as of Jan 2025
            return
        elif any(ext in content_type for ext in ['jpeg', 'jpg', 'pdf', 'png', 'bmp', 'tiff']):
            keywords = self.image_client.describe_image(url)
            full_document_text = self.llm_client.get_image_detailed_decription_from_llm(keywords, url)
            content_chunks[url] = full_document_text # No chunking required here as we are controlling the llm response size window for image description
            currentWebContent.type = 'IMAGE'
        
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            currentWebContent.type = 'ARTICLE'
            full_document_text = soup.get_text()
            docSections = soup.select('h2[id]')
            
            # Iterate through the sections and collect content between them
            for i, section in enumerate(docSections):
                section_text = section.get_text()
                next_section = docSections[i + 1] if i + 1 < len(docSections) else None
                
                # Find the content between the current section and the next section
                if next_section:
                    section_content = ''.join(tag.get_text() for tag in section.find_all_next() if tag != next_section and tag.name != 'h2' and tag.find_previous('h2') == section)
                else:
                    section_content = ''.join(tag.get_text() for tag in section.find_all_next() if tag.name != 'h2' and tag.find_previous('h2') == section)    
                    
                tokens = self.tokenizer.encode(section_content)
                
                # Split the content into smaller chunks if it exceeds the chunk size in tokens
                if len(tokens) > self.chunk_size:
                    for j in range(0, len(tokens), self.chunk_size):
                        chunk_tokens = tokens[j:j + self.chunk_size]
                        chunk_text = self.tokenizer.decode(chunk_tokens)
                        chunk_key = f"{section_text} (part {j // self.chunk_size + 1})"
                        content_chunks[chunk_key] = chunk_text
                        vectorized_content_chunks[chunk_key] = self.llm_client.vectorize_chunk(chunk_text)
                else:
                    content_chunks[section_text] = section_content
                    vectorized_content_chunks[section_text] = self.llm_client.vectorize_chunk(section_content)
           
        # Set the url, content chunks, category, and content embeddings
        currentWebContent.url = url
        currentWebContent.content = content_chunks
        currentWebContent.category = llmToolsService().categorize_content(full_document_text, currentWebContent.url, currentWebContent.type)
        currentWebContent.content_embeddings = vectorized_content_chunks
        
        # Write to index
        self.index_service.write_to_index(currentWebContent)
                
        # If recursive, find all links on the page and process them
        for link in soup.find_all('a', href=True, recursive=True):
            full_url = urljoin(url, link['href'])
            if (full_url not in self.visited and full_url.startswith('https://learn.microsoft.com/en-us/azure/architecture')) and recursive:
                print(f"Following Link: {full_url}")
                self.pull_content(full_url, True)