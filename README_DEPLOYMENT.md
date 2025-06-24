# PropTech Intel - Replit Deployment Guide

This guide will help you deploy your PropTech Intel Flask application from GitHub to Replit.

## Step 1: Import from GitHub

1. **Create a new Repl in Replit**
   - Go to [Replit](https://replit.com)
   - Click "Create Repl"
   - Select "Import from GitHub"
   - Enter your repository URL: `https://github.com/dougshults/competitive-agent.git`
   - Click "Import from GitHub"

2. **Verify Files**
   After import, you should see your original project files plus these new configuration files:
   - `main.py` (modified for Replit)
   - `replit_config.py`
   - `.replit`
   - This README

## Step 2: Configure Environment Variables

1. **Set up Secrets in Replit**
   - Click on the "Secrets" tab in the left sidebar (lock icon)
   - Add the following secrets (replace with your actual values):

   ```
   SESSION_SECRET=your-secret-session-key-here
   OPENAI_API_KEY=your-openai-api-key
   ```

   Add any other API keys or sensitive configuration your app requires.

2. **Required Environment Variables**
   Make sure you have all the environment variables your original app needs:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `SESSION_SECRET` - Flask session secret key
   - Add others as needed based on your app's requirements

## Step 3: Install Dependencies

1. **Check requirements.txt**
   - Ensure your `requirements.txt` file is present and contains all necessary dependencies
   - Replit will automatically install these when you run the app

2. **Manual Installation (if needed)**
   If you need to manually install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Step 4: Run the Application

1. **Start the App**
   - Click the green "Run" button
   - Or run in the console: `python main.py`

2. **Access Your App**
   - Your app will be available at the URL shown in the Replit interface
   - It should be running on port 5000 and accessible externally

## Step 5: Troubleshooting

### Common Issues and Solutions

1. **Import Errors**
   - Check that all your original files were imported correctly
   - Verify that your main Flask app file is properly structured
   - Look at the console output for specific error messages

2. **Missing Dependencies**
   - Ensure `requirements.txt` is complete
   - Install missing packages: `pip install package-name`

3. **Environment Variable Issues**
   - Double-check that all secrets are set in Replit Secrets
   - Verify environment variable names match your app's expectations

4. **Static Files Not Loading**
   - Ensure your `static/` directory exists
   - Check that Flask is configured to serve static files
   - Verify file paths in your templates

5. **Template Errors**
   - Ensure your `templates/` directory exists
   - Check that template file names and paths are correct

### Debug Mode

The app runs in debug mode by default, so you'll see detailed error messages. Check the console output for any issues.

### File Structure

Your project should have a structure similar to:
