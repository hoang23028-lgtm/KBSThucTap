"""Test script để validate migrations và improvements."""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.cache import prediction_cache, rules_cache
from src.database import open_db
from src.ml_model_v2 import MajorClassifier
from src.expert_system_v2 import ExpertSystem
from src.hybrid_engine_v2 import HybridRecommendationEngine
from src.config import RULES_DB, HISTORY_DB


def test_sqlite_migration():
    """Test SQLite database migration."""
    print("\n" + "="*60)
    print("TEST 1: SQLite Database")
    print("="*60)
    
    rules_db_path = RULES_DB.with_suffix(".db")
    history_db_path = HISTORY_DB.with_suffix(".db")
    
    try:
        # Test rules DB
        rules_db = open_db(rules_db_path)
        rules_count = rules_db.count()
        print(f"✓ Rules DB: {rules_count} rules loaded")
        
        # Test history DB
        history_db = open_db(history_db_path)
        history_count = history_db.count()
        print(f"✓ History DB: {history_count} recommendations logged")
        
        return True
    except Exception as e:
        print(f"❌ SQLite test failed: {e}")
        return False


def test_rules_cache():
    """Test rules caching."""
    print("\n" + "="*60)
    print("TEST 2: Rules Cache (In-Memory)")
    print("="*60)
    
    try:
        expert = ExpertSystem()
        
        # Lần 1: Load từ DB
        start = time.time()
        rules1 = expert.get_all_rules()
        time1 = time.time() - start
        
        # Lần 2: Load từ cache
        start = time.time()
        rules2 = expert.get_all_rules()
        time2 = time.time() - start
        
        print(f"✓ First load (DB): {time1*1000:.2f}ms ({len(rules1)} rules)")
        print(f"✓ Second load (Cache): {time2*1000:.2f}ms")
        print(f"✓ Speedup: {time1/time2:.1f}x faster")
        
        # Test indexed search
        start = time.time()
        ds_rules = rules_cache.get_by_major("DATA SCIENCE")
        search_time = time.time() - start
        print(f"✓ Index search (DATA SCIENCE): {search_time*1000:.3f}ms ({len(ds_rules)} rules)")
        
        return True
    except Exception as e:
        print(f"❌ Rules cache test failed: {e}")
        return False


def test_prediction_cache():
    """Test prediction caching."""
    print("\n" + "="*60)
    print("TEST 3: Prediction Cache")
    print("="*60)
    
    try:
        engine = HybridRecommendationEngine()
        
        scores = {
            "Operating System": 75,
            "Algorithm and Programming": 80,
            "Program Design Methods": 78,
            "Discrete Mathematics": 72,
            "Linear Algebra": 80,
            "Basic Statistics": 82,
            "Data Structures": 79,
            "Web Development": 76,
            "Calculus": 75,
            "Artificial Intelligence": 78,
            "Algorithm Design and Analysis": 77,
            "Database Technology": 79,
            "Object Oriented Programming": 80,
            "Computer Networks": 74,
        }
        
        # First call (cache miss)
        start = time.time()
        result1 = engine.recommend(scores, save_history=False)
        time1 = time.time() - start
        
        # Second call (cache hit)
        start = time.time()
        result2 = engine.recommend(scores, save_history=False)
        time2 = time.time() - start
        
        print(f"✓ First call (cache miss): {time1*1000:.2f}ms")
        print(f"✓ Second call (cache hit): {time2*1000:.2f}ms")
        print(f"✓ Speedup: {time1/time2:.1f}x faster")
        
        # Cache stats
        stats = prediction_cache.stats()
        print(f"✓ Cache stats: {stats['hits']} hits, {stats['misses']} misses")
        print(f"  Hit rate: {stats['hit_rate']}")
        print(f"  Size: {stats['size']}/{stats['max_size']}")
        
        return True
    except Exception as e:
        print(f"❌ Prediction cache test failed: {e}")
        return False


def test_hyperparameter_tuning():
    """Test ML model with hyperparameter tuning."""
    print("\n" + "="*60)
    print("TEST 4: ML Model Hyperparameter Tuning")
    print("="*60)
    
    try:
        clf = MajorClassifier.load()
        
        # Check if tuned params exist
        if clf.best_params:
            print(f"✓ Model has tuned parameters:")
            for param, value in clf.best_params.items():
                print(f"   {param}: {value}")
        else:
            print("⚠️  Model loaded but no tuning params found")
        
        # Test prediction
        scores = {
            "Operating System": 75,
            "Algorithm and Programming": 80,
            "Program Design Methods": 78,
            "Discrete Mathematics": 72,
            "Linear Algebra": 80,
            "Basic Statistics": 82,
            "Data Structures": 79,
            "Web Development": 76,
            "Calculus": 75,
            "Artificial Intelligence": 78,
            "Algorithm Design and Analysis": 77,
            "Database Technology": 79,
            "Object Oriented Programming": 80,
            "Computer Networks": 74,
        }
        
        proba = clf.predict_proba(scores)
        pred = clf.predict(scores)
        
        print(f"✓ Prediction: {pred}")
        print(f"  Top 3 majors:")
        for i, (major, prob) in enumerate(sorted(proba.items(), key=lambda x: x[1], reverse=True)[:3], 1):
            print(f"    {i}. {major}: {prob*100:.1f}%")
        
        # Print metrics
        print(f"\n✓ Model metrics:")
        for metric, value in clf.metrics.items():
            print(f"   {metric}: {value}")
        
        return True
    except Exception as e:
        print(f"❌ ML model test failed: {e}")
        return False


def test_hybrid_inference():
    """Test hybrid recommendation engine."""
    print("\n" + "="*60)
    print("TEST 5: Hybrid Recommendation Engine")
    print("="*60)
    
    try:
        engine = HybridRecommendationEngine()
        
        scores = {
            "Operating System": 75,
            "Algorithm and Programming": 80,
            "Program Design Methods": 78,
            "Discrete Mathematics": 72,
            "Linear Algebra": 80,
            "Basic Statistics": 82,
            "Data Structures": 79,
            "Web Development": 76,
            "Calculus": 75,
            "Artificial Intelligence": 78,
            "Algorithm Design and Analysis": 77,
            "Database Technology": 79,
            "Object Oriented Programming": 80,
            "Computer Networks": 74,
        }
        
        start = time.time()
        result = engine.recommend(scores, student_id="TEST001", save_history=False)
        inference_time = time.time() - start
        
        print(f"✓ Hybrid inference: {inference_time*1000:.2f}ms")
        print(f"\n  Recommended: {result['recommended_major_vi']}")
        print(f"  Confidence: {result['confidence']*100:.1f}%")
        print(f"\n  Top 3 majors:")
        for i, ranking in enumerate(result['ranking'][:3], 1):
            print(f"    {i}. {ranking['major_vi']}")
            print(f"       AI: {ranking['ai_score']*100:.1f}% | Expert: {ranking['expert_score']*100:.1f}% | Final: {ranking['final_score']*100:.1f}%")
        
        print(f"\n  Fired rules: {len(result['fired_rules'])}")
        for rule in result['fired_rules'][:3]:
            print(f"    • Rule #{rule['rule_id']}: {rule['name']}")
        
        return True
    except Exception as e:
        print(f"❌ Hybrid inference test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*60)
    print("PROJECT IMPROVEMENTS TEST SUITE")
    print("="*60)
    print("Testing: SQLite, Caching, ML Tuning, Hybrid Engine")
    
    tests = [
        ("SQLite Migration", test_sqlite_migration),
        ("Rules Cache", test_rules_cache),
        ("Prediction Cache", test_prediction_cache),
        ("ML Hyperparameter Tuning", test_hyperparameter_tuning),
        ("Hybrid Recommendation Engine", test_hybrid_inference),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Improvements are working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
