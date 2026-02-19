# app/Services/products/products_service.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any, Tuple
from bson import ObjectId
from app.config.settings import settings
from app.Services.products.products_schema import Product
from app.utils.embedding.embedding import LocalEmbeddingService
import asyncio
from datetime import datetime, timedelta

class ProductService:
     def __init__(self):
          self.client = AsyncIOMotorClient(settings.DATABASE_URL)
          self.db = self.client[settings.DATABASE_NAME]
          self.products_collection = self.db["products"]
          self.users_collection = self.db["users"]
          self.interactions_collection = self.db["interactions"]  # For tracking
          self.embedding_service = LocalEmbeddingService()
     
     async def create_product_with_embedding(self, product_data: dict) -> Product:
          """Create a product and generate its embedding"""
          product = Product(**product_data)
          
          product_text = await self.embedding_service.create_product_text(product)
          embedding = await self.embedding_service.generate_embedding(product_text)
          product.embedding = embedding.tolist()  # Convert numpy to list
          
          result = await self.products_collection.insert_one(
               product.model_dump(by_alias=True, exclude={"id"})
          )
          product.id = result.inserted_id
          
          return product
     
     async def update_product_with_embedding(self, product_id: str, product_data: dict) -> bool:
          """Update embedding for an existing product"""
          product_exists = await self.products_collection.find_one({"_id": ObjectId(product_id)})
          if not product_exists:
               return False
          
          # Merge with existing data
          updated_data = {**product_exists, **product_data}
          product = Product(**updated_data)
          
          product_text = await self.embedding_service.create_product_text(product)
          embedding = await self.embedding_service.generate_embedding(product_text)
          
          await self.products_collection.update_one(
               {"_id": ObjectId(product_id)},
               {"$set": {
                    **product_data,
                    "embedding": embedding.tolist(),
                    "updated_at": datetime.utcnow()
               }}
          )
          return True
     
     async def get_personal_setup(self, userId: str) -> Dict:
          """Get user's personal setup/preferences"""
          user = await self.users_collection.find_one({"_id": ObjectId(userId)})
          
          if not user:
               return self._get_default_setup()
          
          return user.get('setup', self._get_default_setup())
     
     def _get_default_setup(self) -> Dict:
          """Default setup for users without preferences"""
          return {
               'fitnessGoal': 'general_fitness',
               'fitnessLevel': 'intermediate',
               'equipment': 'some',
               'equipmentHave': [],
               'daysPerWeek': 3,
               'sessionLength': '30-45 min',
               'dietaryPreference': [],
               'challenge': [],
               'injuries': 'none'
          }
     
     async def search_by_text_query(
          self,
          userId: str,
          query: str,
          limit: int = 10,
          filters: Optional[Dict[str, Any]] = None,
          use_personalization: bool = True,
          min_score: float = 0.3
     ) -> List[Dict]:
          """
          OPTIMIZED: Enhanced search with multiple strategies
          
          Combines:
          1. Semantic vector search
          2. User personalization
          3. Popularity signals
          4. Hybrid re-ranking
          """
          
          # Get user preferences
          personal_setup = await self.get_personal_setup(userId)
          
          # Strategy 1: Main personalized search
          main_results = await self._personalized_vector_search(
               query=query,
               setup=personal_setup,
               limit=limit * 2,  # Fetch more for re-ranking
               filters=filters,
               min_score=min_score,
               use_personalization=use_personalization
          )
          
          # Strategy 2: Get user's interaction history for personalization boost
          user_history = await self._get_user_history(userId)
          
          # Strategy 3: Hybrid re-ranking
          reranked_results = await self._hybrid_rerank(
               results=main_results,
               query=query,
               setup=personal_setup,
               user_history=user_history,
               limit=limit
          )
          
          # Log search for analytics
          await self._log_search(userId, query, len(reranked_results))
          
          return reranked_results
     
     async def _personalized_vector_search(
          self,
          query: str,
          setup: Dict,
          limit: int,
          filters: Optional[Dict[str, Any]],
          min_score: float,
          use_personalization: bool
     ) -> List[Dict]:
          """Core vector search with personalization"""
          
          # Generate search embedding
          if use_personalization and setup:
               setup_text = await self.embedding_service.create_setup_text(setup)
               query_embedding = await self.embedding_service.generate_weighted_search_vector(
                    query_text=query,
                    setup_text=setup_text
               )
          else:
               # Pure query search without personalization
               query_embedding = await self.embedding_service.generate_embedding(query)
               query_embedding = query_embedding.tolist()
          
          return await self.vector_search_products(
               query_embedding=query_embedding,
               limit=limit,
               filters=filters,
               min_score=min_score
          )
     
     async def _get_user_history(self, userId: str, days: int = 90) -> Dict:
          """Get user's interaction history for personalization"""
          cutoff_date = datetime.utcnow() - timedelta(days=days)
          
          interactions = await self.interactions_collection.find({
               "userId": userId,
               "timestamp": {"$gte": cutoff_date}
          }).to_list(None)
          
          # Aggregate by category and products
          history = {
               'viewed_products': set(),
               'purchased_products': set(),
               'favorite_categories': {},
               'price_range': {'min': 0, 'max': float('inf')}
          }
          
          for interaction in interactions:
               if interaction.get('interaction_type') == 'view':
                    history['viewed_products'].add(str(interaction['product_id']))
               elif interaction.get('interaction_type') == 'purchase':
                    history['purchased_products'].add(str(interaction['product_id']))
                    
                    # Track category preferences
                    category = interaction.get('category', 'unknown')
                    history['favorite_categories'][category] = \
                         history['favorite_categories'].get(category, 0) + 1
          
          return history
     
     async def _hybrid_rerank(
          self,
          results: List[Dict],
          query: str,
          setup: Dict,
          user_history: Dict,
          limit: int
     ) -> List[Dict]:
          """
          Re-rank results using hybrid signals:
          1. Vector similarity score (from initial search)
          2. Popularity score (rating, reviews)
          3. Personalization score (category preference, price fit)
          4. Freshness score (new products)
          5. Diversity (avoid too similar products)
          """
          
          for result in results:
               # Start with vector similarity score
               vector_score = result.get('score', 0.5)
               
               # Popularity score (0-1)
               popularity_score = self._calculate_popularity_score(result)
               
               # Personalization score (0-1)
               personalization_score = self._calculate_personalization_score(
                    result, setup, user_history
               )
               
               # Freshness score (0-1)
               freshness_score = self._calculate_freshness_score(result)
               
               # Combined score with weights
               final_score = (
                    0.50 * vector_score +        # Semantic relevance (most important)
                    0.20 * popularity_score +    # Social proof
                    0.20 * personalization_score +  # User fit
                    0.10 * freshness_score       # Novelty
               )
               
               result['final_score'] = final_score
               result['score_breakdown'] = {
                    'vector': vector_score,
                    'popularity': popularity_score,
                    'personalization': personalization_score,
                    'freshness': freshness_score
               }
          
          # Sort by final score
          results.sort(key=lambda x: x['final_score'], reverse=True)
          
          # Apply diversity filter to avoid too many similar products
          diverse_results = self._apply_diversity_filter(results, limit)
          
          return diverse_results
     
     def _calculate_popularity_score(self, product: Dict) -> float:
          """Calculate popularity score from ratings and reviews"""
          rating = product.get('averageRating', 0)
          review_count = product.get('totalReview', 0)
          
          # Normalize rating (0-5 -> 0-1)
          rating_score = rating / 5.0 if rating else 0.5
          
          # Review count score with logarithmic scaling
          # More reviews = more reliable, but diminishing returns
          review_score = min(np.log1p(review_count) / np.log1p(100), 1.0)
          
          # Weighted combination
          return 0.7 * rating_score + 0.3 * review_score
     
     def _calculate_personalization_score(
          self,
          product: Dict,
          setup: Dict,
          user_history: Dict
     ) -> float:
          """Calculate how well product fits user preferences"""
          score = 0.5  # Base score
          
          # Category preference boost
          category = product.get('category', '')
          if category in user_history.get('favorite_categories', {}):
               category_freq = user_history['favorite_categories'][category]
               score += min(category_freq * 0.1, 0.3)  # Up to +0.3
          
          # Avoid recently purchased products (reduce score)
          product_id = str(product.get('_id', ''))
          if product_id in user_history.get('purchased_products', set()):
               score -= 0.4  # Significant penalty
          
          # Price fit (user's typical price range)
          # This would require analyzing user's purchase history
          # Simplified for now
          
          # Fitness level match (example for fitness products)
          if 'tags' in product and setup.get('fitnessLevel'):
               if setup['fitnessLevel'] in product.get('tags', []):
                    score += 0.2
          
          return max(0.0, min(1.0, score))  # Clamp to [0, 1]
     
     def _calculate_freshness_score(self, product: Dict) -> float:
          """Boost newer products slightly"""
          created_at = product.get('created_at')
          if not created_at:
               return 0.5
          
          # Products created in last 30 days get boost
          if isinstance(created_at, str):
               created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
          
          days_old = (datetime.utcnow() - created_at).days
          
          if days_old < 7:
               return 1.0  # Very new
          elif days_old < 30:
               return 0.8  # Recent
          elif days_old < 90:
               return 0.6  # Moderately new
          else:
               return 0.4  # Older
     
     def _apply_diversity_filter(
          self,
          results: List[Dict],
          limit: int,
          min_category_gap: int = 2
     ) -> List[Dict]:
          """
          Ensure diversity in results - don't show too many similar products
          """
          if len(results) <= limit:
               return results
          
          diverse_results = []
          category_counts = {}
          last_category = None
          consecutive_same = 0
          
          for result in results:
               category = result.get('category', 'unknown')
               
               # Track consecutive products from same category
               if category == last_category:
                    consecutive_same += 1
               else:
                    consecutive_same = 0
                    last_category = category
               
               # Skip if too many consecutive from same category
               if consecutive_same >= min_category_gap:
                    continue
               
               # Skip if category is over-represented
               category_count = category_counts.get(category, 0)
               max_per_category = max(2, limit // 3)  # At most 1/3 from one category
               
               if category_count >= max_per_category:
                    continue
               
               diverse_results.append(result)
               category_counts[category] = category_count + 1
               
               if len(diverse_results) >= limit:
                    break
          
          # If we didn't get enough, fill with remaining results
          if len(diverse_results) < limit:
               for result in results:
                    if result not in diverse_results:
                         diverse_results.append(result)
                         if len(diverse_results) >= limit:
                              break
          
          return diverse_results[:limit]
     
     async def vector_search_products(
          self,
          query_embedding: List[float],
          limit: int = 10,
          filters: Optional[Dict[str, Any]] = None,
          min_score: float = 0.3
     ) -> List[Dict]:
          """Core vector search (your existing implementation)"""
          
          pipeline = [
               {
                    "$vectorSearch": {
                         "index": "product_vector_index",
                         "path": "embedding",
                         "queryVector": query_embedding,
                         "numCandidates": limit * 10,
                         "limit": limit
                    }
               },
               {
                    "$addFields": {
                         "score": {"$meta": "vectorSearchScore"}
                    }
               }
          ]
          
          # Apply filters
          if filters:
               match_conditions = {}
               
               if "category" in filters:
                    match_conditions["category"] = filters["category"]
               
               if "status" in filters:
                    match_conditions["status"] = filters["status"]
               else:
                    match_conditions["status"] = "ACTIVE"
               
               if "price_range" in filters:
                    match_conditions["price"] = {
                         "$gte": filters["price_range"].get("min", 0),
                         "$lte": filters["price_range"].get("max", float('inf'))
                    }
               
               if "min_rating" in filters:
                    match_conditions["averageRating"] = {"$gte": filters["min_rating"]}
               
               if match_conditions:
                    pipeline.append({"$match": match_conditions})
          
          # Min score filter
          pipeline.append({
               "$match": {
                    "score": {"$gte": min_score}
               }
          })
          
          # Project fields
          pipeline.append({
               "$project": {
                    "_id": 1,
                    "name": 1,
                    "category": 1,
                    "description": 1,
                    "price": 1,
                    "discount": 1,
                    "averageRating": 1,
                    "totalReview": 1,
                    "features": 1,
                    "tags": 1,
                    "created_at": 1,
                    "score": 1
               }
          })
          
          results = await self.products_collection.aggregate(pipeline).to_list(None)
          return results
     
     async def get_similar_products(
          self,
          product_id: str,
          limit: int = 5,
          exclude_same_exact: bool = True
     ) -> List[Dict]:
          """Find similar products based on a given product"""
          
          product_data = await self.products_collection.find_one({"_id": ObjectId(product_id)})
          if not product_data or not product_data.get("embedding"):
               return []
          
          results = await self.vector_search_products(
               query_embedding=product_data["embedding"],
               limit=limit + 1,
               min_score=0.5  # Higher threshold for similarity
          )
          
          # Exclude the source product
          filtered = [r for r in results if str(r["_id"]) != product_id]
          
          return filtered[:limit]
     
     async def _log_search(self, userId: str, query: str, result_count: int):
          """Log search for analytics and improvement"""
          await self.interactions_collection.insert_one({
               "userId": userId,
               "interaction_type": "search",
               "query": query,
               "result_count": result_count,
               "timestamp": datetime.utcnow()
          })
     
     async def log_product_interaction(
          self,
          userId: str,
          product_id: str,
          interaction_type: str,  # 'view', 'click', 'purchase', 'add_to_cart'
          metadata: Optional[Dict] = None
     ):
          """Log user-product interactions for future model training"""
          
          product = await self.products_collection.find_one({"_id": ObjectId(product_id)})
          
          interaction = {
               "userId": userId,
               "product_id": product_id,
               "interaction_type": interaction_type,
               "category": product.get('category') if product else None,
               "timestamp": datetime.utcnow(),
               "implicit_score": {
                    'purchase': 1.0,
                    'add_to_cart': 0.8,
                    'click': 0.5,
                    'view': 0.3
               }.get(interaction_type, 0.5)
          }
          
          if metadata:
               interaction['metadata'] = metadata
          
          await self.interactions_collection.insert_one(interaction)
     
     # Keep your existing methods
     async def get_product_by_id(self, product_id: str) -> Optional[Product]:
          """Get a product by its ID"""
          product_data = await self.products_collection.find_one({"_id": ObjectId(product_id)})
          if not product_data:
               return None
          return Product(**product_data)
     
     async def delete_product(self, product_id: str) -> bool:
          """Delete a product"""
          result = await self.products_collection.delete_one({"_id": ObjectId(product_id)})
          return result.deleted_count > 0