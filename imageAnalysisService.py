import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient as AzureImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

class imageAnalysisService:
    def __init__(self, ):
        self.vision_key = os.getenv('VISION_KEY')
        self.vision_endpoint = os.getenv('VISION_ENDPOINT')
    
    def describe_image(self, image_url: str) -> str:
               

        # Create an Image Analysis client
        client = AzureImageAnalysisClient(
            endpoint=self.vision_endpoint,
            credential=AzureKeyCredential(self.vision_key)
        )

        # Get a caption for the image. This will be a synchronously (blocking) call.
        result = client.analyze_from_url(
            image_url=image_url,
            visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ],
            gender_neutral_caption=True,  # Optional (default is False)
        )

        # Extract words from OCR results and create a comma-separated list
        words = []
        if result.read is not None:
            for block in result.read.blocks:
                for line in block.lines:
                    for word in line.words:
                        words.append(word.text)

        word_list = ", ".join(words)
        print(f"Converted image from url to text: {image_url}")
        return word_list

    def describe_image_from_stream(self, original_svg_url, image_stream: str) -> str:
               

        # Create an Image Analysis client
        client = AzureImageAnalysisClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
        )

        # Get a caption for the image. This will be a synchronously (blocking) call.
        result = client._analyze_from_image_data(
            image_data=image_stream,
            visual_features=[VisualFeatures.DENSE_CAPTIONS,
                             VisualFeatures.READ,
                             VisualFeatures.OBJECTS,
                             VisualFeatures.TAGS],
                             
            gender_neutral_caption=True,  # Optional (default is False)
        )

        # Extract words from OCR results and create a comma-separated list
        words = []
        if result.read is not None:
            for block in result.read.blocks:
                for line in block.lines:
                    for word in line.words:
                        words.append(word.text)

        word_list = ", ".join(words)
        print(f"Converted SVG image from url to text: {original_svg_url}")
        return word_list
        
    