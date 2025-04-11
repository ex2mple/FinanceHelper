# Здесь создавайте папки по их фичам (users, auth и пр.)
Их нужно создавать, как пакет (внутри должен быть __init__.py)
Внутри пакета такая архитектура (crud.py, schemas.py (схемы моделей), views.py (роуты))

```python
# пример файла views.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import db_helper
router = APIRouter(tags=["Auth"])

@router.get("/")
async def index(session: AsyncSession = Depends(db_helper.session_dependency)):
    return 'some'
```