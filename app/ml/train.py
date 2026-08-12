import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

from app.ml.preprocess import clean_dataframe, build_preprocessor_pipeline
from app.ml.evaluate import evaluate_predictions, print_evaluation_report

def train_and_select_model():
    # 1. Load the dataset
    dataset_path = "data/career_dataset.csv"
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}. Please run generate_dataset.py first.")
        
    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    
    # 2. Clean data
    df_clean = clean_dataframe(df)
    
    # Split into features (X) and target (y)
    X = df_clean.drop(columns=['career_role'])
    y = df_clean['career_role']
    
    # 3. Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Define models to compare
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5)
    }
    
    best_model_name = None
    best_f1 = -1.0
    best_pipeline = None
    best_metrics = None
    
    # Compare models
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # Build a complete pipeline: Preprocessor + Model
        pipeline = Pipeline([
            ('preprocessor', build_preprocessor_pipeline()),
            ('classifier', model)
        ])
        
        # Fit pipeline
        pipeline.fit(X_train, y_train)
        
        # Predict and evaluate
        y_pred = pipeline.predict(X_test)
        metrics = evaluate_predictions(y_test, y_pred)
        
        print_evaluation_report(metrics, name)
        
        # Select best model based on F1-score
        if metrics['f1-score'] > best_f1:
            best_f1 = metrics['f1-score']
            best_model_name = name
            best_pipeline = pipeline
            best_metrics = metrics
            
    print("\n" + "=" * 60)
    print(f"BEST PERFORMING MODEL: {best_model_name} (F1-score: {best_f1:.4f})")
    print("=" * 60)
    
    # Save the best pipeline and its metadata
    os.makedirs("models", exist_ok=True)
    model_save_path = "models/career_model.joblib"
    
    # Save the training details
    model_artifact = {
        "pipeline": best_pipeline,
        "model_name": best_model_name,
        "metrics": best_metrics,
        "classes": best_pipeline.named_steps['classifier'].classes_.tolist()
    }
    
    joblib.dump(model_artifact, model_save_path)
    print(f"Saved best model pipeline to {model_save_path}")
    
    # Save processed data for record/EDA purposes
    os.makedirs("data", exist_ok=True)
    df_clean.to_csv("data/processed_data.csv", index=False)
    print("Saved processed data to data/processed_data.csv")

if __name__ == "__main__":
    train_and_select_model()
