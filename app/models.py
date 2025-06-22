from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(100), nullable=False)
    user_created_at = Column(DateTime, nullable=False)
    user_deleted_at = Column(DateTime, nullable=True)
    user_state = Column(String(20), nullable=False)
    
    # Relationships
    enrollments = relationship("Enrollment", back_populates="user")
    topics = relationship("Topic", back_populates="creator")
    entries = relationship("Entry", back_populates="author")
    login = relationship("Login", back_populates="user", uselist=False)

class Course(Base):
    __tablename__ = "courses"
    
    course_id = Column(Integer, primary_key=True)
    semester = Column(String(10), nullable=False)
    course_code = Column(String(20), nullable=False)
    course_name = Column(String(200), nullable=False)
    course_created_at = Column(DateTime, nullable=False)
    
    # Relationships
    enrollments = relationship("Enrollment", back_populates="course")
    topics = relationship("Topic", back_populates="course")

class Enrollment(Base):
    __tablename__ = "enrollment"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    enrollment_type = Column(String(20), nullable=False)  # student/teacher
    enrollment_state = Column(String(20), nullable=False)  # active/deleted
    
    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class Topic(Base):
    __tablename__ = "topics"
    
    topic_id = Column(Integer, primary_key=True)
    topic_title = Column(String(200), nullable=False)
    topic_content = Column(Text, nullable=False)
    topic_created_at = Column(DateTime, nullable=False)
    topic_deleted_at = Column(DateTime, nullable=True)
    topic_state = Column(String(20), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    topic_posted_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    
    # Relationships
    course = relationship("Course", back_populates="topics")
    creator = relationship("User", back_populates="topics")
    entries = relationship("Entry", back_populates="topic")

class Entry(Base):
    __tablename__ = "entries"
    
    entry_id = Column(Integer, primary_key=True)
    entry_content = Column(Text, nullable=False)
    entry_created_at = Column(DateTime, nullable=False)
    entry_deleted_at = Column(DateTime, nullable=True)
    entry_state = Column(String(20), nullable=False)
    entry_parent_id = Column(Integer, ForeignKey("entries.entry_id"), nullable=True)
    entry_posted_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.topic_id"), nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="entries")
    topic = relationship("Topic", back_populates="entries")
    parent = relationship("Entry", remote_side=[entry_id])

class Login(Base):
    __tablename__ = "login"
    
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    user_login_id = Column(String(50), unique=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="login")
    