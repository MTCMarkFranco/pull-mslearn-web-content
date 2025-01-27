import os
from fpdf import FPDF  # Add import for PDF library
from dotenv import load_dotenv
from htmlContentService import htmlContentService
from utilities import utilities

# Load environment variables
load_dotenv()

vision_key = os.getenv('VISION_KEY')
vision_endpoint = os.getenv('VISION_ENDPOINT')

start_url = 'https://learn.microsoft.com/en-us/azure/architecture'
scraper = htmlContentService(vision_endpoint, vision_key)

scraper.pull_content(start_url, True)

print("Content has been scraped and indexed!")