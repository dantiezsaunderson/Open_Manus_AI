#!/usr/bin/env python3
"""
Deployment script for Open Manus AI

This script automates the deployment process for the Open Manus AI project.
It handles GitHub repository updates and triggers Render deployment.
"""

import os
import sys
import argparse
import subprocess
import requests
import time
from datetime import datetime

# GitHub credentials
GITHUB_USERNAME = "dantiezsaunderson"
GITHUB_TOKEN = "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"

# Render deploy hook
RENDER_DEPLOY_HOOK = "https://api.render.com/deploy/srv-cvl1m2a4d50c73e0pkdg?key=SjaQiBUV2cM"

# GitHub repository
GITHUB_REPO = "Open_Manus_AI"
GITHUB_REPO_URL = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}.git"

# Render application URL
RENDER_APP_URL = "https://open-manus-ai.onrender.com/"

def setup_argparse():
    """Set up command line argument parsing."""
    parser = argparse.ArgumentParser(description="Deploy Open Manus AI")
    parser.add_argument("--push-only", action="store_true", help="Only push to GitHub without deploying to Render")
    parser.add_argument("--deploy-only", action="store_true", help="Only deploy to Render without pushing to GitHub")
    parser.add_argument("--message", "-m", type=str, default=f"Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                        help="Commit message for GitHub")
    parser.add_argument("--branch", type=str, default="main", help="Branch to push to")
    return parser.parse_args()

def run_command(command, cwd=None):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            cwd=cwd,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error message: {e.stderr}")
        sys.exit(1)

def push_to_github(commit_message, branch):
    """Push changes to GitHub repository."""
    print("\n=== Pushing to GitHub ===")
    
    # Check if we're in the correct directory
    current_dir = os.getcwd()
    if not os.path.exists(os.path.join(current_dir, "src")) or not os.path.exists(os.path.join(current_dir, "README.md")):
        print("Error: Not in the Open Manus AI project directory.")
        print(f"Current directory: {current_dir}")
        sys.exit(1)
    
    # Configure Git credentials
    print("Configuring Git credentials...")
    run_command(f'git config --local credential.helper "store --file=.git/credentials"')
    with open(".git/credentials", "w") as f:
        f.write(f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com\n")
    
    # Check if the repository is already initialized
    if not os.path.exists(".git"):
        print("Initializing Git repository...")
        run_command("git init")
        run_command(f'git remote add origin https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO}.git')
    
    # Check if the remote exists
    remotes = run_command("git remote -v")
    if "origin" not in remotes:
        print("Adding remote origin...")
        run_command(f'git remote add origin https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO}.git')
    
    # Add all files
    print("Adding files to Git...")
    run_command("git add .")
    
    # Commit changes
    print(f"Committing changes with message: {commit_message}")
    run_command(f'git commit -m "{commit_message}"')
    
    # Push to GitHub
    print(f"Pushing to branch: {branch}")
    push_result = run_command(f"git push -u origin {branch}")
    print(push_result)
    
    # Clean up credentials
    if os.path.exists(".git/credentials"):
        os.remove(".git/credentials")
    
    print("Successfully pushed to GitHub!")
    return True

def deploy_to_render():
    """Deploy the application to Render."""
    print("\n=== Deploying to Render ===")
    
    # Trigger Render deployment
    print(f"Triggering deployment via webhook: {RENDER_DEPLOY_HOOK}")
    response = requests.post(RENDER_DEPLOY_HOOK)
    
    if response.status_code == 200:
        print("Deployment triggered successfully!")
        
        # Wait for deployment to complete
        print("Waiting for deployment to complete (this may take a few minutes)...")
        for i in range(12):  # Wait up to 2 minutes
            print(f"Checking deployment status... ({i+1}/12)")
            time.sleep(10)  # Wait 10 seconds between checks
            
            try:
                # Check if the application is responding
                check_response = requests.get(RENDER_APP_URL, timeout=5)
                if check_response.status_code == 200:
                    print(f"Deployment complete! Application is available at: {RENDER_APP_URL}")
                    return True
            except requests.RequestException:
                pass  # Continue waiting
        
        print(f"Deployment may still be in progress. Please check manually at: {RENDER_APP_URL}")
        return True
    else:
        print(f"Error triggering deployment. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def main():
    """Main function to handle deployment process."""
    args = setup_argparse()
    
    print("=== Open Manus AI Deployment ===")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = True
    
    # Push to GitHub if not deploy-only
    if not args.deploy_only:
        success = push_to_github(args.message, args.branch)
    
    # Deploy to Render if not push-only and GitHub push was successful
    if not args.push_only and success:
        success = deploy_to_render()
    
    if success:
        print("\n=== Deployment Process Complete ===")
        print(f"GitHub Repository: https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}")
        print(f"Deployed Application: {RENDER_APP_URL}")
    else:
        print("\n=== Deployment Process Failed ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
