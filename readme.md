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
from htmlContentService import htmlContentService

endpoint = "your_image_analysis_endpoint"
key = "your_image_analysis_key"
service = htmlContentService(endpoint, key)

url = "https://example.com"
service.pull_content(url, recursive=True)
```

## TODO

1. Enable chunking of articles and images.
2. Implement a conversion function from SVG to PNG.
3. Add a column in the index for vectorized chunks.
4. Add code to enable an optimized chunking strategy with parent chunk relationships.
