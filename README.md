# Resume Classification System

An AI-powered resume screening system that automatically analyzes candidate resumes and provides role recommendations with selection decisions.

The Resume Classification System is able to:
- Accept PDF resume uploads through a web interface
- Extract candidate information (name, email, phone, education, experience, skills)
- Automatically determine the best-fit role for each candidate
- Provide pass/fail decisions for role-specific suitability
- Return top 3 role matches with confidence scores
- Deliver instant screening results to HR officers

Built with a full-stack architecture:
- **Backend**: FastAPI for high-performance API endpoints
- **Frontend**: React with Material-UI for intuitive user experience
- **ML Models**: Scikit-learn classifiers trained on labeled resume datasets
- **Data Processing**: PyPDF2 for text extraction and regex-based information parsing

Used scikit-learn for the ML models because they're lightweight, fast to deploy, and don't require GPU resources for inference.

[uv](https://github.com/astral-sh/uv) used as package manager.

## Features

### Two-Stage Classification Pipeline
1. **Role Classifier**: Analyzes resume features to predict the most suitable role
2. **Suitability Classifier**: For each role, determines if the candidate should be selected or rejected

### Information Extraction
- **Contact Details**: Name, email, phone number
- **Education**: Degree level and field of study
- **Experience**: Years of professional experience
- **Skills**: Technical and soft skills

### Intelligent Recommendations
- Confidence scores for each prediction
- Top 3 alternative role suggestions
- Contextual recommendation messages

## Installation

### NOTE: Application note conatainerized using Docker because require models from Jupyter notebook

### Prerequisites
- Python 3.12 or higher
- Node.js 16 or higher
- uv package manager

### Backend Setup

1. Install Python dependencies:
```bash
uv sync
```

2. Train the models (required before first run):
```bash
# Open and run the Jupyter notebook
uv run jupyter notebook resume_classification.ipynb
# Execute all cells to generate model artifacts in ./artifacts/
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Usage

### Starting the Backend

From the project root:
```bash
cd backend
uv run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Starting the Frontend

In a new terminal, from the project root:
```bash
cd frontend
npm start
```

The web interface will open at `http://localhost:3000`

### Using the System

1. Open the web interface at `http://localhost:3000`
2. Upload a PDF resume
3. Click "Analyze Resume"
4. View the results:
   - Candidate information
   - Recommended role with confidence
   - Selection decision (Pass/Fail)
   - Top 3 role matches
   - Recommendation message

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **Scikit-learn**: Machine learning models
- **PyPDF2**: PDF text extraction
- **Pandas**: Data manipulation
- **Uvicorn**: ASGI server

### Frontend
- **React**: UI framework
- **Material-UI**: Component library
- **Axios**: HTTP client

### ML Pipeline
- Feature engineering (experience scaling, education encoding, skills vectorization)
- Multi-class classification for role prediction
- Binary classification for selection decisions
- Probability calibration for confidence scores
