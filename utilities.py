import urllib.parse
import re
import io
import aspose.svg as svg
import aspose.pydrawing as drawing

class utilities:
        
    @staticmethod
    def url_to_filename(url):
        # Parse the URL to get the path
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        
        # Extract the filename from the path
        filename = path.split('/')[-1]
        
        # Sanitize the filename
        filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
        
        if not filename:
            filename = 'index'
            
        # add a unique identifier to the filename
        filename = f"{filename}_{hash(url)}"
                
        # Ensure the filename ends with .pdf
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        return filename
    
    @staticmethod
    def convert_svg_to_png(svg_path):
        document = svg.SVGDocument(svg_path)
        options = svg.rendering.image.ImageRenderingOptions()
        options.background_color = drawing.Color.transparent
        options.page_setup.sizing = svg.rendering.SizingType.FIT_CONTENT
                
        
        with io.BytesIO() as output_stream:
            device = svg.rendering.image.ImageDevice(options, output_stream)
            renderer = svg.rendering.SvgRenderer()
            renderer.render(device, document)
            output_stream.seek(0)
            return output_stream.read()