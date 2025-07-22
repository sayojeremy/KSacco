from . import db
from sqlalchemy import Integer, String, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import date

class Users(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable= False)
    last_name: Mapped[str] = mapped_column(String(100), nullable= False)
    phone_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    id_number: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    date_joined: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)