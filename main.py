import os
from fpdf import FPDF  # Add import for PDF library
from dotenv import load_dotenv
from linkScraper import *

# Load environment variables
load_dotenv()

vision_key = os.getenv('VISION_KEY')
vision_endpoint = os.getenv('VISION_ENDPOINT')


start_url = 'https://learn.microsoft.com/en-us/azure/architecture'
scraper = linkScraper(vision_endpoint, vision_key)
scraper.get_all_links(start_url)

# Generate PDFs from content list
for idx, content in enumerate(scraper.content_list):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    pdf.output(f"PDFs/content_{idx + 1}.pdf")

print(f'Total number of pages visited: {len(scraper.visited)}')
print(f'Total size of content list: {len(scraper.content_list)}')