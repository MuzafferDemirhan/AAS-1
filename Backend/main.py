from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

# Load environment variables
load_dotenv(encoding='utf-8')

app = Flask(__name__, static_folder='../Frontend')
CORS(app)

# Database configuration from environment variables
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'attendance_db')

# URL-encode the password to handle special characters
encoded_password = quote_plus(DB_PASSWORD)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret-key')

db = SQLAlchemy(app)

# ==================== MODELS ====================

class Student(db.Model):
    __tablename__ = 'Student'
    StudentID = db.Column(db.Integer, primary_key=True)
    FullName = db.Column(db.String(255))
    Email = db.Column(db.String(254))
    ConsentStatus = db.Column(db.String(50))
    ConsentVersion = db.Column(db.String(20))
    ConsentTextHash = db.Column(db.String(64))
    ConsentMethod = db.Column(db.String(100))
    EnrollmentDate = db.Column(db.Date)
    CourseList = db.Column(ARRAY(db.Text))

class Course(db.Model):
    __tablename__ = 'Course'
    CourseID = db.Column(db.Integer, primary_key=True)
    CourseName = db.Column(db.String(255))
    CourseCode = db.Column(db.String(20))
    InstructorID = db.Column(db.Integer)

class Instructor(db.Model):
    __tablename__ = 'Instructor'
    InstructorID = db.Column(db.Integer, primary_key=True)
    FullName = db.Column(db.String(255))
    Email = db.Column(db.String(254))
    Department = db.Column(db.String(100))

class Session(db.Model):
    __tablename__ = 'Session'
    SessionID = db.Column(db.Integer, primary_key=True)
    CourseID = db.Column(db.Integer, db.ForeignKey('Course.CourseID'))
    InstructorID = db.Column(db.Integer)
    StartTime = db.Column(db.DateTime(timezone=True))
    EndTime = db.Column(db.DateTime(timezone=True))
    AttendanceWindowBefore = db.Column(db.Integer)
    AttendanceWindowAfter = db.Column(db.Integer)
    Status = db.Column(db.String(50))

class AttendanceRecord(db.Model):
    __tablename__ = 'AttendanceRecord'
    RecordID = db.Column(db.Integer, primary_key=True)
    SessionID = db.Column(db.Integer, db.ForeignKey('Session.SessionID'))
    StudentID = db.Column(db.Integer, db.ForeignKey('Student.StudentID'))
    PresentFlag = db.Column(db.Boolean)
    FirstSeenAt = db.Column(db.DateTime(timezone=True))
    LastSeenAt = db.Column(db.DateTime(timezone=True))
    CumulativeSecondsVisible = db.Column(db.Integer)
    AverageConfidence = db.Column(db.Numeric)
    CamerasSeen = db.Column(ARRAY(db.Integer))
    IsManualOverride = db.Column(db.Boolean)

class AuditLog(db.Model):
    __tablename__ = 'AuditLog'
    LogID = db.Column(db.Integer, primary_key=True)
    ActorID = db.Column(db.String(100))
    Action = db.Column(db.String(50))
    Target = db.Column(db.String(255))
    Timestamp = db.Column(db.DateTime(timezone=True))
    Details = db.Column(db.Text)
    PreviousValue = db.Column(JSONB)
    NewValue = db.Column(JSONB)

# ==================== MOCK AUTH (NOT CONNECTED TO DB) ====================

# Mock users for login (username/email: password)
MOCK_USERS = {
    'admin@smartattend.ai': 'admin123',
    'instructor@smartattend.ai': 'instructor123',
    'student@smartattend.ai': 'student123'
}

# Mock signup storage (in-memory)
MOCK_REGISTERED_USERS = {}

# ==================== ROUTES ====================

# Serve Frontend Files
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'login.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# ==================== AUTH ENDPOINTS ====================

@app.route('/api/login', methods=['POST'])
def login():
    """Mock login endpoint - NOT connected to database"""
    data = request.json
    email = data.get('email', '')
    password = data.get('password', '')
    
    # Check mock users first
    if email in MOCK_USERS and MOCK_USERS[email] == password:
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'email': email,
                'name': email.split('@')[0].capitalize()
            }
        }), 200
    
    # Check registered users
    if email in MOCK_REGISTERED_USERS and MOCK_REGISTERED_USERS[email]['password'] == password:
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'email': email,
                'name': MOCK_REGISTERED_USERS[email]['name']
            }
        }), 200
    
    return jsonify({
        'success': False,
        'message': 'Invalid credentials'
    }), 401

@app.route('/api/register', methods=['POST'])
def register():
    """Mock registration endpoint - NOT connected to database"""
    data = request.json
    name = data.get('name', '')
    email = data.get('email', '')
    password = data.get('password', '')
    
    if not name or not email or not password:
        return jsonify({
            'success': False,
            'message': 'All fields are required'
        }), 400
    
    if email in MOCK_USERS or email in MOCK_REGISTERED_USERS:
        return jsonify({
            'success': False,
            'message': 'User already exists'
        }), 400
    
    # Store in mock registry
    MOCK_REGISTERED_USERS[email] = {
        'name': name,
        'password': password
    }
    
    return jsonify({
        'success': True,
        'message': 'Registration successful',
        'user': {
            'email': email,
            'name': name
        }
    }), 201

# ==================== STUDENT ENDPOINTS ====================

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get all students"""
    students = Student.query.all()
    return jsonify([{
        'StudentID': s.StudentID,
        'FullName': s.FullName,
        'Email': s.Email,
        'ConsentStatus': s.ConsentStatus,
        'EnrollmentDate': s.EnrollmentDate.isoformat() if s.EnrollmentDate else None,
        'CourseList': s.CourseList
    } for s in students])

@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Get specific student"""
    student = Student.query.get_or_404(student_id)
    return jsonify({
        'StudentID': student.StudentID,
        'FullName': student.FullName,
        'Email': student.Email,
        'ConsentStatus': student.ConsentStatus,
        'EnrollmentDate': student.EnrollmentDate.isoformat() if student.EnrollmentDate else None,
        'CourseList': student.CourseList
    })

@app.route('/api/students', methods=['POST'])
def create_student():
    """Create new student"""
    data = request.json
    student = Student(
        FullName=data.get('FullName'),
        Email=data.get('Email'),
        ConsentStatus=data.get('ConsentStatus', 'pending'),
        EnrollmentDate=datetime.now().date(),
        CourseList=data.get('CourseList', [])
    )
    db.session.add(student)
    db.session.commit()
    return jsonify({'StudentID': student.StudentID, 'message': 'Student created'}), 201

# ==================== COURSE ENDPOINTS ====================

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses"""
    courses = Course.query.all()
    return jsonify([{
        'CourseID': c.CourseID,
        'CourseName': c.CourseName,
        'CourseCode': c.CourseCode,
        'InstructorID': c.InstructorID
    } for c in courses])

@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Get specific course"""
    course = Course.query.get_or_404(course_id)
    return jsonify({
        'CourseID': course.CourseID,
        'CourseName': course.CourseName,
        'CourseCode': course.CourseCode,
        'InstructorID': course.InstructorID
    })

@app.route('/api/courses', methods=['POST'])
def create_course():
    """Create new course"""
    data = request.json
    course = Course(
        CourseName=data.get('CourseName'),
        CourseCode=data.get('CourseCode'),
        InstructorID=data.get('InstructorID')
    )
    db.session.add(course)
    db.session.commit()
    return jsonify({'CourseID': course.CourseID, 'message': 'Course created'}), 201

# ==================== SESSION ENDPOINTS ====================

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all sessions"""
    sessions = Session.query.all()
    return jsonify([{
        'SessionID': s.SessionID,
        'CourseID': s.CourseID,
        'InstructorID': s.InstructorID,
        'StartTime': s.StartTime.isoformat() if s.StartTime else None,
        'EndTime': s.EndTime.isoformat() if s.EndTime else None,
        'Status': s.Status
    } for s in sessions])

@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """Get specific session"""
    session = Session.query.get_or_404(session_id)
    return jsonify({
        'SessionID': session.SessionID,
        'CourseID': session.CourseID,
        'InstructorID': session.InstructorID,
        'StartTime': session.StartTime.isoformat() if session.StartTime else None,
        'EndTime': session.EndTime.isoformat() if session.EndTime else None,
        'Status': session.Status
    })

@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create new session"""
    data = request.json
    session = Session(
        CourseID=data.get('CourseID'),
        InstructorID=data.get('InstructorID'),
        StartTime=datetime.fromisoformat(data.get('StartTime')) if data.get('StartTime') else None,
        EndTime=datetime.fromisoformat(data.get('EndTime')) if data.get('EndTime') else None,
        AttendanceWindowBefore=data.get('AttendanceWindowBefore', 10),
        AttendanceWindowAfter=data.get('AttendanceWindowAfter', 10),
        Status=data.get('Status', 'scheduled')
    )
    db.session.add(session)
    db.session.commit()
    return jsonify({'SessionID': session.SessionID, 'message': 'Session created'}), 201

# ==================== ATTENDANCE ENDPOINTS ====================

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    """Get all attendance records"""
    records = AttendanceRecord.query.all()
    return jsonify([{
        'RecordID': r.RecordID,
        'SessionID': r.SessionID,
        'StudentID': r.StudentID,
        'PresentFlag': r.PresentFlag,
        'FirstSeenAt': r.FirstSeenAt.isoformat() if r.FirstSeenAt else None,
        'LastSeenAt': r.LastSeenAt.isoformat() if r.LastSeenAt else None,
        'IsManualOverride': r.IsManualOverride
    } for r in records])

@app.route('/api/attendance/session/<int:session_id>', methods=['GET'])
def get_attendance_by_session(session_id):
    """Get attendance for specific session"""
    records = AttendanceRecord.query.filter_by(SessionID=session_id).all()
    return jsonify([{
        'RecordID': r.RecordID,
        'SessionID': r.SessionID,
        'StudentID': r.StudentID,
        'PresentFlag': r.PresentFlag,
        'FirstSeenAt': r.FirstSeenAt.isoformat() if r.FirstSeenAt else None,
        'LastSeenAt': r.LastSeenAt.isoformat() if r.LastSeenAt else None,
        'IsManualOverride': r.IsManualOverride
    } for r in records])

@app.route('/api/attendance/student/<int:student_id>', methods=['GET'])
def get_attendance_by_student(student_id):
    """Get attendance for specific student"""
    records = AttendanceRecord.query.filter_by(StudentID=student_id).all()
    return jsonify([{
        'RecordID': r.RecordID,
        'SessionID': r.SessionID,
        'StudentID': r.StudentID,
        'PresentFlag': r.PresentFlag,
        'FirstSeenAt': r.FirstSeenAt.isoformat() if r.FirstSeenAt else None,
        'LastSeenAt': r.LastSeenAt.isoformat() if r.LastSeenAt else None,
        'IsManualOverride': r.IsManualOverride
    } for r in records])

@app.route('/api/attendance', methods=['POST'])
def create_attendance():
    """Create new attendance record (manual override)"""
    data = request.json
    record = AttendanceRecord(
        SessionID=data.get('SessionID'),
        StudentID=data.get('StudentID'),
        PresentFlag=data.get('PresentFlag', True),
        FirstSeenAt=datetime.now(),
        LastSeenAt=datetime.now(),
        IsManualOverride=True
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'RecordID': record.RecordID, 'message': 'Attendance recorded'}), 201

@app.route('/api/attendance/<int:record_id>', methods=['PUT'])
def update_attendance(record_id):
    """Update attendance record"""
    record = AttendanceRecord.query.get_or_404(record_id)
    data = request.json
    
    if 'PresentFlag' in data:
        record.PresentFlag = data['PresentFlag']
    if 'IsManualOverride' in data:
        record.IsManualOverride = data['IsManualOverride']
    
    db.session.commit()
    return jsonify({'message': 'Attendance updated'})

# ==================== INSTRUCTOR ENDPOINTS ====================

@app.route('/api/instructors', methods=['GET'])
def get_instructors():
    """Get all instructors"""
    instructors = Instructor.query.all()
    return jsonify([{
        'InstructorID': i.InstructorID,
        'FullName': i.FullName,
        'Email': i.Email,
        'Department': i.Department
    } for i in instructors])

@app.route('/api/instructors', methods=['POST'])
def create_instructor():
    """Create new instructor"""
    data = request.json
    instructor = Instructor(
        FullName=data.get('FullName'),
        Email=data.get('Email'),
        Department=data.get('Department')
    )
    db.session.add(instructor)
    db.session.commit()
    return jsonify({'InstructorID': instructor.InstructorID, 'message': 'Instructor created'}), 201

# ==================== DASHBOARD/STATS ENDPOINTS ====================

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    total_students = Student.query.count()
    total_courses = Course.query.count()
    total_sessions = Session.query.count()
    
    # Get today's sessions
    today = datetime.now().date()
    today_sessions = Session.query.filter(
        db.func.date(Session.StartTime) == today
    ).count()
    
    return jsonify({
        'totalStudents': total_students,
        'totalCourses': total_courses,
        'totalSessions': total_sessions,
        'todaySessions': today_sessions
    })

# ==================== MAIN ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    
    # Get host and port from environment variables
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port)
