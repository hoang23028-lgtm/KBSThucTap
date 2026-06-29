"""Huấn luyện Random Forest với hyperparameter tuning tối ưu."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.expert_system_v2 import ExpertSystem
from src.ml_model_v2 import MajorClassifier


def main():
    print("=" * 60)
    print("Training Random Forest Model with Hyperparameter Tuning")
    print("=" * 60)

    print("\n1. Tuning hyperparameters (RandomizedSearchCV)...")
    clf = MajorClassifier()
    
    # Tuning hyperparameters
    tune_result = clf.tune_hyperparameters(
        search_type="random",  # 'random' nhanh hơn, 'grid' chính xác hơn
        n_iter=20,  # số combinations để test
        cv_folds=5,
    )

    print(f"\n   Best Params: {tune_result['best_params']}")
    print(f"   Best CV F1-macro: {tune_result['best_cv_score']}")
    print(f"   Test Accuracy: {tune_result['test_accuracy']}")
    print(f"   Test F1-macro: {tune_result['test_f1_macro']}")

    # Lưu model
    model_path = clf.save()
    print(f"\n✓ Model saved: {model_path}")

    print("\n2. Initializing Expert System Rules (SQLite)...")
    expert = ExpertSystem()
    n_rules = len(expert.get_all_rules())
    print(f"   ✓ {n_rules} expert rules initialized")
    
    rules_db_path = expert.db_path
    print(f"   ✓ Rules database: {rules_db_path}")

    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print(f"\nNext: streamlit run app/main.py")


if __name__ == "__main__":
    main()
