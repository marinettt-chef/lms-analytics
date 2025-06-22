from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Course, Topic, Entry, Enrollment
from app.auth import verify_user, create_access_token, get_current_user, is_instructor, is_admin
from app.routes import analytics
from app.utils.data_loader import load_excel_data
import os
from datetime import timedelta

app = FastAPI(title="LMS Discussion Analytics", version="1.0.0")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include analytics routes
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.on_event("startup")
async def startup_event():
    """Initialize database with sample data"""
    try:
        load_excel_data()
    except Exception as e:
        print(f"Warning: Could not load initial data: {e}")

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), db: Session = Depends(get_db)):
    """Handle login"""
    user = verify_user(db, username)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Invalid credentials"
        })
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.user_id)}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard"""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/")
    
    user = get_current_user(token, db)
    if not user:
        return RedirectResponse(url="/")
    
    # Get user's accessible courses
    if is_admin(user):
        courses = db.query(Course).all()
    else:
        courses = db.query(Course).join(Enrollment).filter(
            Enrollment.user_id == user.user_id,
            Enrollment.enrollment_state == 'active'
        ).all()
    
    # Get recent discussion activity
    recent_entries = db.query(Entry).join(Topic).join(Course).filter(
        Entry.entry_state == 'active'
    ).order_by(Entry.entry_created_at.desc()).limit(10).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "courses": courses,
        "recent_entries": recent_entries,
        "is_admin": is_admin(user),
        "is_instructor": is_instructor(user, db)
    })

@app.get("/analytics/{course_id}", response_class=HTMLResponse)
async def course_analytics(request: Request, course_id: int, db: Session = Depends(get_db)):
    """Course-specific analytics page"""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/")
    
    user = get_current_user(token, db)
    if not user:
        return RedirectResponse(url="/")
    
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "user": user,
        "course": course,
        "course_id": course_id
    })

@app.get("/logout")
async def logout():
    """Logout and clear session"""
    response = RedirectResponse(url="/")
    response.delete_cookie(key="access_token")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    