from pydantic import BaseModel, Field
from typing import List, Type, TypeVar, Generic, Optional
from fastapi import APIRouter, HTTPException, status
# Schemas

class CategoryBase(BaseModel):
    name: str

class Category(CategoryBase):
    id: int = Field(..., ge=1) # Ensure id is greater than or equal to 1
    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    name: str
    category_id: int

class Task(TaskBase):

    id: int = Field(..., ge=1) # Ensure id is greater than or equal to 1
    class Config:
        from_attributes = True

# Definimos un tipo genérico para nuestros esquemas
T = TypeVar("T", bound=BaseModel)

class MyCRUDRouter(Generic[T], APIRouter):
    def __init__(self, schema: Type[T], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = schema
        self.db: List[T] = []

        # --- CREATE ---
        @self.post("/", response_model=self.schema, status_code=status.HTTP_201_CREATED)
        async def create(item: self.schema):
            self.db.append(item)
            return item

        # --- READ ALL ---
        @self.get("/", response_model=List[self.schema])
        async def get_all():
            return self.db

        # --- READ ONE ---
        @self.get("/{item_id}", response_model=self.schema)
        async def get_one(item_id: int):
            item = self._find_item(item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Elemento no encontrado")
            return item

        # --- UPDATE ---
        @self.put("/{item_id}", response_model=self.schema)
        async def update(item_id: int, updated_data: self.schema):
            for index, item in enumerate(self.db):
                if getattr(item, 'id', None) == item_id:
                    # En Pydantic V2 usamos model_dump para actualizar
                    self.db[index] = updated_data
                    return updated_data
            raise HTTPException(status_code=404, detail="No se pudo actualizar: no encontrado")

        # --- DELETE ---
        @self.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete(item_id: int):
            for index, item in enumerate(self.db):
                if getattr(item, 'id', None) == item_id:
                    self.db.pop(index)
                    return
            raise HTTPException(status_code=404, detail="No se pudo eliminar: no encontrado")

    def _find_item(self, item_id: int) -> Optional[T]:
        """Método auxiliar para buscar por ID."""
        return next((item for item in self.db if getattr(item, 'id', None) == item_id), None)

# --- Uso en tu API ---