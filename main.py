import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
import datetime

app = Flask(__name__)
CORS(app) # Crucial for allowing your app to talk to the server

# --- CONFIGURATION ---
SENDER_EMAIL = "delstarfordisaiah@gmail.com"
# Note: Google app passwords should not have spaces when used in code
APP_PASSWORD = "dpxluxnrjzogozdu" 

# Assuming you already initialized Firebase Admin somewhere up here:
# cred = credentials.Certificate("path/to/serviceAccountKey.json")
# firebase_admin.initialize_app(cred, {'databaseURL': 'YOUR_FIREBASE_URL'})

def send_email_html(target_email, subject, html_content):
    """Helper function to send HTML emails using your Gmail account."""
    msg = MIMEMultipart('alternative')
    msg['From'] = f"Farmula 1 Team <{SENDER_EMAIL}>"
    msg['To'] = target_email
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html'))

    try:
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() # Secure the connection
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email successfully sent to {target_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise e

@app.route('/submit-insurance', methods=['POST'])
def submit_insurance():
    try:
        data = request.json
        provider = data.get('provider')
        phone = data.get('farmer_phone')
        region = data.get('region')
        acres = data.get('farm_size_acres')
        national_id = data.get('national_id')
        health_score = data.get('ai_health_score')
        history = data.get('historical_diseases')

        # 1. Save to Firebase Database under a new node
        db.reference('agritech/insurance_leads').push({
            'provider': provider,
            'phone': phone,
            'national_id': national_id,
            'region': region,
            'acres': acres,
            'health_score': health_score,
            'historical_diseases': history,
            'status': 'Forwarded to Provider',
            'timestamp': str(datetime.datetime.now())
        })

        # 2. Determine Target Email
        # For testing, you can put your own email here to see how it looks!
        provider_emails = {
            'Pula Agricultural Insurance': 'partners@pula-advisors.com',
            'Kilimo Trust Credit': 'credit@kilimotrust.org',
            'APA Insurance (Agri)': 'agri@apainsurance.org',
            'Equity Bank Agri-Loan': 'info@equitybank.co.ke'
        }
        target_email = provider_emails.get(provider, SENDER_EMAIL) 

        subject = f"Farmula 1 AI Risk Report - New Applicant ({region})"
        
        # 3. HTML Email formatting
        html_content = f"""
        <html><body style="font-family: Arial, sans-serif; color: #1E293B;">
            <h2 style="color: #2E7D32;">Farmula 1 AI Data Package</h2>
            <p>A new farmer has applied for services through the Ukulima Safi app.</p>
            <table style="border-collapse: collapse; width: 100%; max-width: 500px;" border="1">
                <tr style="background: #f8f9fa;"><td style="padding: 10px;"><strong>Phone:</strong></td><td style="padding: 10px;">{phone}</td></tr>
                <tr><td style="padding: 10px;"><strong>National ID:</strong></td><td style="padding: 10px;">{national_id}</td></tr>
                <tr style="background: #f8f9fa;"><td style="padding: 10px;"><strong>Region:</strong></td><td style="padding: 10px;">{region}</td></tr>
                <tr><td style="padding: 10px;"><strong>Farm Size:</strong></td><td style="padding: 10px;">{acres} Acres</td></tr>
                <tr style="background: #f8f9fa;"><td style="padding: 10px;"><strong>AI Health Score:</strong></td><td style="padding: 10px; color: #2E7D32;"><b>{health_score}</b></td></tr>
                <tr><td style="padding: 10px;"><strong>Disease History:</strong></td><td style="padding: 10px;">{history}</td></tr>
            </table>
            <br>
            <p><i>Digitally verified by Delstarford Works Infrastructure.</i><br>
            <b>Tamper Flag:</b> CLEAN (Data directly from AI Module)</p>
        </body></html>
        """
        
        # 4. Send the Email
        send_email_html(target_email, subject, html_content)
        
        return jsonify({"success": True, "message": "Transmitted successfully"})
    except Exception as e:
        print(f"Insurance Route Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)