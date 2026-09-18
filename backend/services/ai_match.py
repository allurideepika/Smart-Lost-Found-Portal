from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np

model = SentenceTransformer("clip-ViT-B-32")

def get_image_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    embedding = model.encode(image)
    return embedding

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    similarity = np.dot(vec1, vec2) / (
        np.linalg.norm(vec1) * np.linalg.norm(vec2)
    )

    return float(similarity)