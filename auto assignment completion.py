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
NUM_ASSIGNMENTS_TO_DO = 3 
COURSE_TO_DO = "ALL"  # Set to a specific ID (e.g. 12345) or "ALL"

# --- CONFIGURATION ---
CANVAS_URL = "https://YOUR_SCHOOL.instructure.com"
CANVAS_KEY = "YOUR_CANVAS_API_KEY_HERE"
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"

# --- SETUP ---
canvas = Canvas(CANVAS_URL, CANVAS_KEY)
client = Groq(api_key=GROQ_API_KEY)
completed_ids = []

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
        
        all_unsubmitted = []
        
        # Select Course(s)
        if COURSE_TO_DO == "ALL":
            courses = canvas.get_courses(enrollment_state='active')
        else:
            courses = [canvas.get_course(COURSE_TO_DO)]

        for course in courses:
            try:
                assignments = course.get_assignments()
                for a in assignments:
                    if a.due_at and a.get_submission('self').workflow_state == 'unsubmitted' and a.id not in completed_ids:
                        all_unsubmitted.append(a)
            except:
                continue

        if not all_unsubmitted:
            print("No more work found!")
            break

        most_urgent = min(all_unsubmitted, key=lambda a: a.due_at)
        completed_ids.append(most_urgent.id)
        
        print(f"Working on: {most_urgent.name}")
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are {STUDENT_NAME}. Write a natural student response. No header/title. One solid paragraph. Double quotes for dialogue."},
                {"role": "user", "content": f"Complete this: {clean_assignment_text(most_urgent.description)}"}
            ]
        )

        essay_content = finalize_essay_formatting(completion.choices[0].message.content)
        tokens = nltk.word_tokenize(essay_content)
        header = f"{STUDENT_NAME}\n{TEACHER_NAME}\n{COURSE_NAME}\n{most_urgent.name}\n{time.strftime('%B %d, %Y')}\n\n\n"

        webbrowser.open("https://docs.new")
        time.sleep(10)

        keyboard.press_and_release('alt+/')
        time.sleep(1.2)
        keyboard.write("Rename")
        time.sleep(0.8)
        keyboard.press_and_release('enter')
        time.sleep(0.8)
        keyboard.write(most_urgent.name)
        keyboard.press_and_release('enter')
        time.sleep(2.0)

        keyboard.write(header)
        start_time = time.time()
        
        for idx, token in enumerate(tokens):
            if keyboard.is_pressed('esc'):
                print("Aborted.")
                exit()

            wave_mult = 1.0 + 0.2 * math.sin((time.time() - start_time) / 40.0)
            if token in ["''", "``"]: token = '"'
            for ch in token:
                keyboard.write(ch)
                time.sleep(random.uniform(0.06, 0.11) * wave_mult)

            if idx < len(tokens) - 1:
                if tokens[idx+1] not in [".", ",", "!", "?", ";", ":", '"', "n't", "'s"]:
                    keyboard.write(" ")

            if token in ['.', '!', '?']:
                time.sleep(random.uniform(0.7, 1.3))

        print(f"Done: {most_urgent.name}")
        time.sleep(5)

    except Exception as e:
        print(f"Error: {e}")
        break

print("\nSession complete.")