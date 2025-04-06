# Test-front-end-1 Deployment Guide

This document provides guidance on deploying the Test-front-end-1 Flask application to Railway.

## Deployment Changes Made

The following changes were made to fix deployment issues:

1. **Modified MongoDB Connection in `backend/db.py`**:
   - Improved error handling for MongoDB connection failures
   - Properly defined client and db variables that can be imported by app.py
   - Prevented raising exceptions that would stop the application from falling back to in-memory database

2. **Updated Procfile**:
   - Now uses `wsgi:app` instead of `app:app` for better initialization
   - Properly binds to Railway's dynamic PORT environment variable
   - Added preload for better performance

3. **Added `wsgi.py`**:
   - Provides a proper WSGI entry point for the application
   - Includes proper logging for easier debugging
   - Has fallback for local development

4. **Added `railway.json`**:
   - Configures Railway to use Nixpacks builder
   - Sets proper start command
   - Configures restart policy

5. **Added `runtime.txt`**:
   - Explicitly specifies Python 3.9.18 for consistency with your development environment

## Deployment Steps

### Option 1: Automatic Deployment on Railway

1. Railway should automatically deploy when changes are pushed to the GitHub repository.
2. Check the deployment status in the Railway dashboard.
3. Once deployed, the application will be available at the URL provided by Railway.

### Option 2: Manual Deployment on Railway

If you need to manually deploy:

1. Install the Railway CLI:
   ```
   npm i -g @railway/cli
   ```

2. Login to Railway:
   ```
   railway login
   ```

3. Link your project:
   ```
   railway link
   ```

4. Deploy your application:
   ```
   railway up
   ```

## Environment Variables

Make sure to set the following environment variables in Railway:

- `PORT`: (Set automatically by Railway)
- `MONGODB_URI`: Your MongoDB connection string (if you want to use MongoDB)
- `SECRET_KEY`: A random string for Flask session security

## Troubleshooting

If you encounter issues with the deployment:

1. **Check Railway logs** for detailed error messages
2. **Verify environment variables** are set correctly
3. **Check MongoDB connectivity** if you're using MongoDB

Common issues:

- **Application failed to respond**: The application is not binding to the correct port
- **Module import error**: Missing modules in requirements.txt
- **MongoDB connection failure**: Incorrect MongoDB URI or network issues

## Backup Authentication

The application has a fallback in-memory database that works even when MongoDB is not available. It creates a demo user:

- Username: `demo`
- Password: `password`

## Testing the Deployment

Visit the application URL provided by Railway. The application should start up and show the login page.

To verify all functionality is working:

1. Log in with a test user
2. Try the humanize feature
3. Check the dashboard for user information
4. Try the profile management features
