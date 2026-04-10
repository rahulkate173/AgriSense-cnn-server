import groq
import os
import json
from config import GROQ_API_KEY, GROQ_MODEL

client = groq.Groq(api_key=GROQ_API_KEY)

def get_ai_feedback(class_label, confidence):
    """
    Sends the classification results to Groq to generate multilingual 
    explanation with recommendations.
    Returns structured response with English, Hindi, and Marathi.
    """
    if not GROQ_API_KEY:
        return {
            "english": "AI Feedback unavailable (missing API key).",
            "hindi": "AI प्रतिक्रिया उपलब्ध नहीं है (API कुंजी गायब है)।",
            "marathi": "AI प्रतिक्रिया उपलब्ध नहीं (API की गायब)।"
        }

    prompt = f"""
    Internal Classification Result: {class_label}
    Confidence: {confidence:.2f}

    As an agricultural expert, provide professional explanations EXACTLY in this JSON format ONLY:
    {{
        "english": "Brief explanation of the condition, recommended actions, and preventive measures",
        "hindi": "संक्षिप्त व्याख्या, अनुशंसित कार्रवाई और रोकथाम के उपाय",
        "marathi": "संक्षिप्त स्पष्टीकरण, शिफारस केलेल्या क्रिया आणि प्रतिबंधाचे उपाय"
    }}

    For each language:
    1. Brief explanation of what {class_label} is
    2. Immediate recommended actions or treatments
    3. Preventive measures
    4. Concise "what to do next"

    Return ONLY valid JSON, no additional text.
    """

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful agricultural AI assistant. Return ONLY valid JSON, no markdown or extra text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        
        response_text = completion.choices[0].message.content.strip()
        
        # Try to parse JSON response
        try:
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            parsed_response = json.loads(response_text.strip())
            
            # Ensure all keys are present
            return {
                "english": parsed_response.get("english", "Unable to generate feedback"),
                "hindi": parsed_response.get("hindi", "प्रतिक्रिया उत्पन्न करने में असमर्थ"),
                "marathi": parsed_response.get("marathi", "प्रतिक्रिया तयार करू शकत नाही")
            }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "english": response_text,
                "hindi": "प्रतिक्रिया उत्पन्न करने में असमर्थ",
                "marathi": "प्रतिक्रिया तयार करू शकत नाही"
            }
            
    except Exception as e:
        return {
            "english": f"Error generating AI feedback: {str(e)}",
            "hindi": f"AI प्रतिक्रिया उत्पन्न करने में त्रुटि: {str(e)}",
            "marathi": f"AI प्रतिक्रिया तयार करण्यात त्रुटी: {str(e)}"
        }
