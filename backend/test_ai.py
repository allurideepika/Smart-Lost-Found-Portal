from services.ai_match import get_image_embedding

image_path = "uploads/test.jpg"

embedding = get_image_embedding(image_path)

print("Embedding Length:", len(embedding))
print("First 10 Values:")
print(embedding[:10])