from sentence_transformers import SentenceTransformer


from sentence_transformers import SentenceTransformer

class LocalEmbeddingService:
     def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
          self.model = SentenceTransformer(model_name)
     
     def generate_embedding(self, text: str) -> List[float]:
          embedding = self.model.encode(text)
          return embedding.tolist()
     
     def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
          embeddings = self.model.encode(texts)
          return embeddings.tolist()
     
     def create_product_text(self, product: Product) -> str:
          features_text = ", ".join(product.features) if product.features else ""
          variants_text = ", ".join(product.variants) if product.variants else ""
          
          text = f"""
          Product: {product.name}
          Category: {product.category}
          Description: {product.description}
          Features: {features_text}
          Variants: {variants_text}
          """.strip()
          
          return text
     