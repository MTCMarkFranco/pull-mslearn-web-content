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

## Setup

Create a `.env` file at the root of the project folder and add the following variables with their respective values:


- `IMAGE_ANALYSIS_API_KEY`: Your API key for the image analysis service.
- `IMAGE_ANALYSIS_ENDPOINT`: The endpoint URL for the image analysis service.
- `LLM_TOOL_API_KEY`: Your API key for the LLM tool.
- `LLM_TOOL_ENDPOINT`: The endpoint URL for the LLM tool.
- `VISION_KEY`: Your vision service API key.
- `VISION_ENDPOINT`: The endpoint URL for the vision service.
- `COMPLETIONS_MODEL`: The model name for completions.
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key.
- `AZURE_OPENAI_ENDPOINT`: The endpoint URL for Azure OpenAI.
- `OPENAI_API_VERSION`: The API version for OpenAI.
- `SEARCH_KEY`: Your search service API key.
- `SEARCH_ENDPOINT`: The endpoint URL for the search service.
- `SEARCH_INDEX`: The search index name.
- `OPENAI_EMBEDDING_MODEL`: The model name for OpenAI embeddings.
- `AZURE_OPENAI_EMBEDDING_DIMENSIONS`: The embedding dimensions for Azure OpenAI.
- `CHUNK_SIZE`: The chunk size for processing.

## Usage

```python
from content_service import ContentService

service = ContentService()

url = "https://example.com"
service.pull_content(url, recursive=True)
```

## TODO

1. Implement a conversion function from SVG to PNG.

