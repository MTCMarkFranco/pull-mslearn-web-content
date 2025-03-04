import os
from fpdf import FPDF  # Add import for PDF library
from dotenv import load_dotenv
from htmlContentService import htmlContentService
from utilities import utilities

# Load environment variables
load_dotenv()

# Begin Program
start_url = 'https://learn.microsoft.com/en-us/azure/architecture/'

scraper = htmlContentService()

scraper.pull_content(start_url, True)

print("Content has been scraped and indexed!")