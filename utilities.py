import urllib.parse
import re

class utilities:
        
    @staticmethod
    def url_to_filename(url):
        # Parse the URL to get the path
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        
        # Extract the filename from the path
        filename = path.split('/')[-1]
        
        # Sanitize the filename
        filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
        
        if not filename:
            filename = 'index'
            
        # add a unique identifier to the filename
        filename = f"{filename}_{hash(url)}"
                
        # Ensure the filename ends with .pdf
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        return filename