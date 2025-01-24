import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from imageAnalysisService import imageAnalysisService
from models.webContent import webContent
from llmToolsService import llmToolsService
from indexService import indexService

class htmlContentService:
    def __init__(self,endpoint, key):
        self.visited = set()
        self.image_client = imageAnalysisService(endpoint=endpoint, key=key)
        self.llm_client = llmToolsService()
        self.index_service = indexService()

    def pull_content(self, url, recursive=False):
        
        currentWebContent = webContent()
        soup = BeautifulSoup("", 'html.parser')
        
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
            content = self.llm_client.get_image_detailed_decription_from_llm(keywords, url)
            currentWebContent.type = 'IMAGE'
        
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.get_text()
            currentWebContent.type = 'ARTICLE'
        
        # Set the url, content and category
        currentWebContent.url = url
        currentWebContent.content = content
        currentWebContent.category = llmToolsService().categorize_content(currentWebContent.content, currentWebContent.url, currentWebContent.type)
        
        # Write to index
        self.index_service.write_to_index(currentWebContent)
                
        # If recursive, find all links on the page and process them
        for link in soup.find_all('a', href=True, recursive=True):
            full_url = urljoin(url, link['href'])
            if (full_url not in self.visited and full_url.startswith('https://learn.microsoft.com/en-us/azure/architecture')) and recursive:
                print(f"Following Link: {full_url}")
                self.pull_content(full_url, True)