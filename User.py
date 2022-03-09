from sqlalchemy import Column, String, BigInteger
from db_config import Base, create_all_entities


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger(), primary_key=True, nullable=False, autoincrement=True)
    username = Column(String(), nullable=False, unique=True)
    password = Column(String(), nullable=False)

    def __repr__(self):
        return f'Customer(id={self.id}, username="{self.username}", password="{self.password}")'

    def __str__(self):
        return f'Customer[id={self.id}, username="{self.username}", password="{self.password}"]'
