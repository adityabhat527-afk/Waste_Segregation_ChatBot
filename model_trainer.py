import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

WELL_INTENT_RESPONSES = [
    "You're welcome! 😊",
    "Glad to help!",
    "Anytime! Feel free to ask about other items.",
    "Happy to assist with waste segregation!"
]

FALLBACK_RESPONSES = [
    "Sorry, I couldn't understand that item.",
    "Can you rephrase or be more specific about the waste item?",
    "I'm not sure how to categorize this item. Try asking about a specific item like 'plastic bottle' or 'apple core'."
]

def train_model(categories_data):
    """
    Train TF-IDF + Random Forest model on categories data.
    
    :param categories_data: List of category dicts containing 'category', 'examples', 'description', and optional 'type'
    :return: (vectorizer, model, descriptions, types, metadata)
    """
    patterns = []
    tags = []
    descriptions = {}
    types = {}

    for category in categories_data:
        category_name = category.get("category", "").strip()
        if not category_name:
            continue

        examples = category.get("examples", [])
        for example in examples:
            if isinstance(example, str) and example.strip():
                patterns.append(example.strip().lower())
                tags.append(category_name)

        descriptions[category_name] = category.get("description", "No description available.")
        types[category_name] = category.get("type", "General Waste")

    if not patterns or not tags:
        raise ValueError("No valid training patterns found in the provided data.")

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(patterns)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, tags)

    metadata = {
        "num_categories": len(set(tags)),
        "num_patterns": len(patterns),
        "vocab_size": len(vectorizer.vocabulary_),
        "classes": list(model.classes_)
    }

    return vectorizer, model, descriptions, types, metadata

def predict_intent(vectorizer, model, descriptions, types, user_input, confidence_threshold=0.15):
    """
    Predict category and response for user input.
    """
    clean_input = user_input.strip().lower()
    if not clean_input:
        return {
            "category": "None",
            "response": "Please enter a waste item or question.",
            "confidence": 0.0
        }

    input_vec = vectorizer.transform([clean_input])

    try:
        probabilities = model.predict_proba(input_vec)[0]
        max_idx = probabilities.argmax()
        predicted_category = str(model.classes_[max_idx])
        confidence = float(probabilities[max_idx])

        # Check for gratitude / well intent
        if predicted_category == "WellIntent" or clean_input in ["thank you", "thanks", "thx", "thank u", "hi", "hello", "hey"]:
            return {
                "category": "WellIntent",
                "type": "Greeting / Gratitude",
                "response": random.choice(WELL_INTENT_RESPONSES),
                "confidence": max(confidence, 0.99)
            }

        if confidence < confidence_threshold:
            return {
                "category": "FallbackIntent",
                "type": "Unknown",
                "response": random.choice(FALLBACK_RESPONSES),
                "confidence": confidence
            }

        response_text = descriptions.get(predicted_category, "No description available.")
        waste_type = types.get(predicted_category, "General Waste")

        return {
            "category": predicted_category,
            "type": waste_type,
            "response": response_text,
            "confidence": round(confidence * 100, 1)
        }

    except Exception as e:
        return {
            "category": "Error",
            "type": "Error",
            "response": random.choice(FALLBACK_RESPONSES),
            "confidence": 0.0
        }
