"""
FastAPI Backend for Resume Classification System
This API provides endpoints for HR officers to upload resumes and get role recommendations.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import numpy as np
from scipy.sparse import hstack, csr_matrix
import pandas as pd
import sys
import uvicorn

from utils import extract_text_from_pdf, extract_resume_info
from models import RoleMatch, PredictionResponse


def skill_tokenizer(text):
    """
    Custom tokenizer for skills vectorization.
    This function must be defined before loading the pickled vectorizer.
    """
    if text == 'None' or pd.isna(text):
        return []
    return [skill.strip().lower() for skill in str(text).split(',')]

sys.modules['__main__'].skill_tokenizer = skill_tokenizer

# Initialize FastAPI app
app = FastAPI(
    title="Resume Classification API",
    description="AI-powered resume screening and role recommendation system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Models on Startup
try:
    # Role Classifier
    role_classifier = joblib.load('../artifacts/role_classifier.pkl')
    
    # MODEL 2: Role-Specific Suitability Models
    role_specific_models = joblib.load('../artifacts/role_specific_models.pkl')
    
    # FEATURE TRANSFORMERS: Convert structured data to numbers
    experience_scaler = joblib.load('../artifacts/experience_scaler.pkl')
    education_encoder = joblib.load('../artifacts/education_encoder.pkl')
    skills_vectorizer = joblib.load('../artifacts/skills_vectorizer.pkl')
except Exception as e:
    print("Run the notebook first.")
    raise

@app.get("/", tags=["Health"])
async def root():
    """
    Health check endpoint to verify API is running.
    """
    return {
        "message": "API is running",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.post("/api/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_resume(
    file: UploadFile = File(..., description="Resume PDF file")
):
    """
    Analyze a resume and automatically determine the best role fit and pass/fail status.
    
    Steps:
    1. Extract text from PDF
    2. Extract candidate information
    3. Determine most suitable role automatically
    4. Check if candidate passes or fails for that role
    5. Provide top 3 role matches with confidence scores
    
    Args:
        file: PDF file of the candidate's resume
        
    Returns:
        Comprehensive prediction with pass/fail status and role recommendations
    """
    
    # Step 1: Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Step 2: Read and extract text from PDF
        pdf_content = await file.read()
        resume_text = extract_text_from_pdf(pdf_content)
        
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract sufficient text from PDF")
        
        # Step 3: Extract structured information
        candidate_info = extract_resume_info(resume_text)
        
        # Step 4: Convert structured data to features (same as training)
        # Experience Years (normalized)
        experience_years = np.array([[candidate_info['experience_years']]])
        X_experience = experience_scaler.transform(experience_years)
        X_experience_sparse = csr_matrix(X_experience)
        
        # Education Level (encoded)
        education = candidate_info['education'] if candidate_info['education'] != "Not Found" else "not found"
        try:
            X_education = education_encoder.transform([education]).reshape(-1, 1)
        except ValueError:
            # If education not seen during training, use most common class
            X_education = np.array([[0]])
        X_education_sparse = csr_matrix(X_education)
        
        # Skills (vectorized)
        skills = candidate_info['skills'] if candidate_info['skills'] != "None" else ""
        X_skills = skills_vectorizer.transform([skills])
        
        # Combine all features: [Experience | Education | Skills]
        resume_vectorized = hstack([X_experience_sparse, X_education_sparse, X_skills])
        
        # Step 5: Predict the best-fit role
        recommended_role_raw = role_classifier.predict(resume_vectorized)[0]
        role_probabilities = role_classifier.predict_proba(resume_vectorized)[0]
        
        # Clean up the role name (remove any suffixes like "_select")
        # This handles edge cases from training data
        if '_' in str(recommended_role_raw):
            recommended_role = recommended_role_raw.rsplit('_', 1)[0]
        else:
            recommended_role = recommended_role_raw
        
        # Calculate confidence (How sure is the model) for the recommended role
        role_idx = list(role_classifier.classes_).index(recommended_role_raw)
        role_confidence = float(role_probabilities[role_idx])
        
        # Step 6: Use role-specific model to decide SELECT or REJECT
        role_model = role_specific_models[recommended_role]
        suitability_prediction = role_model.predict(resume_vectorized)[0]
        suitability_proba = role_model.predict_proba(resume_vectorized)[0]
        
        # Get confidence for the prediction
        predicted_idx = list(role_model.classes_).index(suitability_prediction)
        suitability_confidence = float(suitability_proba[predicted_idx])
        
        # Determine if candidate should be selected
        # Check if the prediction is "select" or "hire"
        is_suitable = 'select' in str(suitability_prediction).lower() or 'hire' in str(suitability_prediction).lower()
        
        # Get top 3 role matches
        top_3_indices = role_probabilities.argsort()[-3:][::-1]
        top_3_roles = []
        seen_roles = set()
        
        for idx in top_3_indices:
            role_raw = role_classifier.classes_[idx]
            # Extract just the role name (remove _select/_reject suffix)
            if '_' in str(role_raw):
                role_name = role_raw.rsplit('_', 1)[0]
            else:
                role_name = role_raw
            
            # Only add unique roles (avoid duplicates from _select/_reject variants)
            if role_name not in seen_roles:
                seen_roles.add(role_name)
                top_3_roles.append(RoleMatch(
                    role=role_name,
                    confidence=float(role_probabilities[idx])
                ))
            
            # Stop once we have 3 unique roles
            if len(top_3_roles) >= 3:
                break
        
        # Generate recommendation text
        if is_suitable:
            if suitability_confidence >= 0.8:
                recommendation = "Strong candidate match."
            elif suitability_confidence >= 0.6:
                recommendation = "Good candidate match."
            else:
                recommendation = "Review candidate properly"
        else:
            recommendation = "Not a good fit"
        
        # Step 8: Return comprehensive response
        return PredictionResponse(
            candidate_name=candidate_info['name'],
            email=candidate_info['email'],
            phone=candidate_info['phone'],
            education=candidate_info['education'][:200],  # Truncate if too long
            experience_years=candidate_info['experience_years'],
            skills=candidate_info['skills'],
            is_suitable=is_suitable,
            suitability_confidence=round(suitability_confidence * 100, 2),
            recommended_role=recommended_role,
            role_confidence=round(role_confidence * 100, 2),
            top_3_roles=top_3_roles,
            recommendation=recommendation
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Run the API server
    # Visit http://localhost:8000/docs for interactive API documentation
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes (development only)
    )
