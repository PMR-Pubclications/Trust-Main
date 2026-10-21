# Initialize git in your local project folder (if not already done)
git init

# Link your local folder to your GitHub repository remote
git remote add origin https://github.com/Tole1775/Trust.git

# Stage all your files (including your asset/sh/opensea.sh and Python scripts)
git add .

# Commit your files with a descriptive message
git commit -m "Initial commit: Add OpenSea agent scripts and automation setup"

# Push your code up to GitHub on the main branch
git branch -M main
git push -u origin main
