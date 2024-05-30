Sure! Here's an improved and more detailed GitHub repository description for your Django Ninja API project:

---

# Eyelhearn - Fast Backend API with Django Ninja

Eyelhearn is a modern and efficient backend API built using Django Ninja for high performance. This project features JWT token authentication, Amazon Polly for text-to-speech functionality, and Whisper for transcribing audio commands, enabling seamless voice navigation through the app.

## Key Features

- **High-Performance Backend**: Utilizes Django Ninja for a fast and efficient API backend.
- **JWT Authentication**: Secures API endpoints with JSON Web Token (JWT) authentication.
- **Amazon Polly Integration**: Converts text to natural-sounding speech using Amazon Polly.
- **Whisper Integration**: Transcribes voice commands from the client side for app navigation.

## Technologies Used

- **Django Ninja**: A fast web framework for building APIs with Django and Pydantic.
- **JWT**: JSON Web Token for secure authentication and authorization.
- **Amazon Polly**: AWS service that turns text into lifelike speech.
- **Whisper**: OpenAI's powerful speech recognition system to transcribe audio.

## Getting Started

### Prerequisites

- Python 3.8+
- Django
- AWS credentials for Amazon Polly
- OpenAI API key for Whisper

### Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/pexwave/eyelhearn.git
    cd eyelhearn
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up Environment Variables**:
    Create a `.env` file and add your AWS and OpenAI credentials:
    ```env
    AWS_ACCESS_KEY_ID=your_aws_access_key_id
    AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
    ```

4. **Run Migrations**:
    ```bash
    python manage.py migrate
    ```

5. **Start the Server**:
    ```bash
    python manage.py runserver
    ```

## Usage

- **Authentication**: Obtain a JWT token by authenticating with the API. Use this token to access protected endpoints.
- **Text-to-Speech**: Send text to the API, which utilizes Amazon Polly to convert it to speech.
- **Voice Commands**: Use Whisper to transcribe voice commands sent from the client, allowing navigation through the app.


---

