import os
import random
from PIL import Image, ImageDraw, ImageFont
import imageio

W, H = 600, 320
BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#111111"
HEADER_COLOR = "#888888"
LINE_COLOR = "#E0E0E0"
HIGHLIGHT_COLOR = "#0055FF"

try:
    font_main = ImageFont.truetype("arial.ttf", 16)
    font_bold = ImageFont.truetype("arialbd.ttf", 16)
    font_title = ImageFont.truetype("arialbd.ttf", 22)
except IOError:
    font_main = ImageFont.load_default()
    font_bold = ImageFont.load_default()
    font_title = ImageFont.load_default()

def create_frame(title, users, highlight_col=-1):
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    draw.text((30, 20), title, font=font_title, fill=TEXT_COLOR)
    draw.line([30, 60, W-30, 60], fill=LINE_COLOR, width=2)
    
    headers = ["Virtual User", "Q1: Exercise?", "Q2: How Often?"]
    col_x = [30, 200, 400]
    for i, h in enumerate(headers):
        draw.text((col_x[i], 80), h, font=font_bold, fill=HEADER_COLOR)
    
    draw.line([30, 110, W-30, 110], fill=LINE_COLOR, width=1)
    
    start_y = 120
    row_h = 35
    
    for i, r in enumerate(users):
        y = start_y + i * row_h
        draw.line([30, y+row_h, W-30, y+row_h], fill=LINE_COLOR, width=1)
        draw.text((col_x[0], y+10), r['user'], font=font_main, fill=TEXT_COLOR)
        
        c1 = HIGHLIGHT_COLOR if highlight_col == 1 and r['q1'] else TEXT_COLOR
        f1 = font_bold if highlight_col == 1 and r['q1'] else font_main
        draw.text((col_x[1], y+10), r['q1'], font=f1, fill=c1)
        
        c2 = HIGHLIGHT_COLOR if highlight_col == 2 and r['q2'] else TEXT_COLOR
        f2 = font_bold if highlight_col == 2 and r['q2'] else font_main
        draw.text((col_x[2], y+10), r['q2'], font=f2, fill=c2)
        
    return img

frames = []
durations = []

def add_frame(img, duration_sec):
    frames.append(img)
    durations.append(duration_sec)

users = [{"user": f"User {i+1}", "q1": "", "q2": ""} for i in range(5)]

# Step 1: Empty slots (hold for 5 seconds)
img = create_frame("Step 1: Create Virtual Users", users)
add_frame(img, 5.0)

# Step 2: Fill Q1 linearly (1.5s per row)
q1_answers = ["Yes", "Yes", "Yes", "No", "No"]
for i in range(5):
    users[i]['q1'] = q1_answers[i]
    img = create_frame("Step 2: Apply Answers for Question 1", users, 1)
    add_frame(img, 1.5)
# Hold after filling Q1
add_frame(img, 4.0)

# Step 3: Fill Q2 linearly (1.5s per row)
q2_answers = ["Daily", "Daily", "Daily", "Never", "Never"]
for i in range(5):
    users[i]['q2'] = q2_answers[i]
    img = create_frame("Step 3: Apply Answers for Question 2", users, 2)
    add_frame(img, 1.5)
# Hold after filling Q2
add_frame(img, 4.0)

# Step 4: Shuffle (slower! 0.4s per frame)
shuffled = users.copy()
for i in range(10):
    random.shuffle(shuffled)
    img = create_frame("Step 4: Shuffling to Randomize Patterns...", shuffled)
    add_frame(img, 0.4)

# Step 5: Final (hold for 8 seconds before repeating)
final_shuffled = [users[3], users[1], users[4], users[0], users[2]]
img = create_frame("Step 5: Final Submission Order", final_shuffled)
add_frame(img, 8.0)

# Save with exact durations and infinite loop (loop=0)
imageio.mimsave("linked_distribution.gif", frames, duration=durations, loop=0)
print("Professional paced GIF created successfully.")
