# Andikar AI - Manual Authentication Version

This is a variant of the original Andikar AI application that uses manual registration and authentication instead of Google OAuth. Users can register with username, email, password, and optional phone number.

## Features

- **Manual User Registration**: Create accounts with username, email, and password
- **Secure Password Handling**: Passwords are securely hashed and salted
- **User Profile Management**: Update email, phone, and password
- **MongoDB Integration**: User data is stored in MongoDB
- **Fallback Database**: In-memory storage when MongoDB is unavailable
- **Edge Browser Compatibility**: Special handling for Microsoft Edge
- **Text Humanization**: Uses the Andikar AI backend to humanize text

## Getting Started

### Prerequisites

- Python 3.9+
- MongoDB (or the fallback in-memory database will be used)

### Environment Variables

Set the following environment variables:

- `MONGODB_URI` - MongoDB connection string
- `SECRET_KEY` - Secret key for session security (optional)
- `PORT` - Port to run the application on (default: 5000)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```

## Deployment

The application can be deployed on Railway or any other platform that supports Python applications.

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Deploy the application

## API Integration

The application connects to the Andikar AI API for text humanization. The API provides:

- Text humanization
- Word count
- AI detection

## Differences from the Original Version

This version differs from the original Test-front-end in the following ways:

1. Uses manual registration instead of Google OAuth
2. Requires direct MongoDB configuration (no Google authentication)
3. Includes user profile management features
4. Has additional security features for password handling

## Support

For any issues or questions, please contact the Andikar AI team.
