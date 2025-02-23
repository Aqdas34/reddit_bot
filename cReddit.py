import tkinter as tk
from tkinter import messagebox
import csv
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
import customtkinter as ctk
import os
import socket
import random

def is_internet_connected():
    try:
        # Try to connect to a public DNS server (Google's DNS server in this case)
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False


posts_replied = []
def fetch_posts_replied():
    global posts_replied
    url = "https://drgopal.webncodes.site/gopal/fetch_posts_replied.php"
    try:
        response = requests.get(url)
        response.raise_for_status()  
        posts_replied = [item['link'] for item in response.json()]
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
def send_post_replied(link):

    url = "https://drgopal.webncodes.site/gopal/insert_post_replied.php"
    payload = {
        "link": link
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
        data = response.json()  # Parse response as JSON
        print(data)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
def call_php_api(api_url, data):
    data["gpt_response"] = clean_gpt_response(data["gpt_response"])
    
    try:
        # Send the POST request to the PHP API with JSON data
        response = requests.post(api_url, json=data)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Return the JSON response from the API
            return response.json()
        else:
            error_label.configure(text=f"Failed to connect to API", text_color="red")
            return {"status": "error", "message": f"Failed to connect to API, status code: {response.status_code}"}
    
    except requests.exceptions.RequestException as e:
        # Handle any request exceptions (e.g., network errors)
        error_label.configure(text= "network issue", text_color="red")
        return {"status": "error", "message": str(e)}

# 

def get_all_responses():
    url = "http://drgopal.webncodes.site/gopal/fetch_responses.php"

    try:
        # Make the GET request
        response = requests.get(url)

        # Check if the request was successful
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Print the data
        print(data)
        return data

    except requests.exceptions.RequestException as e:
        error_label.configure(text="network issue", text_color="red")
        # Print the error
        print(f"An error occurred: {e}")



# Function to disapprove an item
def disapprove_item(item_id):
    url = 'http://drgopal.webncodes.site/gopal/disapprove.php'  # Change to the actual path of your disapprove.php file
    try:
        # Send a POST request to the API
        response = requests.post(url, data={'id': item_id})

        # Check the response
        if response.status_code == 200:
            result = response.json()  # Parse the JSON response
            if 'success' in result:
                print(f"Success: {result['success']}")
            elif 'error' in result:
                print(f"Error: {result['error']}")
        else:
            print(f"Failed to disapprove item. HTTP Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        error_label.configure(text=f"Failed to connect to API", text_color="red")

        print(f"An error occurred: {e}")


# Create a threading event to control posting
post_event = threading.Event()

def login_to_reddit(driver, username, password):
    try:
        driver.get('https://www.reddit.com/login/')
        wait = WebDriverWait(driver, 5)
        
        username_field = wait.until(EC.visibility_of_element_located((By.ID, 'login-username')))
        username_field.send_keys(username)
        time.sleep(2)
        
        password_field = wait.until(EC.visibility_of_element_located((By.ID, 'login-password')))
        password_field.send_keys(password)
        time.sleep(2)
        # time.sleep(20)
        # time.sleep(3)

        # JavaScript to access shadow DOM and locate login button
        js_script = """
        return document.querySelector('shreddit-overlay-display').shadowRoot
        .querySelector('shreddit-signup-drawer').shadowRoot
        .querySelector('shreddit-slotter').shadowRoot
        .querySelector('button.login');
        """
        
        login_button = driver.execute_script(js_script)
        login_button.click()
        error_label.configure(text="Logged in successfully!", text_color="green")
        # print("Logged in successfully!")
        time.sleep(10)
    except Exception as e:
        error_label.configure(text="Login Unsuccessfull", text_color="red")
        

def ask_gpt(title, content):

    key = ''  # Replace with your OpenAI API key
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }

    # prompt = f"Title: {title}\nContent: {content}\nIs this a question? If yes, provide a response as a liposuction surgeon."
    prompt = (
        "As a professional liposuction surgeon, Please analyze the information provided and respond in a friendly, conversational tone. "
        "Consider the patient's perspective, and offer helpful advice or explanations that reflect compassion and professionalism. If this is a question, please provide a thorough and empathetic response."
        f"This is patient question's Title: \"{title}\"\n"
        f"This is Content: \"{content}\"\n\n"
      
    )
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json={
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': random.randint(100,150)
        }
    )
    
    if response.status_code == 200:
        answer = response.json()['choices'][0]['message']['content']
        return answer.strip()
    else:
        # print(f"Error from GPT API: {response.status_code} - {response.text}")
        error_label.configure(text=f"Error from GPT API", text_color="red")
        return None


def clean_gpt_response(response):
    # Replace common escape characters with empty strings
    cleaned_response = response.replace('\n', '') \
                               .replace('\t', '') \
                               .replace('\\', '') \
                               .replace('\r', '') # Handles carriage return if needed
    return cleaned_response


def post_gpt_response(driver, gpt_response,link):
    try:
        gpt_response = clean_gpt_response(gpt_response)
        # Wait for the comment box to be visible and click on it to focus
        time.sleep(2)
        comment_box_xpath = "/html/body/shreddit-app/div/div[1]/div/main/shreddit-async-loader/comment-body-header/shreddit-async-loader[1]/comment-composer-host/faceplate-tracker[1]/button"
        
        # Locate the comment box (clickable area)
        comment_box = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, comment_box_xpath))
        )
        time.sleep(2)

        # Type the GPT response into the comment box
        comment_box.send_keys(gpt_response)
        print("GPT response pasted into the comment box.")
        time.sleep(2)
        
        # Optionally, submit the comment by clicking the submit button
        submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
        )
        submit_button.click()  # Submit the comment
        time.sleep(1)

        send_post_replied(link)
        posts_replied.append(link)
    
        print("Comment posted successfully.")
    except Exception as e:
        print(f"Error posting comment: {e}")
        error_label.configure(text=f"Error posting comment", text_color="red")

        pass

def evaluate_gpt_accuracy(title,post_content, gpt_response):
    if not post_content or not gpt_response or post_content.strip() == '' or gpt_response.strip() == '':
        return 0
    
    prompt = f"As a professional liposuction surgeon, Please analyze the information provided and respond in a friendly, conversational tone. Consider the patient's perspective, and offer helpful advice or explanations that reflect compassion and professionalism. If this is a question, please provide a thorough and empathetic response.This is patient question's Title: \"{title}\"\nThis is Content: \"{post_content}\"\n\n"
      

    # api_key = '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'  # Replace with your OpenAI API key
    api_key = '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'  # Replace with your OpenAI API key
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    
    new_prompt =  f"{prompt}\n\n This is the response I provided to chatgpt \n\n\n {gpt_response}\n\n and this was response given by the chatgpt. can ypu tell me its accuracy. only give me a one number word response in percentage without the percentage sign"     
    
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json={
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': new_prompt}],
            'max_tokens': random.randint(100,150)
        }
    )
    
    if response.status_code == 200:
        answer = response.json()['choices'][0]['message']['content']
        print(answer)
        return answer.strip()
    else:
        # print(f"Error from GPT API: {response.status_code} - {response.text}")
        error_label.configure(text=f"Error from GPT API", text_color="red")
        return None
    


    # # Create a TF-IDF Vectorizer to convert the text into vector form
    # vectorizer = TfidfVectorizer().fit_transform([prompt, gpt_response])
    # vectors = vectorizer.toarray()
    
    # # Compute cosine similarity between the post content and GPT response
    # similarity = cosine_similarity([vectors[0]], [vectors[1]])[0][0]

    # # Convert similarity into a percentage
    # accuracy_percentage = similarity * 100
    # return round(accuracy_percentage, 2)



def start_previous_button(email, password,posts):
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        # Log in to Reddit
        login_to_reddit(driver, email, password)
        
        for post in posts:
            if post["post_link"] in posts_replied:
                print("post already replied")
                continue
            time.sleep(3)
            driver.get(post["post_link"])
            time.sleep(2)
            if post["approved"] == 1:
                post_gpt_response(driver, post["gpt_response"],post["post_link"])
                # disapprove_item(post["id"])
    except Exception as e:
        error_label.configure(text=f"Error", text_color="red")




def start_posting(email, password, keywords):
    global post_event
    driver = webdriver.Chrome()
    driver.maximize_window()

    # Log in to Reddit
    login_to_reddit(driver, email, password)

    # Define the list of search keywords
    search_keywords = keywords

    # Prepare CSV files for storing results and failed posts
    csv_file = 'liposuction_post_details_with_gpt_accuracy.csv'
    failed_posts_file = 'failed_liposuction_posts.csv'

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file, \
        open(failed_posts_file, mode='w', newline='', encoding='utf-8') as failed_file:
        
        writer = csv.writer(file)
        failed_writer = csv.writer(failed_file)
        
        writer.writerow(['Keyword', 'Title', 'Link', 'Content', 'GPT Response', 'Accuracy Percentage'])
        failed_writer.writerow(['Keyword', 'Title', 'Link', 'Error'])

        # Iterate over each keyword
        for search_keyword in search_keywords:
            if not post_event.is_set():  # Check if posting should stop
                break

            search_url = f"https://www.reddit.com/search/?q={search_keyword}&type=link"
            driver.get(search_url)

            # Collect post details for each keyword
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, '//a[@data-testid="post-title"]'))
            )
            post_details = []

            anchor_tags = driver.find_elements(By.XPATH, '//a[@data-testid="post-title"]')
            for tag in anchor_tags:
                href = tag.get_attribute('href')
                title = tag.text
                post_details.append((title, href))

            # Process each post
            for title, link in post_details:
                if not post_event.is_set():  # Check if posting should stop
                    break

                if link in posts_replied:
                    print("post already replied")
                    continue

                driver.get(link)
                time.sleep(3)
                
                try:
                    content_divs = driver.find_elements(By.CLASS_NAME, 'text-neutral-content')
                    content = "".join([para.text for div in content_divs for para in div.find_elements(By.TAG_NAME, 'p')])
                    
                    if content:
                        gpt_response = ask_gpt(title, content)
                        time.sleep(3)
                    
                        if gpt_response:
                            # Evaluate the GPT response accuracy
                            accuracy_percentage = evaluate_gpt_accuracy(title,content, gpt_response)
                            print(f"Accuracy: {accuracy_percentage}%")

                            accuracy_percentage = float(accuracy_percentage)

                            if True:
                                print("Called")

                                api_url = "https://drgopal.webncodes.site/gopal/api.php"
                                approved = 1
                                if(accuracy_percentage < 80):
                                    approved = 0
                                data = {
                                    "keyword":search_keyword,
                                    "post_link": link,
                                    "gpt_response": gpt_response,
                                    "accuracy": float(accuracy_percentage),
                                    "approved": approved


                                    }
                                print(f"{search_keyword} {link} {gpt_response} {accuracy_percentage}")

                                # result = insert_keyword_response(search_keyword,link,gpt_response,float(accuracy_percentage))
                                # result = insert_keyword_response(search_keyword,link,gpt_response,float(accuracy_percentage))
                                result = call_php_api(api_url,data)
                                if result:
                                    print(result)
                                else:
                                    print("None")


                            # if accuracy_percentage >= 80:
                            post_gpt_response(driver, gpt_response,link)
                            
                            # Write the post details and GPT response along with accuracy percentage to CSV
                            writer.writerow([search_keyword, title, link, content, gpt_response, accuracy_percentage])

                        else:
                            raise Exception("GPT response is empty")
                    else:
                        raise Exception("Content extraction failed")

                except Exception as e:
                    print(f"Error processing post {link}: {e}")
                    error_label.configure(text=f"Error processing post {link}", text_color="red")
                    failed_writer.writerow([search_keyword, title, link, str(e)])
                    failed_file.flush()  # Ensure data is written to the file after every failed post

    # Close the browser
    driver.quit()

def start_posting_thread(email, password, keywords):
    """Threaded function to start posting without blocking the GUI."""
    post_event.set()  # Allow posting to proceed
    start_posting(email, password, keywords)

def on_submit():
    global email
    global password
    global keywords_list

    email = email_entry.get()
    password = password_entry.get()
    keywords = keywords_entry.get()
    
    # Check if all fields are filled
    if not email or not password or not keywords:
        messagebox.showwarning("Input Error", "Please fill out all fields.")
        return
    
    # Convert the comma-separated keywords into a list
    keywords_list = [keyword.strip() for keyword in keywords.split(',')]


    if not is_internet_connected():
        error_label.configure(text="Not Connected with internet", text_color="red")
        return

    # Start the posting thread
    posting_thread = threading.Thread(target=start_posting_thread, args=(email, password, keywords_list))
    posting_thread.start()

def on_close():
    global post_event
    post_event.clear()  # Stop posting
    root.destroy()  # Close the Tkinter window



def previous_post():
    fetch_all_pending_posts = get_all_responses()


    global email
    global password
    global keywords_list

    email = email_entry.get()
    password = password_entry.get()
    keywords = keywords_entry.get()
    
    # Check if all fields are filled
    if not email or not password or not keywords:
        messagebox.showwarning("Input Error", "Please fill out all fields.")
        return
    if not is_internet_connected():
        error_label.configure(text="Not Connected with internet", text_color="red")
    start_previous_button(email,password,fetch_all_pending_posts)

def get_credentials():
    try:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_directory,"credentials.txt")
        with open(file_path, "r") as file:
            lines = file.readlines()
            email_entry.delete(0, tk.END)  # Clear the existing email
            email_entry.insert(0, lines[0].strip())  # Insert email from file
            password_entry.delete(0, tk.END)  # Clear the existing password
            password_entry.insert(0, lines[1].strip())  # Insert password from file
    except FileNotFoundError:
        messagebox.showerror("File Not Found", "The file 'credentials.txt' was not found.\n" + os.path.abspath(__file__))
    except IndexError:
        messagebox.showerror("Error", "Invalid format in 'credentials.txt'. Expected email on line 1, password on line 2.")

# Function to get keywords from the keywords.txt file
def get_keywords():
    try:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_directory,"keywords.txt")
        with open(file_path, "r") as file:
            keywords = file.read().strip()  # Read all keywords from the file
            keywords_entry.delete(0, tk.END)  # Clear the existing keywords
            keywords_entry.insert(0, keywords)  # Insert keywords from file
    except FileNotFoundError:
        messagebox.showerror("File Not Found", "The file 'keywords.txt' was not found.")




fetch_posts_replied()
# Create the main window
ctk.set_appearance_mode("light")  # Options: "light", "dark"
ctk.set_default_color_theme("blue")  # You can change this to any available theme

root = ctk.CTk()
root.title("Reddit Keyword Tool")
root.geometry("500x600")
root.resizable(False, False)

# Style settings
label_font = ("Helvetica", 12, "bold")

error_label = ctk.CTkLabel(root, text="Welcome Gopal!", text_color="green", wraplength=350)
error_label.pack(pady=20)

# Frame for email and password
credentials_frame = ctk.CTkFrame(root)
credentials_frame.pack(pady=25)

# Create and place the Email Label and Entry
email_label = ctk.CTkLabel(credentials_frame, text="Email:", font=label_font)
email_label.grid(row=0, column=0, sticky="e")
email_entry = ctk.CTkEntry(credentials_frame, width=350)
email_entry.grid(row=0, column=1, padx=10,pady=10)

# Create and place the Password Label and Entry
password_label = ctk.CTkLabel(credentials_frame, text="Password:", font=label_font)
password_label.grid(row=1, column=0,padx=10, sticky="e")
password_entry = ctk.CTkEntry(credentials_frame, show="*", width=350)
password_entry.grid(row=1, column=1,padx=10, pady=10)

# Frame for keywords
keywords_frame = ctk.CTkFrame(root)
keywords_frame.pack(pady=15)

# Create and place the Keywords Label and Entry
keywords_label = ctk.CTkLabel(keywords_frame, text="Keywords (comma-separated):", font=label_font)
keywords_label.grid(row=0, column=0, columnspan=2)
keywords_entry = ctk.CTkEntry(keywords_frame, width=350)
keywords_entry.grid(row=1, column=0, columnspan=2, padx=10,pady=10)

# Button Frame for better alignment
button_frame = ctk.CTkFrame(root)
button_frame.pack(pady=15)

# Create and place the buttons with custom styles
get_credentials_button = ctk.CTkButton(button_frame, text="Get Credentials", command=get_credentials)
get_credentials_button.grid(row=0, column=0, sticky="ew",padx=10, pady=10)

get_keywords_button = ctk.CTkButton(button_frame, text="Get Keywords", command=get_keywords)
get_keywords_button.grid(row=1, column=0, sticky="ew",padx=10, pady=10)

submit_button = ctk.CTkButton(button_frame, text="Start Posting", command=on_submit)
submit_button.grid(row=2, column=0, sticky="ew",padx=10, pady=10)

previous_post_button = ctk.CTkButton(button_frame, text="Start Previous Pending Posting", command=previous_post)
previous_post_button.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

# Handle window close event
root.protocol("WM_DELETE_WINDOW", on_close)

# Start the GUI event loop
root.mainloop()
