import os

def query_gemini_waste_assistant(user_input, ml_prediction=None, mongo_context=None, api_key=None):
    """
    Get accurate waste segregation guidance from Google Gemini AI.
    
    :param user_input: The item or query from the user.
    :param ml_prediction: Prediction dict from Random Forest classifier (optional).
    :param mongo_context: Categories context from MongoDB (optional).
    :param api_key: Gemini API key string.
    :return: (success: bool, response_text: str, model_used: str)
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        return False, "No Gemini API Key provided.", "None"

    # Context formatting
    context_str = ""
    if mongo_context:
        cat_summaries = []
        for c in mongo_context[:10]: # Top categories summary
            c_name = c.get("category", "")
            c_desc = c.get("description", "")
            cat_summaries.append(f"- {c_name}: {c_desc}")
        context_str = "\n".join(cat_summaries)

    ml_info = ""
    if ml_prediction:
        ml_info = f"ML Classifier predicted category: '{ml_prediction.get('category')}' with confidence {ml_prediction.get('confidence')}%. Description: {ml_prediction.get('response')}"

    prompt = f"""You are an expert, highly accurate Waste Segregation & Environmental AI Assistant.
Your mission is to provide accurate, reliable, and actionable waste disposal instructions so users never misdispose of waste or follow incorrect advice.

--- DATABASE CONTEXT ---
{context_str or 'Standard waste categories: Organic/Compostable, Recyclable (Plastics, Paper, Glass, Metal), E-Waste, Hazardous, Medical/Sanitary, General Residual Waste.'}

--- ML PREDICTION CONTEXT ---
{ml_info or 'No ML prediction available.'}

--- USER QUERY ---
Item / Question: "{user_input}"

--- INSTRUCTIONS ---
1. Identify the exact waste item requested.
2. Determine its exact waste category (e.g. Organic, Recyclable Plastic/Glass/Metal, E-Waste, Hazardous, Medical/Sanitary, Landfill Waste).
3. Provide step-by-step instructions on how to properly clean, segregate, and dispose of it (e.g., bin color recommendations, drop-off centers, safety precautions).
4. Keep the response concise, clear, and easy to follow with bullet points and emojis.
5. If the item requires special handling (like lithium-ion batteries, fluorescent bulbs, electronics, chemicals), explicitly highlight safety precautions.
"""

    # Try google-genai SDK first
    try:
        from google import genai
        client = genai.Client(api_key=key)
        # Try gemini-2.5-flash or gemini-2.0-flash or gemini-1.5-flash
        for model_name in ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']:
            try:
                res = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if res and res.text:
                    return True, res.text.strip(), model_name
            except Exception:
                continue
    except ImportError:
        pass

    # Fallback to google.generativeai SDK
    try:
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=key)
        for model_name in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']:
            try:
                gmodel = genai_legacy.GenerativeModel(model_name)
                res = gmodel.generate_content(prompt)
                if res and res.text:
                    return True, res.text.strip(), model_name
            except Exception:
                continue
    except Exception as e:
        return False, f"Gemini API Error: {str(e)}", "Error"

    return False, "Failed to generate content from Gemini API with available models.", "Error"
