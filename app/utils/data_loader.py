import pandas as pd
from sqlalchemy.orm import Session
from app.models import User, Course, Enrollment, Topic, Entry, Login
from app.database import engine, Base
from datetime import datetime
import os
import numpy as np

def parse_datetime(date_str):
    """Parse datetime string with multiple possible formats"""
    if pd.isna(date_str) or date_str == 'NA':
        return None
    
    # Try different datetime formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%y %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(str(date_str), fmt)
        except ValueError:
            continue
    
    print(f"Warning: Could not parse datetime: {date_str}")
    return None

def load_excel_data():
    """Load data from Excel files into database"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = Session(bind=engine)
    
    try:
        data_dir = "/app/data"  # Directory where Excel files are mounted
        
        # 1. Load Users
        print("Loading users...")
        try:
            users_df = pd.read_excel(f"{data_dir}/users.xlsx")
            for _, row in users_df.iterrows():
                user = User(
                    user_id=int(row['user_id']),
                    user_name=str(row['user_name']),
                    user_created_at=parse_datetime(row['user_created_at']),
                    user_deleted_at=parse_datetime(row['user_deleted_at']) if row['user_deleted_at'] != 'NA' else None,
                    user_state=str(row['user_state'])
                )
                session.merge(user)
            print(f"Loaded {len(users_df)} users")
        except Exception as e:
            print(f"Error loading users: {e}")
        
        # 2. Load Courses
        print("Loading courses...")
        try:
            courses_df = pd.read_excel(f"{data_dir}/courses.xlsx")
            for _, row in courses_df.iterrows():
                course = Course(
                    course_id=int(row['course_id']),
                    semester=str(row['semester']),
                    course_code=str(row['course_code']),
                    course_name=str(row['course_name']),
                    course_created_at=parse_datetime(row['course_created_at'])
                )
                session.merge(course)
            print(f"Loaded {len(courses_df)} courses")
        except Exception as e:
            print(f"Error loading courses: {e}")
        
        # 3. Load Enrollment
        print("Loading enrollment...")
        try:
            enrollment_df = pd.read_excel(f"{data_dir}/enrollment.xlsx")
            for _, row in enrollment_df.iterrows():
                enrollment = Enrollment(
                    user_id=int(row['user_id']),
                    course_id=int(row['course_id']),
                    enrollment_type=str(row['enrollment_type']),
                    enrollment_state=str(row['enrollment_state'])
                )
                session.add(enrollment)
            print(f"Loaded {len(enrollment_df)} enrollments")
        except Exception as e:
            print(f"Error loading enrollment: {e}")
        
        # 4. Load Login
        print("Loading login...")
        try:
            login_df = pd.read_excel(f"{data_dir}/login.xlsx")
            for _, row in login_df.iterrows():
                login = Login(
                    user_id=int(row['user_id']),
                    user_login_id=str(row['user_login_id'])
                )
                session.merge(login)
            print(f"Loaded {len(login_df)} login records")
        except Exception as e:
            print(f"Error loading login: {e}")
        
        # 5. Load Topics
        print("Loading topics...")
        try:
            topics_df = pd.read_excel(f"{data_dir}/topics.xlsx")
            for _, row in topics_df.iterrows():
                topic = Topic(
                    topic_id=int(row['topic_id']),
                    topic_title=str(row['topic_title']),
                    topic_content=str(row['topic_content']),
                    topic_created_at=parse_datetime(row['topic_created_at']),
                    topic_deleted_at=parse_datetime(row['topic_deleted_at']) if row['topic_deleted_at'] != 'NA' else None,
                    topic_state=str(row['topic_state']),
                    course_id=int(row['course_id']),
                    topic_posted_by_user_id=int(row['topic_posted_by_user_id'])
                )
                session.merge(topic)
            print(f"Loaded {len(topics_df)} topics")
        except Exception as e:
            print(f"Error loading topics: {e}")
        
        # 6. Load Entries
        print("Loading entries...")
        try:
            entries_df = pd.read_excel(f"{data_dir}/entries.xlsx")
            for _, row in entries_df.iterrows():
                entry = Entry(
                    entry_id=int(row['entry_id']),
                    entry_content=str(row['entry_content']),
                    entry_created_at=parse_datetime(row['entry_created_at']),
                    entry_deleted_at=parse_datetime(row['entry_deleted_at']) if row['entry_deleted_at'] != 'NA' else None,
                    entry_state=str(row['entry_state']),
                    entry_parent_id=int(row['entry_parent_id']) if pd.notna(row['entry_parent_id']) and row['entry_parent_id'] != 'NA' else None,
                    entry_posted_by_user_id=int(row['entry_posted_by_user_id']),
                    topic_id=int(row['topic_id'])
                )
                session.merge(entry)
            print(f"Loaded {len(entries_df)} entries")
        except Exception as e:
            print(f"Error loading entries: {e}")
        
        # Create test accounts by finding teachers and creating login credentials
        print("Creating test accounts...")
        
        # Find teacher users
        teachers = session.query(Enrollment).filter(
            Enrollment.enrollment_type == 'teacher',
            Enrollment.enrollment_state == 'active'
        ).limit(2).all()
        
        if teachers:
            # Create instructor account (first teacher)
            instructor_login = Login(
                user_id=teachers[0].user_id,
                user_login_id="instructor1"
            )
            session.merge(instructor_login)
            
            # Create admin account (second teacher or same if only one)
            admin_user_id = teachers[1].user_id if len(teachers) > 1 else teachers[0].user_id
            admin_login = Login(
                user_id=admin_user_id,
                user_login_id="admin"
            )
            session.merge(admin_login)
            
            print(f"Created test accounts: instructor1 (user_id: {teachers[0].user_id}), admin (user_id: {admin_user_id})")
        
        session.commit()
        print("All data loaded successfully!")
        
        # Print summary statistics
        print("\n=== DATA SUMMARY ===")
        print(f"Users: {session.query(User).count()}")
        print(f"Courses: {session.query(Course).count()}")
        print(f"Enrollments: {session.query(Enrollment).count()}")
        print(f"Topics: {session.query(Topic).count()}")
        print(f"Entries: {session.query(Entry).count()}")
        print(f"Login records: {session.query(Login).count()}")
        
    except Exception as e:
        session.rollback()
        print(f"Error loading data: {e}")
        raise e
    finally:
        session.close()

def load_data_from_files(file_paths):
    """Load data from specific file paths (for custom file locations)"""
    
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)
    
    try:
        # Load each file
        for table_name, file_path in file_paths.items():
            print(f"Loading {table_name} from {file_path}...")
            df = pd.read_excel(file_path)
            
            if table_name == 'users':
                for _, row in df.iterrows():
                    user = User(
                        user_id=int(row['user_id']),
                        user_name=str(row['user_name']),
                        user_created_at=parse_datetime(row['user_created_at']),
                        user_deleted_at=parse_datetime(row['user_deleted_at']) if row['user_deleted_at'] != 'NA' else None,
                        user_state=str(row['user_state'])
                    )
                    session.merge(user)
                    
            elif table_name == 'courses':
                for _, row in df.iterrows():
                    course = Course(
                        course_id=int(row['course_id']),
                        semester=str(row['semester']),
                        course_code=str(row['course_code']),
                        course_name=str(row['course_name']),
                        course_created_at=parse_datetime(row['course_created_at'])
                    )
                    session.merge(course)
                    
            # ... add other tables as needed
            
        session.commit()
        print("Data loaded successfully from custom files!")
        
    except Exception as e:
        session.rollback()
        print(f"Error loading data: {e}")
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    load_excel_data()