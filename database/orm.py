import logging
from typing import Any
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from database.db_config import SessionLocal, Base
from database.models import User

object_type_hint = User
objects_type_hints = list[User] | list


class ORMBase:

    def __init__(self, model: Base):
        self.model = model

    def create(self, **object_data: dict):
        with SessionLocal() as db:
            try:
                object_data = self.model(**object_data)
                db.add(object_data)
                db.commit()

            except IntegrityError:
                logging.info(f"Already added to the database.")

            except Exception as e:
                logging.error(f"An error occurred: {e}")

    def update(self, id: int, **updated_data) -> object_type_hint:
        with SessionLocal() as db:
            try:
                object = db.query(self.model).get(id)

                if not object:
                    raise ValueError(f"User with ID {id} not found")

                # Update user fields selectively using object attributes
                for key, value in updated_data.items():
                    if hasattr(object, key):  # Check if attribute exists
                        setattr(object, key, value)

                db.commit()
                return object
            except Exception as e:
                logging.error(f"An error occurred while updating user: {e}")
                raise  # Re-raise the exception for handling outside the function

    def delete(self, id: int) -> Any:
        with SessionLocal() as db:
            try:
                object = db.query(self.model).get(id)

                if object is not None:
                    db.delete(object)
                    db.commit()

            except Exception as e:
                logging.error(f"An error occurred: {e}")

    def all(self) -> objects_type_hints:
        with SessionLocal() as db:
            return db.query(self.model).all()

    def filter(self, **filters) -> objects_type_hints:
        with SessionLocal() as db:
            try:
                query = db.query(self.model)

                # Build dynamic query based on filter keywords
                conditions = []
                for key, value in filters.items():
                    if hasattr(self.model, key):  # Check for valid filter field
                        conditions.append(getattr(self.model, key) == value)  # Basic comparison


                if "logic" in filters and filters["logic"].lower() == "or":
                    query = query.filter(or_(*conditions))  # Combine filters with OR (default)
                else:
                    query = query.filter(and_(*conditions))  # Combine filters with AND

                return query.all()  # Fetch all filtered objects
            except Exception as e:
                logging.error(f"An error occurred while filtering users: {e}")
                raise  # Re-raise the exception for handling outside the function

    def count(self) -> int:
        with SessionLocal() as db:
            return db.query(self.model).count()


UserDB = ORMBase(User)
