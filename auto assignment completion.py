import re
import time
import math
import random
import webbrowser
import keyboard
import nltk
from groq import Groq 
from canvasapi import Canvas 

# --- USER INFO ---
STUDENT_NAME = "John Doe"
TEACHER_NAME = "Ms. Smith"
COURSE_NAME = "English"

# --- CONFIGURATION ---
CANVAS_URL = "https://mccsc.instructure.com"
CANVAS_KEY = "YOUR_CANVAS_API_KEY_HERE"  # Replace with your actual Canvas API key
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"  # Replace with your actual Groq API key
COURSE_ID = 00000  # Replace with your actual course ID

# --- FUNCTIONS ---
def clean_assignment_text(text):
    if not text: return ""
    text = re.sub('<[^<]+?>', '', text) 
    text = re.sub(r'\*\*|__', '', text) 
    text = re.sub(r'#+\s?', '', text)    
    return text.strip()

def finalize_essay_formatting(text):
    if not text: return ""
    
    # 1. Fix double single quotes ('' -> ")
    text = text.replace("''", '"')
    
    # 2. Replace dialogue single quotes with doubles, keep contractions
    # This looks for quotes at the start/end of words or sentences
    text = re.sub(r"(\s)'|^'", r'\1"', text) # Start of word/string
    text = re.sub(r"'(\s)|'$", r'"\1', text) # End of word/string
    
    # 3. Flatten into one block
    text = " ".join(text.splitlines())
    return re.sub(r'\s+', ' ', text).strip()

# --- EXECUTION ---
canvas = Canvas(CANVAS_URL, CANVAS_KEY)
client = Groq(api_key=GROQ_API_KEY)

try:
    print("Checking Canvas for work...")
    course = canvas.get_course(COURSE_ID)
    unsubmitted = [a for a in course.get_assignments() if a.due_at and a.get_submission('self').workflow_state == 'unsubmitted']
    
    if not unsubmitted:
        print("No work found!"); exit()

    most_urgent = min(unsubmitted, key=lambda a: a.due_at)
    print(f"Working on: {most_urgent.name}")
    
    print("AI generating (no-header mode)...")
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[
            {
                "role": "system", 
                "content": f"You are {STUDENT_NAME}. Write a natural student response. DO NOT include any header, title, or your name. Start immediately with the first sentence. Use ONE solid paragraph. Use standard double quotes for dialogue."
            },
            {
                "role": "user", 
                "content": f"Complete this assignment: {clean_assignment_text(most_urgent.description)}"
            }
        ]
    )
    
    # Process AI text
    raw_ai_text = completion.choices[0].message.content # Choice 0 to be safe
    essay_content = finalize_essay_formatting(raw_ai_text)
    tokens = nltk.word_tokenize(essay_content)

    # Prepare Header
    current_date = time.strftime("%B %d, %Y")
    header_to_type = f"{STUDENT_NAME}\n{TEACHER_NAME}\n{COURSE_NAME}\n{most_urgent.name}\n{current_date}\n\n\n"

    print("Opening Google Docs...")
    webbrowser.open("https://docs.new")
    time.sleep(10) 

    # --- RENAME ---
    keyboard.press_and_release('alt+/') 
    time.sleep(1.2)
    keyboard.write("Rename")
    time.sleep(0.8)
    keyboard.press_and_release('enter')
    time.sleep(0.8)
    keyboard.write(most_urgent.name)
    keyboard.press_and_release('enter')
    time.sleep(2.0)

    # --- TYPE HEADER ---
    keyboard.write(header_to_type)
    time.sleep(0.5)

    # --- TYPE ESSAY ---
    print("typing")
    start_time = time.time()
    for i, token in enumerate(tokens):
        if keyboard.is_pressed('esc'): 
            break

        wave_mult = 1.0 + 0.2 * math.sin((time.time() - start_time) / 40.0)
        
        # Fixing tokenized quotes: if nltk turned " into '', turn it back
        if token == "''" or token == "``":
            token = '"'

        for ch in token:
            keyboard.write(ch)
            time.sleep(random.uniform(0.06, 0.11) * wave_mult)

        if i < len(tokens) - 1:
            next_token = tokens[i+1]
            # Precise punctuation check
            if next_token not in [".", ",", "!", "?", ";", ":", '"', "n't", "'s"]:
                keyboard.write(" ")
        
        if token in ['.', '!', '?']:
            time.sleep(random.uniform(0.7, 1.3))

    print("assignment is ready.")

except Exception as e:
    print(f"Error: {e}")