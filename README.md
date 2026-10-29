# WE UNIRESEARCHITY

A searchable repository where students and researchers at Kenyan universities can submit, discover, and browse research (theses, papers, datasets).

## Features

- **Browse and Search**: Search research by title, abstract, author, and keywords
- **Submit Research**: Easy submission form with PDF upload (max 20MB)
- **Researcher Profiles**: Public profiles showing researcher's publications
- **Admin Approval**: Password-protected admin dashboard to manage submissions
- **Mobile-First Design**: Responsive design optimized for low bandwidth and mobile devices
- **APA Citation**: Automatic APA citation generation with copy button

## Technology Stack

- **Backend**: Python with FastAPI
- **Database**: SQLite (easy to run locally)
- **Frontend**: HTML + Tailwind CSS + minimal JavaScript
- **File Storage**: Local `/uploads` folder for PDFs

## Installation

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### 2. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd WE-UNIRESEARCHITY

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize Database

The application will automatically create the SQLite database file (`database/research.db`) and seed it with sample data when you first run it.

### 4. Run the Application

```bash
# Start the development server
python main.py
```

The application will be available at `http://localhost:8000`

## Usage

### For Researchers

1. **Browse Research**: Visit the home page and use the search bar or browse recent publications
2. **Submit Research**: Click "Submit Research" in the navigation menu
3. **Complete the Form**: Fill in all required fields and upload your PDF
4. **Wait for Approval**: Your submission will be reviewed by an administrator

### For Administrators

1. **Login**: Visit `/admin` and login with:
   - Username: `admin`
   - Password: `admin123`
2. **Review Submissions**: Go to the admin dashboard to see pending submissions
3. **Approve/Reject**: Review each submission and approve or reject with a reason

## Sample Data

The database is pre-seeded with:

- **4 Kenyan Universities**: University of Nairobi, Kenyatta University, Moi University, JKUAT
- **4 Sample Researchers**: With profiles and contact information
- **5 Sample Publications**: Including theses, journal articles, and datasets
- **1 Admin User**: For managing submissions

## Project Structure

```
WE-UNIRESEARCHITY/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── database.py            # Database configuration
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic schemas
├── crud.py                # Database operations
├── auth.py                # Authentication utilities
├── config.py              # Application configuration
├── uploads/               # Uploaded PDF files
├── static/                # Static files (CSS, JS, uploads)
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Home page
│   ├── search.html        # Search results
│   ├── publication.html   # Publication detail
│   ├── researcher.html    # Researcher profile
│   ├── submit.html        # Submission form
│   ├── admin_login.html   # Admin login
│   └── admin_dashboard.html # Admin dashboard
└── database/              # SQLite database files
```

## Security Features

- **Input Validation**: All form inputs are validated on both client and server side
- **File Upload Security**: Only PDF files up to 20MB are accepted
- **Password Hashing**: Admin passwords are hashed using bcrypt
- **SQL Injection Prevention**: Using SQLAlchemy ORM with parameterized queries
- **XSS Prevention**: Template auto-escaping and input sanitization

## API Endpoints

- `GET /` - Home page with stats
- `GET /search` - Search research publications
- `GET /publication/{id}` - Publication details
- `GET /researcher/{id}` - Researcher profile
- `GET /submit` - Submission form
- `POST /api/submit` - Submit research (API)
- `GET /admin` - Admin login
- `GET /admin/dashboard` - Admin dashboard
- `POST /api/admin/login` - Admin login (API)
- `POST /api/admin/approve/{id}` - Approve publication (API)
- `POST /api/admin/reject/{id}` - Reject publication (API)

## Future Enhancements

Planned features for future versions:

1. **Email Notifications**: Notify researchers when submissions are approved/rejected
2. **Advanced Search**: Filters by citation count, publication date range
3. **Collaboration Features**: Researcher matching and messaging
4. **Analytics Dashboard**: Publication trends and statistics
5. **Export Features**: Export search results to CSV or BibTeX
6. **DOI Integration**: Automatic DOI registration
7. **Plagiarism Check**: Integration with plagiarism detection services
8. **API Access**: REST API for integration with other systems

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `config.py` or use `PORT=8001 python main.py`
2. **Database issues**: Delete `database/research.db` and restart the application
3. **File upload errors**: Ensure the `uploads` directory exists and has write permissions
4. **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

### Getting Help

If you encounter issues:

1. Check the console output for error messages
2. Ensure all dependencies are installed correctly
3. Verify file permissions on the `uploads` and `database` directories
4. Check that Python 3.8+ is installed

## License

This project is developed for educational and demonstration purposes.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for the backend
- Styled with [Tailwind CSS](https://tailwindcss.com/) for the frontend
- Icons from [Font Awesome](https://fontawesome.com/)
- Sample data represents typical research from Kenyan universities

## Demo Credentials

- **Admin**: `admin` / `admin123`
- **Sample Researcher Email**: `jane.wanjiku@uon.ac.ke`
- **Sample Publication**: "Machine Learning for Crop Disease Detection in Smallholder Farms"