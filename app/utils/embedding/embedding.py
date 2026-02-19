from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Optional, Tuple
import hashlib
from functools import lru_cache
import torch
import asyncio

class LocalEmbeddingService:
     def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
          self.model = SentenceTransformer(model_name)
          if torch.cuda.is_available():
               self.model = self.model.to('cuda')
          self._setup_cache = {}
          self._cache_size_limit = 1000
     async def generate_embedding(self, text: str) -> np.ndarray:
          """Generate embedding for a single text"""
          # Run in thread pool to avoid blocking
          embedding = await asyncio.to_thread(
               self.model.encode,
               text,
               convert_to_numpy=True,
               normalize_embeddings=True  # L2 normalize by default
          )
          return embedding

     async def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
          """Generate embeddings for multiple texts efficiently"""
          embeddings = await asyncio.to_thread(
               self.model.encode,
               texts,
               convert_to_numpy=True,
               normalize_embeddings=True,
               batch_size=32
          )
          return embeddings

     def _get_setup_cache_key(self, setup: Dict) -> str:
          """Generate cache key from setup dict"""
          setup_str = str(sorted(setup.items()))
          return hashlib.md5(setup_str.encode()).hexdigest()

     async def generate_weighted_search_vector(
          self, 
          query_text: str, 
          setup_text: str,
          query_weight: float = 0.7,
          setup_weight: float = 0.3,
          use_cache: bool = True
) -> List[float]:
          """
          IMPROVED: Better combination strategy with caching
          
          Combines query and setup embeddings with proper normalization.
          Now uses concatenation + embedding for better semantic alignment.
          """
          
          # Strategy 1: Concatenate and embed (RECOMMENDED)
          # This allows the model to see both contexts together
          combined_text = self._create_combined_context(query_text, setup_text)
          combined_embedding = await self.generate_embedding(combined_text)
          
          return combined_embedding.tolist()
     async def generate_weighted_search_vector_separate(
          self,
          query_text: str,
          setup_text: str,
          query_weight: float = 0.7,
          setup_weight: float = 0.3,
          use_cache: bool = True
     ) -> List[float]:
               """
               Alternative: Separate embeddings with weighted combination
               Use this if concatenation makes queries too long
               """
               
               # Generate query embedding
               v_query = await self.generate_embedding(query_text)
               
               # Check cache for setup embedding
               setup_cache_key = None
               if use_cache:
                    setup_cache_key = self._get_setup_cache_key({"text": setup_text})
                    if setup_cache_key in self._setup_cache:
                         v_setup = self._setup_cache[setup_cache_key]
                    else:
                         v_setup = await self.generate_embedding(setup_text)
                         self._cache_setup_embedding(setup_cache_key, v_setup)
               else:
                    v_setup = await self.generate_embedding(setup_text)
               
               # Weighted combination with proper normalization
               combined_vector = (query_weight * v_query) + (setup_weight * v_setup)
               
               # L2 normalize the result
               norm = np.linalg.norm(combined_vector)
               if norm > 0:
                    combined_vector = combined_vector / norm
               
               return combined_vector.tolist()
          
     def _create_combined_context(self, query: str, setup: str) -> str:
          """
          Create a unified context that helps the model understand both
          the query and user preferences together
          """
          return f"""User searching for: {query}

     User preferences and context:
     {setup}

     Find products matching the search query that align with user preferences."""
     
     def _cache_setup_embedding(self, cache_key: str, embedding: np.ndarray):
          """Cache user setup embedding with LRU eviction"""
          if len(self._setup_cache) >= self._cache_size_limit:
               self._setup_cache.pop(next(iter(self._setup_cache)))
          self._setup_cache[cache_key] = embedding

     async def create_product_text(self, product) -> str:
          """Enhanced product text with better structure"""
          features_text = ", ".join(product.features) if product.features else "None"
          variants_text = ", ".join(product.variants) if product.variants else "None"
          
          # More structured format for better embeddings
          text = f"""Product: {product.name}
     Category: {product.category}
     Description: {product.description}
     Key Features: {features_text}
     Available Options: {variants_text}
     Price Range: ${product.price}"""
          
          if hasattr(product, 'averageRating') and product.averageRating:
               text += f"\nRating: {product.averageRating}/5 ({product.totalReview} reviews)"
          
          return text.strip()
     
     async def create_setup_text(self, setup: Dict) -> str:
          """Enhanced setup text with better structure"""
          
          # Build contextual description
          parts = []
          if setup.get('fitnessGoal'):
               parts.append(f"Goal: {setup['fitnessGoal']}")
          if setup.get('fitnessLevel'):
               parts.append(f"Experience: {setup['fitnessLevel']}")
          if setup.get('equipment'):
               equipment_have = ', '.join(setup.get('equipmentHave', []))
               parts.append(f"Equipment access: {equipment_have or 'none'}")
          if setup.get('daysPerWeek'):
               parts.append(f"Training frequency: {setup['daysPerWeek']} days/week")
          if setup.get('sessionLength'):
               parts.append(f"Session duration: {setup['sessionLength']}")
          if setup.get('dietaryPreference'):
               diet = ', '.join(setup['dietaryPreference'])
               parts.append(f"Diet: {diet}")
          if setup.get('challenge'):
               challenges = ', '.join(setup['challenge'])
               parts.append(f"Focus areas: {challenges}")
          if setup.get('injuries'):
               parts.append(f"Considerations: {setup['injuries']}")
          return "; ".join(parts)
     async def expand_query(self, query: str, setup: Dict) -> List[str]:
          """
          Generate query variations based on user context
          This helps find more relevant products
          """
          expanded_queries = [query]  # Original query
          # Add context-aware variations
          if setup.get('fitnessGoal') == 'muscle_gain':
               expanded_queries.append(f"{query} for muscle building")
               expanded_queries.append(f"{query} strength training")
          elif setup.get('fitnessGoal') == 'weight_loss':
               expanded_queries.append(f"{query} for fat loss")
               expanded_queries.append(f"{query} cardio")
          if setup.get('fitnessLevel') == 'beginner':
               expanded_queries.append(f"{query} beginner friendly")
          # Add equipment context
          equipment = setup.get('equipmentHave', [])
          if 'dumbbells' in equipment:
               expanded_queries.append(f"{query} with dumbbells")
          
          return expanded_queries[:3]  # Limit to top 3 variations