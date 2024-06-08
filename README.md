# StreamSMS Project

StreamSMS is a Django-based project designed to receive SMS messages sent to specific phone numbers and manage those messages via a moderation interface. Approved messages are then published via an RSS feed which can be used in OBS or vMix scrollers. This is a hobby project that could potentially scale to production if successful.

## Features
- **Receive SMS**: Integrates with Africa's Talking API to receive SMS messages.
- **Moderation Interface**: Provides a web interface to moderate incoming messages.
- **RSS Feed**: Generates an RSS feed for approved messages.
- **User Authentication**: Includes user login for secure access to the moderation interface.

## Prerequisites
- Python 3.x
- Django
- MySQL
- Africa's Talking API credentials

## Setup Instructions

1. **Clone the Repository**
    ```sh
    git clone https://github.com/yourusername/StreamSMS.git
    cd StreamSMS
    ```

2. **Create a Virtual Environment and Activate It**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the Required Packages**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**

    Copy and rename `.env.default` to `.env` file in the project root directory.

5. **Set Up the Database**
    ```sh
    python manage.py migrate
    ```

6. **Create a Superuser**
    ```sh
    python manage.py createsuperuser
    ```

7. **Run the Development Server**
    ```sh
    python manage.py runserver
    ```

8. **Set Up ngrok for Local Testing**
    ```sh
    ngrok http 8000
    ```
    Copy the ngrok URL and add it to your `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in the `.env` file.

9. **Configure Africa's Talking Webhook**
    - Set the webhook URL in the Africa's Talking dashboard to your ngrok URL (e.g., `http://your-ngrok-url.ngrok-free.app/africastalking-webhook/`).


## Populate Database with Dummy Data

To populate the database with dummy data for testing purposes, run the following script:
```sh
python manage.py populate_db
```

### Using Africa's Talking API
The project integrates with Africa's Talking API to receive SMS messages. Ensure you have your Africa's Talking credentials set in the .env file and the webhook URL configured in the Africa's Talking dashboard.

## Moderation Interface
Access the moderation interface at `/messages/moderate/` to view, approve, or decline messages. Approved messages will be available in the RSS feed.

## RSS Feed
Access the RSS feed of approved messages at `/messages/rss/`.

## Conclusion
StreamSMS is designed to streamline the process of receiving, moderating, and displaying SMS messages in a convenient and efficient manner. Contributions and feedback are welcome.

