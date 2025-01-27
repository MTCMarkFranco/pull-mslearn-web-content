# Pull Web Content Service

This project is designed to pull content from web pages, analyze images, categorize content, and index the results. It supports recursive crawling of specific domains and processes both text and image content.

## Features

- Fetches and processes web content from specified URLs.
- Analyzes images using a computer vision service.
- Categorizes content using an LLM tool.
- Indexes the processed content for further use.
- Supports recursive crawling of links within a specified domain.

## Installation

1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Configure the necessary API keys and endpoints for the image analysis and LLM tools.

## Usage

```python
from content_service import ContentService

service = ContentService()

url = "https://example.com"
service.pull_content(url, recursive=True)
```

## TODO

1. Implement a conversion function from SVG to PNG.

