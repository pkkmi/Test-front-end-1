# Railway Environment Variables

For proper deployment on Railway, set the following environment variables:

## Required Variables

| Variable     | Description                                    | Example                                  |
|--------------|------------------------------------------------|------------------------------------------|
| MONGODB_URI  | MongoDB connection string                      | mongodb+srv://user:pass@cluster.mongodb.net/andikar |
| SECRET_KEY   | Secret key for sessions (generate a random one)| a1b2c3d4e5f6g7h8i9j0                    |

## Optional Variables

| Variable | Description                      | Default   |
|----------|----------------------------------|-----------|
| PORT     | Port to run the application on   | 8080      |

## How to set up

1. Go to your Railway dashboard
2. Select your project
3. Click on the "Variables" tab
4. Add each variable with its corresponding value

## Notes

- **Security**: Keep your MongoDB connection string private
- **Performance**: The application will use an in-memory fallback database if MongoDB is not configured, but this is not recommended for production use.
- **Error Handling**: Check the logs if you encounter any issues with database connections

## Testing MongoDB Connection

To confirm your MongoDB connection is working:

1. Deploy your application after setting the variables
2. Visit `/debug` endpoint
3. Verify that the db_status field shows "Using MongoDB" instead of "Using fallback in-memory database"
