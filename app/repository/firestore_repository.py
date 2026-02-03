from google.cloud.firestore import AsyncClient
from typing import Optional, Any

class FirestoreRepository:
    def __init__(self, db: AsyncClient):
        self.db = db

    async def find_by_id(self, collection: str, doc_id: str) -> Optional[dict]:
        """Comando centralizado para buscar por ID (chave primária)"""
        doc = await self.db.collection(collection).document(doc_id).get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            return data
        return None

    async def find_one_by_field(self, collection: str, field: str, value: Any) -> Optional[dict]:
        """Comando centralizado para buscar um registro por campo específico (ex: email)"""
        query = self.db.collection(collection).where(field, "==", value).limit(1)
        docs = await query.get()
        if docs:
            data = docs[0].to_dict()
            data["id"] = docs[0].id
            return data
        return None
    
    async def list_with_filters(self, collection: str, filters: list[tuple] = None, limit: int = 10, last_doc_id: str = None):
        """
        filters: lista de tuplas ex: [("status", "==", "active"), ("age", ">", 20)]
        """
        ref = self.db.collection(collection)
        if filters:
            for field, op, value in filters:
                ref = ref.where(field, op, value)

        ref = ref.order_by("__name__") # Ordena pelo ID do documento

        if last_doc_id:
            last_doc = await self.db.collection(collection).document(last_doc_id).get()
            if last_doc.exists:
                ref = ref.start_after(last_doc)
        
        docs = await ref.limit(limit).get()
        return [
            {**doc.to_dict(), "id": doc.id}
            for doc in docs
        ]

    async def save(self, collection: str, data: dict, doc_id: Optional[str] = None):
        """Comando centralizado para salvar/atualizar dados"""
        data_return = {**data}
        if doc_id: 
            await self.db.collection(collection).document(doc_id).set(data, merge=True)
            data_return["id"] = doc_id
        else:
            _, doc_ref = await self.db.collection(collection).add(data)
            data_return["id"] = doc_ref.id
        return data_return
    
    async def update_fields(self, collection: str, doc_id: str, data: dict):
        """Atualiza campos específicos de um documento existente"""
        await self.db.collection(collection).document(doc_id).update(data)

    async def delete(self, collection: str, doc_id: str):
        await self.db.collection(collection).document(doc_id).delete()