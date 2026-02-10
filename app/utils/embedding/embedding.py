from sentence_transformers import SentenceTransformer


class LocalEmbeddingService:
     def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
          self.model = SentenceTransformer(model_name)

     async def generate_embedding(self, text: str) -> np.ndarray:
          return self.model.encode(text, convert_to_numpy=True)

     async def generate_weighted_search_vector(
          self, 
          query_text: str, 
          setup_text: str, 
     ) -> List[float]:
          """
          Combines query (70%), setup (30%) 
          into a single search embedding.
          """
          v_query = self.generate_embedding(query_text)
          v_setup = self.generate_embedding(setup_text)

          combined_vector = (0.70 * v_query) + (0.30 * v_setup) 
          norm = np.linalg.norm(combined_vector)
          if norm > 0:
               combined_vector = combined_vector / norm

          return combined_vector.tolist()
     
     async def create_product_text(self, product: Product) -> str:
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
     async def create_setup_text(self, setup: Setup) -> str:
          return f"""
          fitnessGoal: {setup.fitnessGoal}
          fitnessLevel: {setup.fitnessLevel}
          height: {setup.height}
          weight: {setup.weight}
          equipment: {setup.equipment}
          equipmentHave: {', '.join(setup.equipmentHave)}
          daysPerWeek: {setup.daysPerWeek}
          sessionLength: {setup.sessionLength}
          injuries: {setup.injuries}
          dietaryPreference: {', '.join(setup.dietaryPreference)}
          challenge: {', '.join(setup.challenge)}
          bloodType: {setup.bloodType}
          """.strip()
