import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from imageAnalysisClient import imageAnalysisClient
from utilities import utilities
from models.webContent import webContent
from deriveArticleCategory import deriveArticleCategory
from writeToIndex import writeToIndex

class linkScraper:
    def __init__(self,endpoint, key):
        self.visited = set()
        #self.webContentList = []
        self.image_client = imageAnalysisClient(endpoint=endpoint, key=key)
     

    def get_all_links(self, url):
        
        currentWebContent = webContent()
        
        if url in self.visited:
            return
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return

        self.visited.add(url)
        print(url)
        
        # If we have an image just process the image using computer vision and
        # obviously no search for child links
        currentWebContent.url = url
        
        # convert SVG to Jpeg (Microsoft architecture articles are riddled with SVGs)
        content_type = response.headers['Content-Type']

        if content_type.startswith("image/svg"):
            return
        elif any(ext in content_type for ext in ['jpeg', 'jpg', 'pdf', 'png', 'bmp', 'tiff']):
            image_description = self.image_client.describe_image(url)
            currentWebContent.content = image_description
            currentWebContent.Type = 'IMAGE'
            currentWebContent.category = deriveArticleCategory().categorize_content(currentWebContent.content, currentWebContent.url, currentWebContent.Type)
            
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            currentWebContent.content = soup.get_text()
            currentWebContent.Type = 'ARTICLE'
            currentWebContent.category = deriveArticleCategory().categorize_content(currentWebContent.content, currentWebContent.url, currentWebContent.Type)

            # for link in soup.find_all('a', href=True, recursive=True):
            #     full_url = urljoin(url, link['href'])
            #     if full_url not in self.visited and full_url.startswith('https://learn.microsoft.com/en-us/azure/architecture'):
            #         print(full_url)
            #         self.get_all_links(full_url)
        
        writeToIndex().write_to_index(currentWebContent)
        #self.webContentList.append(currentWebContent)