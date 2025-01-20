import os
from fpdf import FPDF  # Add import for PDF library
from dotenv import load_dotenv
from linkScraper import *
from utilities import utilities
from writeToIndex import writeToIndex

# Load environment variables
load_dotenv()

vision_key = os.getenv('VISION_KEY')
vision_endpoint = os.getenv('VISION_ENDPOINT')

start_url = 'https://learn.microsoft.com/en-us/azure/architecture'
scraper = linkScraper(vision_endpoint, vision_key)

try:
    writeToIndex().create_index()
except Exception as e:
    if "already exists" in str(e):
        print("Index already exists. Continuing...")

scraper.get_all_links(start_url)

# for idx, content in enumerate(scraper.webContentList):
    
    # writeToIndex().write_to_index(content)

    # Generate PDFs from content list
    # for idx, content in enumerate(scraper.webContentList):
    #     try:
    #         pdf = FPDF()
    #         pdf.add_page()
    #         pdf.set_auto_page_break(auto=True, margin=15)
    #         pdf.add_font('ArialUnicode', '', 'ArialUnicodeMS.ttf', uni=True)
    #         pdf.set_font("ArialUnicode", size=12)
            
    #         # Add URL and Type to the first page
    #         pdf.multi_cell(0, 10, f"URL: {content.url}")
    #         pdf.multi_cell(0, 10, f"Type of Link: {content.Type}")
    #         pdf.multi_cell(0, 10, f"Category of Link: {content.category}")
                    
    #         pdf.multi_cell(0, 10, content.content)
    #         filename = os.path.join("PDFs", utilities.url_to_filename(content.url))
    #         pdf.output(filename)
    #         print(f"Created PDF :' {filename} '")
    #     except Exception as e:
    #         print(f"Failed to create PDF :' {filename} '")