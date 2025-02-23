
# Reddit Auto-Responder Bot  

## Overview  
This Python-based bot automates responses to Reddit posts based on specified keywords. It uses a GUI interface for easy configuration and interacts with Reddit to fetch posts, identify questions, and reply as a **surgeon doctor**. All interactions are logged in a database for later review.  

## How It Works  

1. **Launching the Bot**  
   - Running the bot opens a small GUI window.  

2. **Input Options**  
   - Users can either:  
     - **Manually enter a list of keywords**.  
     - Click **"Get Keywords"** to fetch them from `keywords.txt`.  
   - Users can either:  
     - **Manually enter Reddit credentials (username & password)**.  
     - Click **"Get Credentials"** to fetch them from `credentials.txt`.  

3. **Starting the Bot**  
   - After providing the required inputs, clicking **"Start"** will:  
     - Log in to Reddit using the provided credentials.  
     - Fetch posts related to the given keywords.  
     - Identify posts that are **questions**.  
     - Automatically reply to those posts **as a surgeon doctor**.  
     - Save the post details and responses in a **database for later review**.  

## Features  
✅ **Automated Reddit Login** – Uses stored or manually entered credentials.  
✅ **Keyword-Based Post Search** – Fetches posts matching given keywords.  
✅ **Question Detection** – Analyzes posts to determine if they are questions.  
✅ **AI-Generated Replies** – Responds as a **surgeon doctor**.  
✅ **Database Logging** – Saves replies for later review.  

It needs to have an Open AI API key to work.....
