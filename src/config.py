from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT_DIR / "data" / "raw" / "data.csv"
MODELS_DIR = ROOT_DIR / "models"
RULES_DB = ROOT_DIR / "data" / "rules" / "rules.json"
HISTORY_DB = ROOT_DIR / "data" / "history" / "recommendations.json"

COURSES = [
    "Operating System",
    "Algorithm and Programming",
    "Program Design Methods",
    "Discrete Mathematics",
    "Linear Algebra",
    "Basic Statistics",
    "Data Structures",
    "Web Development",
    "Calculus",
    "Artificial Intelligence",
    "Algorithm Design and Analysis",
    "Database Technology",
    "Object Oriented Programming",
    "Computer Networks",
]

MAJORS = [
    "DATA SCIENCE",
    "INTERNET OF THINGS",
    "DATABASE TECHNOLOGY",
    "INTELLIGENT SYSTEM",
    "GAME TECHNOLOGY",
    "NETWORK TECHNOLOGY",
    "SOFTWARE ENGINEERING",
]

MAJOR_LABELS_VI = {
    "DATA SCIENCE": "Khoa học Dữ liệu",
    "INTERNET OF THINGS": "Internet vạn vật (IoT)",
    "DATABASE TECHNOLOGY": "Công nghệ Cơ sở dữ liệu",
    "INTELLIGENT SYSTEM": "Hệ thống Thông minh",
    "GAME TECHNOLOGY": "Công nghệ Game",
    "NETWORK TECHNOLOGY": "Công nghệ Mạng",
    "SOFTWARE ENGINEERING": "Kỹ thuật Phần mềm",
}

COURSE_LABELS_VI = {
    "Operating System": "Hệ điều hành",
    "Algorithm and Programming": "Thuật toán và Lập trình",
    "Program Design Methods": "Phương pháp Thiết kế Chương trình",
    "Discrete Mathematics": "Toán rời rạc",
    "Linear Algebra": "Đại số tuyến tính",
    "Basic Statistics": "Thống kê cơ bản",
    "Data Structures": "Cấu trúc dữ liệu",
    "Web Development": "Phát triển Web",
    "Calculus": "Giải tích",
    "Artificial Intelligence": "Trí tuệ nhân tạo",
    "Algorithm Design and Analysis": "Thiết kế và Phân tích Thuật toán",
    "Database Technology": "Công nghệ CSDL",
    "Object Oriented Programming": "Lập trình Hướng đối tượng",
    "Computer Networks": "Mạng máy tính",
}

# Trọng số lai: AI vs Hệ chuyên gia
HYBRID_AI_WEIGHT = 0.6
HYBRID_EXPERT_WEIGHT = 0.4

ADMIN_PASSWORD = "admin123"
