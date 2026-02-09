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
NUM_ASSIGNMENT = 3  # Set how many assignments to complete in one run

# --- CONFIGURATION ---
CANVAS_URL = "https://YOUR_SCHOOL.instructure.com"
CANVAS_KEY = "YOUR_CANVAS_API_KEY_HERE"
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"
COURSE_ID = 00000

# --- SETUP ---
canvas = Canvas(CANVAS_URL, CANVAS_KEY)
client = Groq(api_key=GROQ_API_KEY)
completed_ids = []  # Prevents repeating assignments not yet submitted

# --- FUNCTIONS ---
def clean_assignment_text(text):
    if not text: return ""
    text = re.sub('<[^<]+?>', '', text)
    text = re.sub(r'\*\*|__', '', text)
    text = re.sub(r'#+\s?', '', text)
    return text.strip()

def finalize_essay_formatting(text):
    if not text: return ""
    text = text.replace("''", '"')
    text = re.sub(r"(\s)'|^'", r'\1"', text)
    text = re.sub(r"'(\s)|'$", r'"\1', text)
    text = " ".join(text.splitlines())
    return re.sub(r'\s+', ' ', text).strip()

# --- MAIN LOOP ---
for i in range(NUM_ASSIGNMENTS_TO_DO):
    try:
        print(f"\n[Task {i+1}/{NUM_ASSIGNMENTS_TO_DO}] Checking Canvas...")
        course = canvas.get_course(COURSE_ID)
        
        # Filter for unsubmitted work excluding current session progress
        unsubmitted = [
            a for a in course.get_assignments() 
            if a.due_at and a.get_submission('self').workflow_state == 'unsubmitted'
            and a.id not in completed_ids
        ]

        if not unsubmitted:
            print("No more work found!")
            break

        most_urgent = min(unsubmitted, key=lambda a: a.due_at)
        completed_ids.append(most_urgent.id)
        
        print(f"Working on: {most_urgent.name}")
        
        # AI Generation
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": f"You are {STUDENT_NAME}. Write a natural student response. No header/title. One solid paragraph. Double quotes for dialogue."
                },
                {"role": "user", "content": f"Complete this: {clean_assignment_text(most_urgent.description)}"}
            ]
        )

        essay_content = finalize_essay_formatting(completion.choices[0].message.content)
        tokens = nltk.word_tokenize(essay_content)
        header = f"{STUDENT_NAME}\n{TEACHER_NAME}\n{COURSE_NAME}\n{most_urgent.name}\n{time.strftime('%B %d, %Y')}\n\n\n"

        # Automation
        webbrowser.open("https://docs.new")
        time.sleep(10)

        # Rename Doc
        keyboard.press_and_release('alt+/')
        time.sleep(1.2)
        keyboard.write("Rename")
        time.sleep(0.8)
        keyboard.press_and_release('enter')
        time.sleep(0.8)
        keyboard.write(most_urgent.name)
        keyboard.press_and_release('enter')
        time.sleep(2.0)

        # Type Content
        keyboard.write(header)
        start_time = time.time()
        
        for idx, token in enumerate(tokens):
            if keyboard.is_pressed('esc'):
                print("Aborted.")
                exit()

            wave_mult = 1.0 + 0.2 * math.sin((time.time() - start_time) / 40.0)
            
            # Fix tokenized quotes
            if token in ["''", "``"]: token = '"'

            for ch in token:
                keyboard.write(ch)
                time.sleep(random.uniform(0.06, 0.11) * wave_mult)

            # Space logic
            if idx < len(tokens) - 1:
                if tokens[idx+1] not in [".", ",", "!", "?", ";", ":", '"', "n't", "'s"]:
                    keyboard.write(" ")

            if token in ['.', '!', '?']:
                time.sleep(random.uniform(0.7, 1.3))

        print(f"Done: {most_urgent.name}")
        time.sleep(5) # Cooldown between tasks

    except Exception as e:
        print(f"Error on task {i+1}: {e}")
        break

print("\nSession complete.")