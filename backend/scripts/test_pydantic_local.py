import asyncio
import traceback
from app.core.database import AsyncSessionLocal
from app.repositories.visitor_repository import VisitorRepository
from app.schemas.visitor import VisitorResponse
from app.services.visitor_service import VisitorService
from app.models.user import User

async def main():
    async with AsyncSessionLocal() as session:
        service = VisitorService(session)
        repo = VisitorRepository(session)
        user = User(id="72696622-1f96-47f0-8c88-3562ca619176", username="admin")
        items, _ = await repo.search_and_filter(limit=1)
        if items:
            v = items[0]
            print(f"Testing checkout for visitor {v.id}...")
            res = await service.checkout_visitor(v.id, current_user=user)
            print("CHECKOUT RETURNED ORM OBJ:", res)
            try:
                dto = VisitorResponse.model_validate(res)
                print("DTO MODEL VALIDATED:", dto.model_dump())
            except Exception as e:
                print("DTO MODEL VALIDATE FAILED:")
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
