import tkinter as tk
import itertools

def load_texts(filename):
    try:
        with open(filename, "r") as file:
            texts = [line.strip() for line in file if line.strip()]
        return texts if texts else ["No text available"]
    except FileNotFoundError:
        return ["File not found"]

def start():
    global question_count, text_cycle, button_cycle, solution_cycle, score
    question_count = 0
    score = 0

    start_button.pack_forget()
    start_label.pack_forget()

    text_cycle = itertools.cycle(texts)
    button_cycle = itertools.cycle(buttons * 4)
    solution_cycle = itertools.cycle(solutions)

    show_main_window()

def show_main_window():
    label.pack(pady=10)

    max_width = max(len(text) for text in buttons)
    for button in [button1, button2, button3, button4]:
        button.config(width=max_width, height=3)

    button1.grid(row=0, column=0, padx=20, pady=5)
    button2.grid(row=0, column=1, padx=20, pady=5)
    button3.grid(row=1, column=0, padx=20, pady=5)
    button4.grid(row=1, column=1, padx=20, pady=5)

    next_text()

def next_text():
    global question_count
    if question_count >= num_questions:
        label.config(text=f"Quiz Complete! Your Score: {score}/{num_questions}")
        for button in [button1, button2, button3, button4]:
            button.config(state=tk.DISABLED)
        return

    question_count += 1
    label.config(text=next(text_cycle))

    button1_text = next(button_cycle)
    button2_text = next(button_cycle)
    button3_text = next(button_cycle)
    button4_text = next(button_cycle)

    correct_choice = int(next(solution_cycle))

    button1.config(text=button1_text, state=tk.NORMAL, command=lambda: option_selected(1, correct_choice))
    button2.config(text=button2_text, state=tk.NORMAL, command=lambda: option_selected(2, correct_choice))
    button3.config(text=button3_text, state=tk.NORMAL, command=lambda: option_selected(3, correct_choice))
    button4.config(text=button4_text, state=tk.NORMAL, command=lambda: option_selected(4, correct_choice))

def option_selected(choice, correct_choice):
    global score
    if choice == correct_choice:
        score += 1
    next_text()

root = tk.Tk()
root.geometry("500x300")

num_questions = 10
score = 0
question_count = 0

texts = load_texts("questions.txt")
buttons = load_texts("answers.txt")
solutions = load_texts("solutions.txt")

start_label = tk.Label(root, text="All questions are subject to change.")
start_label.pack(pady=10)

start_button = tk.Button(root, text="begin", width=10, height=3, command=start)
start_button.pack()

label = tk.Label(root, text="")
label.pack()

button_frame = tk.Frame(root)
button_frame.pack()

button1 = tk.Button(button_frame, text="")
button2 = tk.Button(button_frame, text="")
button3 = tk.Button(button_frame, text="")
button4 = tk.Button(button_frame, text="")

root.mainloop()
