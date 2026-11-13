from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import Answer, Form, User
from app.schemas.form_schemas import AnswerCreate
from db.database import get_db


class AnswerService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def create_answer(self, form_id: int, answer_data: AnswerCreate, user: User) -> int:
        result = await self.db.execute(select(Form).where(Form.id == form_id))
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found",
            )

        answer = Answer(
            form_id=form_id,
            user_id=user.id,
            answers_data=answer_data.answers_data,
        )
        self.db.add(answer)
        await self.db.commit()
        await self.db.refresh(answer)
        return answer.id
