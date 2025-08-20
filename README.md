# Breaders_Twilio_New

## WhatsApp Bot – Quick Start

### Requirements
- Python 3.8+
- pip (or pipenv)
- Twilio account (WhatsApp API credentials)
- [ngrok](https://ngrok.com/) (for local development)

### 1. Clone the Repository
```bash
git clone https://github.com/MatPizzolo/Breaders_Twilio_New.git
cd breaders_twilio_bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number
DJANGO_SECRET_KEY=your_secret_key
```

### 4. Apply Migrations
```bash
python manage.py migrate
```

### 5. Run the Bot Locally (with ngrok)
```bash
python run_dev.py
```
This will start Django and ngrok, exposing your local server to the internet.

### 6. Set Your Twilio WhatsApp Webhook
- Copy the forwarding URL from ngrok (e.g., `https://xxxx.ngrok.io/webhook/whatsapp/`)
- Set it as your WhatsApp webhook in the Twilio Console.

### 7. Start Chatting!
Send a WhatsApp message to your Twilio sandbox number to interact with the bot.

---

**For production deployment, use a real web server (e.g., Gunicorn + Nginx) and a cloud provider.**

For any issues, see the code or contact the project maintainer.

