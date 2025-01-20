class webContent:
    def __init__(self, url: str = '', content: str = '', Type: str = 'ARTICLE'):
        if Type not in ['ARTICLE', 'IMAGE']:
            raise ValueError("Type must be either 'ARTICLE' or 'IMAGE'")
        self.url = url
        self.content = content
        self.Type = Type