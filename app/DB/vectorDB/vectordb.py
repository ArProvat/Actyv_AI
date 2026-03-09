from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from app.utils.embedding.embedding import LocalEmbeddingService

class VectorDB:
     def __init__(self):
          self.client = AsyncQdrantClient(host="localhost", port=6333)
          self.collection_name = "Actyv_products"
          
          self.model = LocalEmbeddingService()
          self.vector_size = 768 

     async def create_collection(self):
          await self.client.create_collection(
               collection_name=self.collection_name,
               vectors_config=models.VectorParams(
                    size=self.vector_size, 
                    distance=models.Distance.COSINE
               )
          )

     async def add_product(self, descriptions:str,id:str ):
          # Generate embeddings for all descriptions at once (more efficient)
          try:
               try:
                    embeddings = self.model.generate_embedding(descriptions)
               except Exception as e:
                    raise HTTPException(status_code=500,detail=str(e))

               points = [
                    models.PointStruct(
                         id=id,
                         vector=embeddings,
                         payload={"id":id}
                    )
          ]

               await self.client.upsert(
                    collection_name=self.collection_name,
                    points=points,
               )
          except Exception as e:
               raise HTTPException(status_code=500,detail=str(e))
     

     async def search_product(self, query: str, limit: int = 10):
          query_vector = self.model.generate_embedding(query)

          results = await self.client.search(
               collection_name=self.collection_name,
               query_vector=query_vector,
               limit=limit,
          )
          return [result.payload["id"] for result in results]

     async def delete_product(self, product_id):
          await self.client.delete(
               collection_name=self.collection_name,
               points_selector=models.PointIdsList(
                    points=[product_id],
               ),
          )