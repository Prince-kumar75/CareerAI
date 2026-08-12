import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

class ProfileTextCombiner(BaseEstimator, TransformerMixin):
    """
    Custom transformer to combine multiple text columns into a single space-separated string
    for vectorization (e.g. TF-IDF).
    """
    def __init__(self, text_cols):
        self.text_cols = text_cols
        
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        X_df = pd.DataFrame(X)
        # Ensure columns exist, fillna, join them row-wise
        joined = X_df[self.text_cols].fillna("").astype(str).agg(" ".join, axis=1)
        return joined

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensures correct types and fills missing values in the dataframe before preprocessing.
    """
    df = df.copy()
    
    categorical_cols = ['education_level', 'degree_branch', 'preferred_domain', 'preferred_job_type']
    text_cols = ['technical_skills', 'programming_languages', 'soft_skills', 'interests', 'career_interests']
    
    for col in categorical_cols:
        df[col] = df[col].fillna("Missing").astype(str).str.strip()
        
    for col in text_cols:
        df[col] = df[col].fillna("").astype(str).str.strip()
        
    df['years_of_experience'] = pd.to_numeric(df['years_of_experience'], errors='coerce').fillna(0).astype(float)
    return df

def build_preprocessor_pipeline() -> ColumnTransformer:
    """
    Builds the ColumnTransformer pipeline for features.
    """
    text_cols = ['technical_skills', 'programming_languages', 'soft_skills', 'interests', 'career_interests']
    
    # Text processing pipeline (Combine -> TF-IDF)
    text_pipeline = Pipeline([
        ('combiner', ProfileTextCombiner(text_cols)),
        ('tfidf', TfidfVectorizer(token_pattern=r'(?u)\b[\w\s+#.-]+\b', lowercase=True))
    ])
    
    # Combined preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), ['years_of_experience']),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), 
             ['education_level', 'degree_branch', 'preferred_domain', 'preferred_job_type']),
            ('text', text_pipeline, text_cols)
        ],
        remainder='drop'
    )
    
    return preprocessor
