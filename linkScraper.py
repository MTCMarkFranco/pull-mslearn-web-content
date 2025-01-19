import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from imageAnalysisClient  import *

class linkScraper:
    def __init__(self,endpoint, key):
        self.visited = set()
        self.content_list = []
        self.image_client = imageAnalysisClient(endpoint=endpoint, key=key)
     

    def get_all_links(self, url):
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
        
        if any(ext in response.headers['Content-Type'] for ext in ['jpeg', 'jpg', 'pdf', 'png', 'bmp', 'tiff']):
            image_description = self.image_client.describe_image(url) 
            self.content_list.append(image_description)
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            self.content_list.append(soup.get_text())

            for link in soup.find_all('a', href=True, recursive=True):
                full_url = urljoin(url, link['href'])
                if full_url not in self.visited and full_url.startswith('https://learn.microsoft.com/en-us/azure/architecture'):
                    print(full_url)
                    self.get_all_links(full_url)