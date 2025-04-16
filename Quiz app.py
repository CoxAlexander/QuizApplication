# Imports
import tkinter as tk
import itertools
import sqlite3

#Window Setup first
root = tk.Tk()
root.geometry("750x500")

# Globals before anything else because otherwise it doesn't work
score = 0
question_count = 0
selected_quiz_id = tk.IntVar(value=1)
questions = []
answers_flat = []
correct_answers = []
num_questions = 0

#Backend Logic
class Backend:
    @staticmethod
    def load(quizId=None):
        if quizId is None:
            try:
                conn = sqlite3.connect("QuizDatabase.db")
                cursor = conn.cursor()
                cursor.execute("SELECT QuizID, QuizName FROM Quiz")
                options = cursor.fetchall()
                conn.close()
                return options
            except:
                return [(1, "Default Quiz")]

        try:
            conn = sqlite3.connect("QuizDatabase.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT Solutions.Ans1, Solutions.Ans2, Solutions.Ans3, Solutions.Ans4, Solutions.SolutionNum
                FROM Solutions WHERE Solutions.QuizId == ?
            """, (quizId,))
            solution_rows = cursor.fetchall()

            cursor.execute("""
                SELECT Questions.QuestionText 
                FROM Questions WHERE Questions.QuizId == ?
            """, (quizId,))
            question_rows = cursor.fetchall()
            conn.close()
            
            if not solution_rows and not question_rows:
                return ["No data available"], [], [], 0

            questions = [row[0] for row in question_rows]
            answers_flat = [ans for row in solution_rows for ans in row[0:4]]
            correct_answers = [row[4] for row in solution_rows]
            num_questions = len(question_rows)
            return questions, answers_flat, correct_answers, num_questions

        except sqlite3.Error:
            return ["Database error"], [], [], 0

    @staticmethod
    def start():
        global question_count, score, questions, answers_flat, correct_answers, num_questions
        global text_cycle, button_cycle, solution_cycle

        question_count = 0
        score = 0

        quizId = selected_quiz_id.get()
        questions, answers_flat, correct_answers, num_questions = Backend.load(quizId)

        start_button.pack_forget()
        start_label.pack_forget()
        quiz_select_label.pack_forget()
        
        for widget in root.pack_slaves():
            if isinstance(widget, tk.Radiobutton):
                widget.pack_forget()

        text_cycle = itertools.cycle(questions)
        button_cycle = itertools.cycle(answers_flat)
        solution_cycle = itertools.cycle(correct_answers)

        FrontEnd.Main_Window()

    @staticmethod
    def Next():
        global question_count, score
        quizId = selected_quiz_id.get()

        if question_count >= num_questions:
            score_percent = (score / num_questions) * 100
            label.config(text=f"Quiz Complete! Your Score: {score}/{num_questions} {score_percent:.2f}%")
            try:
                conn = sqlite3.connect("QuizDatabase.db")
                cursor = conn.cursor()
                cursor.execute("SELECT Score FROM Quiz WHERE QuizID == ?", (quizId,))
                prev_score_rows = cursor.fetchall()
                prev_score = [row[0] for row in prev_score_rows]
                if score_percent > prev_score[0]:
                    cursor.execute("UPDATE Quiz SET Score = ? WHERE QuizID == ?", (int(score_percent), quizId))
                    conn.commit()
                conn.close()
            except:
                return
            
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

        button1.config(text=button1_text, state=tk.NORMAL, command=lambda: Backend.Selected(1, correct_choice))
        button2.config(text=button2_text, state=tk.NORMAL, command=lambda: Backend.Selected(2, correct_choice))
        button3.config(text=button3_text, state=tk.NORMAL, command=lambda: Backend.Selected(3, correct_choice))
        button4.config(text=button4_text, state=tk.NORMAL, command=lambda: Backend.Selected(4, correct_choice))

    @staticmethod
    def Selected(choice, correct_choice):
        global score
        if choice == correct_choice:
            score += 1
        Backend.Next()

# Frontend GUI
class FrontEnd:
    @staticmethod
    def Main_Window():
        label.pack(pady=25)
        button_frame.pack(pady=50)

        button1.config(width=25, height=3)
        button2.config(width=25, height=3)
        button3.config(width=25, height=3)
        button4.config(width=25, height=3)

        button1.grid(row=0, column=0, padx=20, pady=5)
        button2.grid(row=0, column=1, padx=20, pady=5)
        button3.grid(row=1, column=0, padx=20, pady=5)
        button4.grid(row=1, column=1, padx=20, pady=5)

        Backend.Next()

#Start screen
start_label = tk.Label(root, text="All questions are subject to change.")
start_label.pack(pady=10)

quiz_select_label = tk.Label(root, text="Select a Quiz:", font=("Arial", 20))
quiz_select_label.pack()

quiz_options = Backend.load()
for quiz_id, quiz_name in quiz_options:
    tk.Radiobutton(root, text=quiz_name, variable=selected_quiz_id, value=quiz_id).pack(anchor='c')

start_button = tk.Button(root, text="begin", width=10, height=3, command=Backend.start)
start_button.pack(pady=10)

label = tk.Label(root, font=("Arial", 20))
button_frame = tk.Frame(root)
button1 = tk.Button(button_frame)
button2 = tk.Button(button_frame)
button3 = tk.Button(button_frame)
button4 = tk.Button(button_frame)

root.mainloop()
