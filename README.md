# Student Behavior Analysis Web Application

A comprehensive web application for managing students and training AI face recognition systems for behavioral analysis.

## ✨ Features

### 👥 Student Management
- **Complete Student Profiles**: Full personal, contact, and academic information
- **Auto-generated Student Codes**: Automatic generation of unique student identifiers
- **Advanced Search & Filter**: Search by name, code, email, or class with status filtering
- **Data Export**: Export student data to CSV format
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### 🤖 AI Face Recognition
- **Face Photo Upload**: Batch upload multiple photos for better recognition accuracy
- **AI Embedding Generation**: Automatic face embedding creation for recognition training
- **Photo Management**: View and manage training photos with detailed metadata
- **Recognition Statistics**: Track AI training progress and embedding counts

### 🎨 Modern UI/UX
- **Professional Design**: Clean, modern interface using TailwindCSS and DaisyUI
- **Interactive Components**: Real-time updates with Alpine.js
- **Icon Integration**: Beautiful Lucide icons throughout the interface
- **Loading States**: Smooth loading animations and progress indicators
- **Toast Notifications**: User-friendly success/error messages

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **MySQL**: Relational database
- **Pydantic**: Data validation using Python type annotations
- **FAISS**: Vector similarity search for face embeddings
- **OpenCV**: Computer vision library
- **Ultralytics YOLO**: Object detection and face recognition

### Frontend
- **HTML5 + Jinja2**: Template engine for server-side rendering
- **TailwindCSS**: Utility-first CSS framework
- **DaisyUI**: Component library for TailwindCSS
- **Alpine.js**: Lightweight JavaScript framework
- **HTMX**: High power tools for HTML
- **Lucide Icons**: Beautiful & consistent icon pack

## 📋 Requirements

- Python 3.11+
- MySQL 8.0+
- Modern web browser with JavaScript enabled

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd student_behavior_web
```

### 2. Install Dependencies
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 3. Database Setup
1. Create a MySQL database
2. Update database configuration in `core/config.py`
3. The application will automatically create tables on first run

### 4. Configuration
Create or update `core/config.py` with your settings:
```python
DATABASE_URL = "mysql+pymysql://username:password@localhost/database_name"
UPLOAD_DIR = "uploads"
```

### 5. Run the Application
```bash
# Development server
python run_server.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Access the Application
Open your browser and navigate to: `http://localhost:8000`

## 📖 Usage Guide

### Student Management

#### Adding a New Student
1. Click the "Add Student" button on the main page
2. Fill in the student information form:
   - **Personal Info**: Name, student code, date of birth, gender, address
   - **Contact Info**: Email, phone number
   - **Academic Info**: Class, course, major, academic level, GPA, status
3. Click "Add Student" to save

#### Managing Students
- **Search**: Use the search bar to find students by name, code, email, or class
- **Filter**: Filter students by status (Active, Inactive, Graduated)
- **Edit**: Click the "Edit" button to modify student information
- **Delete**: Click the "Delete" button to remove a student (with confirmation)
- **Export**: Click "Export" to download student data as CSV

### Face Recognition Training

#### Uploading Photos
1. Click "Faces" next to a student in the list
2. Select multiple photos using the file input
3. Click "Upload Photos" to process the images
4. The system will automatically generate AI embeddings for face recognition

#### Best Practices for Photo Upload
- Upload 5-10 clear photos per student
- Ensure good lighting and face visibility
- Use different angles and expressions
- Supported formats: JPG, PNG, GIF

## 🏗️ Project Structure

```
student_behavior_web/
├── app/                    # API routes and business logic
│   ├── auth_api.py        # Authentication endpoints
│   ├── routers.py         # Router configuration
│   └── students_api.py    # Student management endpoints
├── core/                   # Core utilities and configuration
│   ├── config.py          # Application configuration
│   ├── database.py        # Database connection and setup
│   ├── fastapi_logger.py  # Logging configuration
│   └── fastapi_util.py    # FastAPI utilities and helpers
├── db/                     # Database models and operations
│   ├── crud.py            # Database CRUD operations
│   ├── models.py          # SQLAlchemy models
│   └── vector_db.py       # Vector database for embeddings
├── services/               # Business logic services
│   ├── ai_loader.py       # AI model loading and management
│   ├── enrollment.py      # Student enrollment services
│   └── pipeline.py        # Data processing pipelines
├── templates/              # HTML templates
│   ├── layout.html        # Base template
│   ├── students.html      # Student management page
│   └── faces.html         # Face training page
├── static/                 # Static assets
├── uploads/                # Uploaded files storage
├── main.py                # FastAPI application entry point
├── run_server.py          # Development server runner
└── requirements.txt       # Python dependencies
```

## 🔧 API Documentation

The application provides a comprehensive REST API. Access the interactive documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### Students
- `GET /api/students` - List students with search and pagination
- `POST /api/students` - Create a new student
- `GET /api/students/{id}` - Get student details
- `PUT /api/students/{id}` - Update student information
- `DELETE /api/students/{id}` - Delete a student

#### Face Recognition
- `POST /api/students/{id}/face` - Upload single face photo
- `POST /api/students/{id}/faces/batch` - Batch upload face photos
- `GET /api/students/{id}/photos` - List student photos

## 🔒 Security Features

- Input validation and sanitization
- SQL injection prevention through ORM
- File upload security with type validation
- Error handling and logging
- CORS configuration for API security

## 🎯 Performance Optimizations

- Database query optimization with proper indexing
- Lazy loading for large datasets
- Image compression for uploaded photos
- Efficient vector search using FAISS
- Caching for frequently accessed data

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check MySQL server is running
   - Verify database credentials in config
   - Ensure database exists

2. **File Upload Issues**
   - Check upload directory permissions
   - Verify file size limits
   - Ensure supported file formats

3. **AI Model Loading Error**
   - Check model files are present
   - Verify system has sufficient memory
   - Install required AI dependencies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI team for the excellent web framework
- TailwindCSS and DaisyUI for the beautiful UI components
- Alpine.js for lightweight JavaScript functionality
- Lucide for the comprehensive icon set
- The open-source community for various tools and libraries

## 📞 Support

For support, please open an issue in the repository or contact the development team.

---

**Built with ❤️ for educational institutions and student management systems.**