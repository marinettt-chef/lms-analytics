# LMS Discussion Analytics

Web application for analyzing student discussion data from Learning Management Systems.

🚀 Live Demo
Railway Deployment: https://lms-analytics-production.up.railway.app

Note: Demo link is temporary and will be available for approximately 1 month. For permanent access, deploy locally using Docker.

## Problem

Instructors need to understand student engagement in online discussions. Raw LMS data is hard to interpret without visualization and analytics.

## Solution

Built a web dashboard that:
- Loads discussion data from Excel files
- Shows student engagement rankings
- Displays course-level analytics
- Provides interactive charts and metrics

## Tech Stack

- **Backend**: FastAPI + PostgreSQL
- **Frontend**: HTML templates + Bootstrap + Plotly
- **Deployment**: Docker + Docker Compose
- **Data**: Pandas for Excel processing

## Data Model

6 tables with relationships:
- `users` ↔ `courses` (via `enrollment`)
- `courses` → `topics` → `entries` (discussion hierarchy)
- `entries` can reply to other `entries` (threaded discussions)
- `login` handles authentication

## Quick Start

1. **Clone and setup:**
```bash
git clone https://github.com/marinettt-chef/lms-analytics.git
cd lms-analytics
mkdir data
```

2. **Run with Docker:**
```bash
docker-compose up --build
```

3. **Access application:**
- URL: http://localhost:8000
- Login: `instructor1` or `admin`

## Application Pages

### 1. Login Page (`/`)
- Simple login form
- Test accounts: `instructor1`, `admin`
- Shows available test credentials

### 2. Dashboard (`/dashboard`)
**All Users See:**
- Course overview cards (total courses, recent posts, active users)
- Course list table with analytics buttons
- Recent discussion activity feed
- Discussion activity timeline chart

**Instructors See:** Only courses they're enrolled in
**Admins See:** All courses and system-wide data

### 3. Course Analytics (`/analytics/{course_id}`)
**Top Statistics Cards:**
- Total Topics in course
- Total Posts in course  
- Active Students count
- Average Posts per Student

**Main Content:**
- **Student Engagement Rankings Table**: Rank, student name, posts, topics participated, engagement score
- **Course Summary**: Course ID, creation date, status
- **Quick Stats**: Bullet points with course metrics
- **Debug Info**: Real-time API call information (for troubleshooting)
- **Discussion Timeline Chart**: Interactive Plotly chart showing posts over time (helps track engagement trends, identify activity patterns, and monitor course health)

**Data Shown:**
- Real student engagement scores (posts + topics × 2)
- Ranked list of students by participation
- Timeline of discussion activity
- Course-specific statistics

### 4. User Permissions

**Instructor Account (`instructor1`):**
- Can view courses they're enrolled in as teacher
- See student engagement for their courses
- Access course-specific analytics

**Admin Account (`admin`):**
- Full access to all courses
- System-wide statistics
- All student data across courses

## File Structure

```
lms-analytics/
├── app/
│   ├── main.py              # FastAPI app
│   ├── models.py            # Database models
│   ├── auth.py              # Authentication
│   ├── routes/analytics.py  # API endpoints
│   ├── utils/data_loader.py # Excel import
│   └── templates/           # HTML pages
│       ├── base.html        # Common layout
│       ├── login.html       # Login form
│       ├── dashboard.html   # Main dashboard
│       └── analytics.html   # Course analytics
├── data/                    # Excel files go here
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Excel File Requirements

Your files must have exact column names:

**courses.xlsx:** `course_id`, `semester`, `course_code`, `course_name`, `course_created_at`

**users.xlsx:** `user_id`, `user_name`, `user_created_at`, `user_deleted_at`, `user_state`

**enrollment.xlsx:** `user_id`, `course_id`, `enrollment_type`, `enrollment_state`

**topics.xlsx:** `topic_id`, `topic_title`, `topic_content`, `topic_created_at`, `topic_deleted_at`, `topic_state`, `course_id`, `topic_posted_by_user_id`

**entries.xlsx:** `entry_id`, `entry_content`, `entry_created_at`, `entry_deleted_at`, `entry_state`, `entry_parent_id`, `entry_posted_by_user_id`, `topic_id`

**login.xlsx:** `user_id`, `user_login_id`

## Key Features

- Student engagement rankings by course
- Discussion activity timelines
- Course-level statistics
- Role-based access (instructor vs admin)
- Responsive web interface
- Real-time data loading with debug information

## API Endpoints

- `GET /api/analytics/course-stats` - Overall course statistics
- `GET /api/analytics/discussion-timeline` - Activity timeline
- `GET /api/analytics/student-engagement/{course_id}` - Student rankings
- `GET /api/analytics/thread-analysis/{topic_id}` - Thread analysis

## Example Data Flow

1. **Load Excel files** → Database tables
2. **User logs in** → Dashboard shows their courses
3. **Click "Analytics"** → Course-specific engagement data
4. **View rankings** → Students ranked by posts + topic participation
5. **Timeline chart** → Visual discussion activity over time


## Troubleshooting

**Data not loading:**
```bash
docker-compose logs web | grep Loading
docker-compose exec web ls -la /app/data
```

**Application errors:**
```bash
docker-compose logs web
docker-compose restart web
```

**Fresh start:**
```bash
docker-compose down -v
docker-compose up --build
```

## Environment

- Python 3.11
- PostgreSQL 15
- Tested on macOS and Linux

## Railway Deployment
Check logs:

Go to Railway dashboard → Your service → Logs tab
Look for startup errors or missing environment variables

Database connection issues:

Verify PostgreSQL service is running in Railway
Check DATABASE_URL environment variable is set