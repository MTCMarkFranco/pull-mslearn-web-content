from typing import List

class webContent:
    def __init__(self, url: str = '', content: str = '', type: str = 'ARTICLE',category: List[str] = ['MISC']):
        if type not in ['ARTICLE', 'IMAGE']:
            raise ValueError("Type must be either 'ARTICLE' or 'IMAGE'")
        self.url = url
        self.content = content
        self.type = type
        self.category = category