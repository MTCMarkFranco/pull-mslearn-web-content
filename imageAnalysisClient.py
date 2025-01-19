import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient as AzureImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

class imageAnalysisClient:
    def __init__(self, endpoint, key):
        self.endpoint = endpoint
        self.key = key

    def describe_image(self, image_url: str) -> str:
               

        # Create an Image Analysis client
        client = AzureImageAnalysisClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
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
        return word_list