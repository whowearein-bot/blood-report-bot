from flask import Flask, render_template, request
from openai import OpenAI
import re

app = Flask(__name__)

# Setup OpenAI client for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

# Clean unwanted tags like <think>
def clean_response(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

# Optional: filter obviously non-medical queries
def is_medical_query(text):
    keywords = [
        "blood", "sugar", "diabetes", "cholesterol", "report", "glucose", "hba1c",
        "hemoglobin", "cbc", "symptom", "fatigue", "vitamin", "bp", "pressure", "hdl", "ldl", "esr"
    ]
    return any(word in text.lower() for word in keywords)

@app.route('/', methods=['GET', 'POST'])
def index():
    response_text = ""
    if request.method == 'POST':
        user_input = request.form['prompt']
        
        # Optional filter
        if not is_medical_query(user_input):
            response_text = "❌ This assistant only responds to medical questions related to health and blood reports."
        else:
            try:
                completion = client.chat.completions.create(
                    model="deepseek/deepseek-r1-0528:free",
                    extra_headers={
                        "HTTP-Referer": "http://localhost:5000",
                        "X-Title": "MedicalReportAssistant"
                    },
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful and knowledgeable medical assistant. Only respond to questions "
                                "about health, blood reports, symptoms, and lab values like glucose, hemoglobin, etc. "
                                "If the user asks something unrelated, politely inform them that this assistant is only for health and medical use."
                            )
                        },
                        {"role": "user", "content": user_input}
                    ]
                )
                raw_text = completion.choices[0].message.content
                response_text = clean_response(raw_text)
            except Exception as e:
                response_text = f"❌ Error: {str(e)}"
    
    return render_template('index.html', response=response_text)

if __name__ == '__main__':
    app.run(debug=True)
