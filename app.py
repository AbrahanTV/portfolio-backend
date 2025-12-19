import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import BaseModel, EmailStr, Field, ValidationError
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
load_dotenv()

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

app = Flask(__name__)
origins_env = os.getenv("CORS_ORIGINS")
if origins_env:
    allowed_origins = [o.strip() for o in origins_env.split(",") if o.strip()]
else:
    allowed_origins = ["https://www.abrahantolentino.com/"]

CORS(app, origins=["https://www.abrahantolentino.com/"])



class ContactPayload(BaseModel):
    name: str = Field(
        strip_whitespace=True,
        min_length=1,
        max_length=100
    )
    email: EmailStr
    message: str = Field(
        strip_whitespace=True,
        min_length=1,
        max_length=5000
    )
    

def send_email(payload: ContactPayload) -> None:
    msg = EmailMessage()
    msg["Subject"] = f"New message from {payload.name}"
    msg["From"] = {payload.email}
    msg["To"] = "abrahantolentinov@gmail.com"

    msg.set_content(f"""
Name: {payload.name}
Email: {payload.email}

Message:
{payload.message}
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("abrahantolentinov@gmail.com", os.getenv("GMAIL_APP_PASSWORD"))
        server.send_message(msg)

@app.route('/api/contact', methods=['POST'])
def contact():
    payload = request.get_json()

    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid payload format"}), 400
    
    try:
        contact_data = ContactPayload(**payload)
    
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.errors()}), 400
    
    try:
        send_email(contact_data)
    except Exception as e:
        return jsonify({'error': 'Failed to send email', 'details': str(e)}), 500
    
    return jsonify({'message': 'Email sent successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)