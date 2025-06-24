#!/bin/bash
# Commands to push changes to GitHub
# Run these in the Replit Shell

# Remove git lock file
rm -f .git/index.lock

# Add your repository as the remote origin
git remote add origin https://github.com/dougshults/competitive-agent.git

# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Enhanced PropTech Intel with AI competitive analysis

- Implemented OpenAI-powered competitive intelligence analysis
- Added structured analysis output (NEW ORGANIZATIONS, PRODUCT LAUNCHES, etc.)
- Fixed SQLite database integration with caching for AI analysis
- Moved dashboard to root route for better UX
- Enhanced article scraping from multiple PropTech sources
- Added comprehensive error handling and logging
- Created .gitignore for proper version control"

# Push to GitHub
git push -u origin main