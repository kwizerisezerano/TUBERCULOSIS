import os
import json
from app import app

def show_model_accuracy():
    """Display model accuracy from model_info.json"""
    model_info_path = os.path.join(os.path.dirname(__file__), "models", "model_info.json")
    
    if not os.path.exists(model_info_path):
        print("❌ model_info.json not found. Train the model first using:")
        print("   python bootstrap.py --runserver")
        return
    
    with open(model_info_path, "r") as f:
        results = json.load(f)
    
    print("\n" + "="*60)
    print("📊 MODEL ACCURACY REPORT")
    print("="*60)
    
    for model_name, model_data in results.items():
        if model_name == "reason":
            continue
            
        print(f"\n🔹 {model_name.upper()} MODEL")
        print("-" * 60)
        print(f"✅ Accuracy: {model_data.get('accuracy', 'N/A'):.2%}")
        print(f"📈 Total Samples: {model_data.get('n_samples', 'N/A')}")
        print(f"🏷️  Classes: {model_data.get('classes', [])}")
        
        class_counts = model_data.get('class_counts', {})
        if class_counts:
            print(f"\n📊 Class Distribution:")
            for cls, count in class_counts.items():
                print(f"   - {cls}: {count}")
        
        feature_importances = model_data.get('feature_importances', {})
        if feature_importances:
            print(f"\n🎯 Top 5 Feature Importances:")
            sorted_features = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)[:5]
            for feat, imp in sorted_features:
                print(f"   - {feat}: {imp}%")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    with app.app_context():
        show_model_accuracy()
