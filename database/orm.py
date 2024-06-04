import logging
from typing import Any

from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError

from database.datatypes import UserType
from database.db_config import SessionLocal, get_db
from database.models import User


class UserDB:

    @staticmethod
    def create(user_data: UserType):
        with SessionLocal() as db:
            try:
                user_data = User(**user_data)
                db.add(user_data)
                db.commit()

            except IntegrityError as e:
                logging.info(f"Already added to the database.")

            except Exception as e:
                logging.error(f"An error occurred: {e}")

    @staticmethod
    def get(user_id: int) -> User:
        with SessionLocal() as db:
            try:
                user = db.query(User).get(user_id)
                return user

            except Exception as e:
                logging.error(f"An error occurred: {e}")

    @staticmethod
    def update(user_id: int, **updated_data) -> User:
        with SessionLocal() as db:
            try:
                user = db.query(User).get(user_id)
                if not user:
                    raise ValueError(f"User with ID {user_id} not found")

                # Update user fields selectively using object attributes
                for key, value in updated_data.items():
                    if hasattr(user, key):  # Check if attribute exists
                        setattr(user, key, value)

                db.commit()
                return user
            except Exception as e:
                logging.error(f"An error occurred while updating user: {e}")
                raise  # Re-raise the exception for handling outside the function

    @staticmethod
    def delete(user_id: int) -> Any:
        with SessionLocal() as db:
            try:
                user = db.query(User).get(user_id)

                if user is not None:
                    db.delete(user)
                    db.commit()

            except Exception as e:
                logging.error(f"An error occurred: {e}")

    @staticmethod
    def all() -> list | list[User]:
        with SessionLocal() as db:
            return db.query(User).all()


    @staticmethod
    def filter(**filters) -> list[User] | list:
        with SessionLocal() as db:
            try:
                query = db.query(User)

                # Build dynamic query based on filter keywords
                conditions = []
                for key, value in filters.items():
                    if hasattr(User, key):  # Check for valid filter field
                        conditions.append(getattr(User, key) == value)  # Basic comparison

                # Combine conditions with OR and AND logic based on a separate parameter

                if "logic" in filters and filters["logic"].lower() == "or":
                    query = query.filter(or_(*conditions))  # Combine filters with OR (default)
                else:
                    query = query.filter(and_(*conditions))  # Combine filters with AND

                return query.all()  # Fetch all filtered objects
            except Exception as e:
                logging.error(f"An error occurred while filtering users: {e}")
                raise  # Re-raise the exception for handling outside the function
