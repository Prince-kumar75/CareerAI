from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import pandas as pd
import numpy as np

def evaluate_predictions(y_true, y_pred):
    """
    Evaluates predictions and returns accuracy, precision, recall, f1, and confusion matrix.
    """
    accuracy = accuracy_score(y_true, y_pred)
    
    # Calculate macro precision, recall, f1
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='macro', zero_division=0)
    
    # Detailed report per class
    classes = sorted(list(set(y_true) | set(y_pred)))
    prec_class, rec_class, f1_class, support = precision_recall_fscore_support(y_true, y_pred, labels=classes, zero_division=0)
    
    class_report = {}
    for idx, cls in enumerate(classes):
        class_report[cls] = {
            "precision": float(prec_class[idx]),
            "recall": float(rec_class[idx]),
            "f1-score": float(f1_class[idx]),
            "support": int(support[idx])
        }
        
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    
    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1-score": float(f1),
        "class_report": class_report,
        "confusion_matrix": cm.tolist(),
        "classes": classes
    }

def print_evaluation_report(metrics: dict, model_name: str):
    """
    Formats and prints the evaluation report.
    """
    print("=" * 60)
    print(f" EVALUATION REPORT FOR: {model_name} ")
    print("=" * 60)
    print(f"Overall Accuracy : {metrics['accuracy']:.4f}")
    print(f"Macro Precision  : {metrics['precision']:.4f}")
    print(f"Macro Recall     : {metrics['recall']:.4f}")
    print(f"Macro F1-Score   : {metrics['f1-score']:.4f}")
    print("-" * 60)
    print(f"{'Career Role':<30} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
    print("-" * 60)
    for cls, cl_metrics in metrics['class_report'].items():
        print(f"{cls:<30} | {cl_metrics['precision']:.4f}     | {cl_metrics['recall']:.4f}  | {cl_metrics['f1-score']:.4f}")
    print("=" * 60)
