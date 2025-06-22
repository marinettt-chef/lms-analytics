# app/routes/analytics.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database import get_db
from app.models import Course, Topic, Entry, User, Enrollment
from datetime import datetime, timedelta
import json

router = APIRouter()

@router.get("/course-stats")
async def get_course_stats(db: Session = Depends(get_db)):
    """Get overall course statistics"""
    
    # Total courses
    total_courses = db.query(Course).count()
    
    # Active topics per course
    topic_stats = db.query(
        Course.course_name,
        func.count(Topic.topic_id).label('topic_count')
    ).select_from(Course).join(Topic, Course.course_id == Topic.course_id).filter(
        Topic.topic_state == 'active'
    ).group_by(Course.course_name).all()
    
    # Discussion activity per course
    activity_stats = db.query(
        Course.course_name,
        func.count(Entry.entry_id).label('entry_count')
    ).select_from(Course).join(Topic, Course.course_id == Topic.course_id).join(
        Entry, Topic.topic_id == Entry.topic_id
    ).filter(
        Entry.entry_state == 'active'
    ).group_by(Course.course_name).all()
    
    # Student participation per course
    participation_stats = db.query(
        Course.course_name,
        func.count(func.distinct(Entry.entry_posted_by_user_id)).label('active_students')
    ).select_from(Course).join(Topic, Course.course_id == Topic.course_id).join(
        Entry, Topic.topic_id == Entry.topic_id
    ).join(User, Entry.entry_posted_by_user_id == User.user_id).filter(
        Entry.entry_state == 'active',
        User.user_state == 'registered'
    ).group_by(Course.course_name).all()
    
    return {
        "total_courses": total_courses,
        "topic_stats": [{"course": name, "topics": count} for name, count in topic_stats],
        "activity_stats": [{"course": name, "posts": count} for name, count in activity_stats],
        "participation_stats": [{"course": name, "active_students": count} for name, count in participation_stats]
    }

@router.get("/discussion-timeline")
async def get_discussion_timeline(course_id: int = None, db: Session = Depends(get_db)):
    """Get discussion activity timeline"""
    
    query = db.query(
        func.date(Entry.entry_created_at).label('date'),
        func.count(Entry.entry_id).label('post_count')
    ).filter(Entry.entry_state == 'active')
    
    if course_id:
        query = query.select_from(Entry).join(Topic, Entry.topic_id == Topic.topic_id).filter(
            Topic.course_id == course_id
        )
    
    timeline = query.group_by(func.date(Entry.entry_created_at)).order_by('date').all()
    
    return [{"date": str(date), "posts": count} for date, count in timeline]

@router.get("/student-engagement/{course_id}")
async def get_student_engagement(course_id: int, db: Session = Depends(get_db)):
    """Get student engagement metrics for a specific course"""
    
    # Get enrolled students
    students = db.query(User).select_from(User).join(
        Enrollment, User.user_id == Enrollment.user_id
    ).filter(
        Enrollment.course_id == course_id,
        Enrollment.enrollment_type == 'student',
        Enrollment.enrollment_state == 'active'
    ).all()
    
    engagement_data = []
    
    for student in students:
        # Count posts by student in this course
        post_count = db.query(Entry).select_from(Entry).join(
            Topic, Entry.topic_id == Topic.topic_id
        ).filter(
            Topic.course_id == course_id,
            Entry.entry_posted_by_user_id == student.user_id,
            Entry.entry_state == 'active'
        ).count()
        
        # Count topics student has participated in
        topic_count = db.query(func.count(func.distinct(Topic.topic_id))).select_from(Topic).join(
            Entry, Topic.topic_id == Entry.topic_id
        ).filter(
            Topic.course_id == course_id,
            Entry.entry_posted_by_user_id == student.user_id,
            Entry.entry_state == 'active'
        ).scalar() or 0
        
        engagement_data.append({
            "student_name": student.user_name,
            "posts": post_count,
            "topics_participated": topic_count,
            "engagement_score": post_count + (topic_count * 2)  # Simple scoring
        })
    
    return sorted(engagement_data, key=lambda x: x['engagement_score'], reverse=True)

@router.get("/thread-analysis/{topic_id}")
async def get_thread_analysis(topic_id: int, db: Session = Depends(get_db)):
    """Analyze discussion thread structure"""
    
    # Get all entries for the topic
    entries = db.query(Entry).filter(
        Entry.topic_id == topic_id,
        Entry.entry_state == 'active'
    ).order_by(Entry.entry_created_at).all()
    
    # Build thread structure
    thread_data = {
        "total_posts": len(entries),
        "original_posts": len([e for e in entries if e.entry_parent_id is None]),
        "replies": len([e for e in entries if e.entry_parent_id is not None]),
        "participants": len(set([e.entry_posted_by_user_id for e in entries])),
        "timeline": [
            {
                "entry_id": e.entry_id,
                "created_at": e.entry_created_at.isoformat(),
                "parent_id": e.entry_parent_id,
                "author": e.author.user_name
            } for e in entries
        ]
    }
    
    return thread_data