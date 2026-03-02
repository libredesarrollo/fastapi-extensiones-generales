from pydantic import BaseModel, Field
from typing import List, Type, TypeVar, Generic, Optional
from fastapi import APIRouter, HTTPException, status, Depends

from typing import Generic, TypeVar, Type, List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
# Schemas


from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship

class CategoryBase(BaseModel):
    name: str

class Category(CategoryBase):
    id: int = Field(..., ge=1) # Ensure id is greater than or equal to 1
    class Config:
        from_attributes = True

# Este se usa para el "Body" del POST (Entrada)
class CategoryCreate(BaseModel):
    name: str

class TaskBase(BaseModel):
    name: str
    category_id: int

class Task(TaskBase):

    id: int = Field(..., ge=1) # Ensure id is greater than or equal to 1
    class Config:
        from_attributes = True
        
        


# 1. Definimos la Clase Base (Recomendado en SQLAlchemy 2.0)
class Base(DeclarativeBase):
    pass

# 2. El Modelo de la Entidad
class CategoryModel(Base):
    __tablename__ = "categories"

    # Definimos las columnas
    id=Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)

    # Opcional: Si quieres que una categoría tenga muchas tareas
    # tasks = relationship("TaskModel", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"        



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

# T = TypeVar("T", bound=BaseModel) # Para Pydantic
M = TypeVar("M")                 # Para el Modelo de SQLAlchemy

class SQLCRUDRouter(Generic[T, M], APIRouter):
    def __init__(self, schema: Type[T], model: Type[M], get_db_func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = schema
        self.model = model
        self.get_db = get_db_func

        # --- CREATE ---
        @self.post("/", response_model=self.schema, status_code=status.HTTP_201_CREATED)
        def create(item: self.schema, db: Session = Depends(self.get_db)):
            # Convertimos Pydantic a Modelo de SQLAlchemy
            
            # 2. Creamos la instancia del modelo de SQLAlchemy con los datos limpios
            # db_item = self.model(**item.model_dump()) # hay que quitar el id
            db_item = self.model(**item.model_dump(exclude={'id'}, exclude_unset=True))
    
            
          
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            return db_item

        # --- READ ALL ---
        @self.get("/", response_model=List[self.schema])
        def get_all(db: Session = Depends(self.get_db)):
            # Usamos la nueva sintaxis de SQLAlchemy 2.0 (select)
            result = db.execute(select(self.model)).scalars().all()
            return result

        # --- READ ONE ---
        @self.get("/{item_id}", response_model=self.schema)
        def get_one(item_id: int, db: Session = Depends(self.get_db)):
            db_item = db.get(self.model, item_id)
            if not db_item:
                raise HTTPException(status_code=404, detail="No encontrado")
            return db_item

        # --- DELETE ---
        @self.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
        def delete(item_id: int, db: Session = Depends(self.get_db)):
            db_item = db.get(self.model, item_id)
            if not db_item:
                raise HTTPException(status_code=404, detail="No encontrado")
            db.delete(db_item)
            db.commit()
            return
        # --- UPDATE ---
        @self.put("/{item_id}", response_model=self.schema)
        def update(item_id: int, updated_data: self.schema, db: Session = Depends(self.get_db)):
            # 1. Buscar el registro existente
            db_item = db.get(self.model, item_id)
            if not db_item:
                raise HTTPException(status_code=404, detail="No se pudo actualizar: no encontrado")

            # 2. Extraer los datos de Pydantic
            # Excluimos 'id' para evitar que intenten cambiar la PK de la fila
            # exclude_unset=True permite actualizaciones parciales si el esquema lo soporta
            update_dict = updated_data.model_dump(exclude={'id'}, exclude_unset=True)

            # 3. Actualizar los atributos del modelo dinámicamente
            for key, value in update_dict.items():
                setattr(db_item, key, value)

            # 4. Persistir
            db.commit()
            db.refresh(db_item)
            return db_item