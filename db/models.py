from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Promoter(Base):
    __tablename__ = "promoters"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    projects = relationship("Project", back_populates="promoter")


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    rera_id = Column(String, unique=True, nullable=False)
    address = Column(String)
    promoter_id = Column(Integer, ForeignKey("promoters.id"))
    promoter = relationship("Promoter", back_populates="projects")
