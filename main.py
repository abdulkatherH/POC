from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import model
from database import engine, SessionLocal
from sqlalchemy.orm import session

app = FastAPI()
model.Base.metadata.create_all(bind=engine)
# @app.get('/')
# async def read():
#     return {'Message': 'Testing 1'}
class ChoiceBase(BaseModel):
    choice_text:str
    is_correct: bool

class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[session, Depends(get_db)]

@app.get("/questions/{question_id}")
async def read_question(question_id: int, db: db_dependency):
    result = db.query(model.Question).filter(model.Question.id == question_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Question is not found")
    return result   

@app.get("/choices/{question_id}")
async def read_choices(question_id: int, db: db_dependency):
    result = db.query(model.Choices).filter(model.Choices.question_id == question_id).all()
    if not result:
        raise HTTPException(status_code=404, detail="Choices is not fount")
    return result

@app.post('/questions/')
async def create_questions(question: QuestionBase, db: db_dependency):
    db_question =  model.Question(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    for choice in question.choices:
        db_choice = model.Choices(choice_text=choice.choice_text, is_correct=choice.is_correct, question_id=db_question.id)
        db.add(db_choice)
    db.commit()