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
htmlContentService(vision_endpoint,vision_key).pull_content(start_url, True)

# Generate PDFs from content list
# for idx, content in enumerate(scraper.webContentList):
#     try:
#         pdf = FPDF()
#         pdf.add_page()
#         pdf.set_auto_page_break(auto=False, margin=15)
#         pdf.add_font('ArialUnicode', '', 'ArialUnicodeMS.ttf', uni=True)
#         pdf.set_font("ArialUnicode", size=12)
        
#         # Add URL and Type to the first page
#         pdf.multi_cell(0, 12, f"URL: {content.url}")
#         pdf.multi_cell(0, 12, f"Type of Link: {content.Type}")
#         pdf.ln(10)  # Add a line break
        
#         pdf.multi_cell(0, 12, content.content)
#         filename = os.path.join("PDFs", utilities.url_to_filename(content.url))
#         pdf.output(filename)
#         print(f"Created PDF :' {filename} '")
#     except Exception as e:
#         print(f"Failed to create PDF :' {filename} '")