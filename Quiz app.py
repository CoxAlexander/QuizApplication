# Imports
import tkinter as tk
import itertools
import sqlite3
from tkinter import PhotoImage
from PIL import Image, ImageTk

# Window Setup first
root = tk.Tk()
root.title("Quiz App")
root.geometry("750x500")

# Globals before anything else because otherwise it doesn't work
score = 0
question_count = 0
selected_quiz_id = tk.IntVar(value=1)
questions = []
answers_flat = []
correct_answers = []
num_questions = 0
quit_button = None
good_pil = Image.open("Good.png").resize((100, 100))
bad_pil = Image.open("Bad.png").resize((100, 100))
goodimage = ImageTk.PhotoImage(good_pil)
badimage = ImageTk.PhotoImage(bad_pil)
image_label = None
on_main_menu = True

# Backend Logic
class Backend:
    @staticmethod
    def load(quizId=None):
        if quizId is None:
            try:
                conn = sqlite3.connect("QuizDatabase.db")
                cursor = conn.cursor()
                cursor.execute("SELECT QuizID, QuizName, Score FROM Quiz")
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
        global on_main_menu
        on_main_menu = False


        question_count = 0
        score = 0

        quizId = selected_quiz_id.get()
        questions, answers_flat, correct_answers, num_questions = Backend.load(quizId)

        start_button.pack_forget()
        start_label.pack_forget()
        quiz_select_label.pack_forget()
        newQuiz_button.pack_forget()

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
        global image_label
        quizId = selected_quiz_id.get()
        if question_count >= num_questions:
            score_percent = (score / num_questions) * 100
            label.config(text=f"Quiz Complete! Your Score: {score}/{num_questions} {score_percent:.2f}%")
            Backend.show_quit_button()
            for button in [button1, button2, button3, button4]:
                button.config(state=tk.DISABLED)
            if image_label:
                image_label.pack_forget()
            if score_percent >= 75:
                image_label = tk.Label(root, image=goodimage, borderwidth=0)
                image_label.image = goodimage
            else:
                image_label = tk.Label(root, image=badimage, borderwidth=0)
                image_label.image = badimage
            image_label.place(relx=1.0, y=0, anchor='ne')

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
        
    @staticmethod
    def new():
        global on_main_menu
        on_main_menu = False
        start_button.pack_forget()
        start_label.pack_forget()
        quiz_select_label.pack_forget()
        newQuiz_button.pack_forget()
        quit_button.pack_forget()
        for widget in root.pack_slaves():
            if isinstance(widget, tk.Radiobutton):
                widget.pack_forget()
        
        newQuizLabel.pack()
        newQuizName.pack()
        confirmButton.pack()

    @staticmethod
    def addQuiz():
        quizName = newQuizName.get("1.0", "end-1c")
        if quizName != "": 
            try:
                conn = sqlite3.connect("QuizDatabase.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Quiz (QuizName,Score) VALUES (?,0) ", (quizName,))
                conn.commit()
                cursor.execute("SELECT QuizID FROM Quiz WHERE QuizName == ?", (quizName,))
                newQuizIdRows = cursor.fetchall()
                newQuizId = [row[0] for row in newQuizIdRows]
                conn.close()
                Backend.addQuestions(newQuizId)
            except:
                errorLabel = tk.Label(text="An error has occured in quiz making")
                errorLabel.pack()
            
    @staticmethod
    def addQuestions(newQuizId):
        newQuizLabel.config(text="Enter a question")
        answer1Label.pack_forget()
        newAnswer1.pack_forget()
        answer2Label.pack_forget()
        newAnswer2.pack_forget()
        answer3Label.pack_forget()
        newAnswer3.pack_forget()
        answer4Label.pack_forget()
        newAnswer4.pack_forget()
        SolutionLabel.pack_forget()
        newQuizName.delete("1.0","end")
        newQuizName.pack()
        confirmButton.config(text="Confirm Question", command=lambda: Backend.addQuestionDatabase(newQuizId))
        confirmButton.pack()

    @staticmethod 
    def addQuestionDatabase(quizId):
        questionText = newQuizName.get("1.0", "end-1c")
        if questionText != "": 
            try:
                conn = sqlite3.connect("QuizDatabase.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Questions (QuestionText,QuizId) VALUES (?,?) ", (questionText,quizId[0],))
                conn.commit()
                conn.close()
                confirmButton.pack_forget()
                newQuizName.delete("1.0","end")
                newQuizName.pack_forget()
                Backend.addAnswers(quizId, questionText)
            except:
                errorLabel = tk.Label(text="An error has occured")
                errorLabel.pack()    

    def addAnswers(quizId, questionText):
        newQuizLabel.config(text=questionText + "\n Enter the answers to the question and select which one is right")
        confirmButton.config(text="Next Question", command=lambda: Backend.addAnswersDatabase(quizId))
        answer1Label.pack()
        newAnswer1.pack()
        answer2Label.pack()
        newAnswer2.pack()
        answer3Label.pack()
        newAnswer3.pack()
        answer4Label.pack()
        newAnswer4.pack()
        SolutionLabel.pack()
        newQuizName.pack()
        confirmButton.pack()
        Backend.show_quit_button()


    def addAnswersDatabase(quizId):
        answer1Text = newAnswer1.get("1.0", "end-1c")
        answer2Text = newAnswer2.get("1.0", "end-1c")
        answer3Text = newAnswer3.get("1.0", "end-1c")
        answer4Text = newAnswer4.get("1.0", "end-1c")
        SolutionNum = newQuizName.get("1.0", "end-1c")
        newAnswer1.delete("1.0","end")
        newAnswer2.delete("1.0","end")
        newAnswer3.delete("1.0","end")
        newAnswer4.delete("1.0","end")
        newQuizName.delete("1.0","end")
        if ((answer1Text and answer2Text and answer3Text and answer4Text) and SolutionNum in ("1", "2", "3", "4")):
            try:
                conn = sqlite3.connect("QuizDatabase.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Solutions (SolutionNum,Ans1,Ans2,Ans3,Ans4,QuizId) VALUES (?,?,?,?,?,?) ", (int(SolutionNum),answer1Text,answer2Text,answer3Text,answer4Text,quizId[0],))
                conn.commit()
                conn.close()
                Backend.addQuestions(quizId)
            except:
                errorLabel = tk.Label(text="An weird error has occured")
                errorLabel.pack()

    def saveAndExit(quizId):
        answer1Text = newAnswer1.get("1.0", "end-1c")
        answer2Text = newAnswer2.get("1.0", "end-1c")
        answer3Text = newAnswer3.get("1.0", "end-1c")
        answer4Text = newAnswer4.get("1.0", "end-1c")
        SolutionNum = newQuizName.get("1.0", "end-1c")
        newAnswer1.delete("1.0","end")
        newAnswer2.delete("1.0","end")
        newAnswer3.delete("1.0","end")
        newAnswer4.delete("1.0","end")
        newQuizName.delete("1.0","end")
        if ((answer1Text and answer2Text and answer3Text and answer4Text) and SolutionNum in ("1", "2", "3", "4")):
            try:
                conn = sqlite3.connect("QuizDatabase.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Solutions (SolutionNum,Ans1,Ans2,Ans3,Ans4,QuizId) VALUES (?,?,?,?,?,?) ", (int(SolutionNum),answer1Text,answer2Text,answer3Text,answer4Text,quizId[0],))
                conn.commit()
                conn.close()
                Backend.addQuestions(quizId)
                Backend.BackToStart()
            except:
                errorLabel = tk.Label(text="An weird error has occured")
                errorLabel.pack()

    def BackToStart():
        #it forgor
        label.pack_forget()
        button_frame.pack_forget()
        button1.grid_forget()
        button2.grid_forget()
        button3.grid_forget()
        button4.grid_forget()
        newQuizLabel.pack_forget()
        newQuizName.pack_forget()
        confirmButton.pack_forget()
        answer1Label.pack_forget()
        newAnswer1.pack_forget()
        answer2Label.pack_forget()
        newAnswer2.pack_forget()
        answer3Label.pack_forget()
        newAnswer3.pack_forget()
        answer4Label.pack_forget()
        newAnswer4.pack_forget()
        SolutionLabel.pack_forget()
        if image_label:
            image_label.place_forget()
        
        # Recreate the radio buttons
        quiz_options = Backend.load()
        for widget in root.pack_slaves():
            if isinstance(widget, tk.Radiobutton):
                widget.destroy()

        start_label.pack(pady=10)
        quiz_select_label.pack(pady=5)
        for quiz_id, quiz_name, quiz_score in quiz_options:
            tk.Radiobutton(root, text=quiz_name + " : " + str(quiz_score) + "%", variable=selected_quiz_id, value=quiz_id).pack(anchor='c', pady=2)
        start_button.pack(pady=10)
        newQuiz_button.pack(pady=10)

    def show_quit_button():
        quit_button.pack(pady=10)

    @staticmethod
    def quit_logic():
        global on_main_menu, quit_button
        if on_main_menu:
            root.destroy()  # Quit the app if you're on the main menu
        else:
            quit_button.pack_forget()
            Backend.BackToStart()  # Otherwise just reset back to main menu
            on_main_menu = True


# Frontend GUI
class FrontEnd:
    @staticmethod
    def Main_Window():
        label.pack(pady=25)
        button_frame.pack(pady=50)

        button1.config(width=25, height=3, bg="red", fg="white")
        button2.config(width=25, height=3, bg="blue", fg="white")
        button3.config(width=25, height=3, bg="green", fg="white")
        button4.config(width=25, height=3, bg="yellow")

        button1.grid(row=0, column=0, padx=20, pady=5)
        button2.grid(row=0, column=1, padx=20, pady=5)
        button3.grid(row=1, column=0, padx=20, pady=5)
        button4.grid(row=1, column=1, padx=20, pady=5)

        Backend.Next()

# Start screen
start_label = tk.Label(root, text="All questions are subject to change.")
start_label.pack(pady=10)

quiz_select_label = tk.Label(root, text="Select a Quiz:", font=("Arial", 20))
quiz_select_label.pack()

quiz_options = Backend.load()
for quiz_id, quiz_name, quiz_score in quiz_options:
    tk.Radiobutton(root, text=quiz_name + " : " + str(quiz_score)+"%", variable=selected_quiz_id, value=quiz_id).pack(anchor='c')

start_button = tk.Button(root, text="begin", width=10, height=3, command=Backend.start)
start_button.pack(pady=10)

newQuiz_button = tk.Button(root, text="Make New Quiz", width=15, height=3, command=Backend.new)
newQuiz_button.pack(pady=10)

quit_button = tk.Button(root, text="Quit", width=10, height=3, command=lambda: Backend.quit_logic())

# Other widgets setup
newQuizName = tk.Text(root, height=0, width=50)
newQuizLabel = tk.Label(root, text="Enter the Quiz name")
confirmButton = tk.Button(root, text="Confirm", command=Backend.addQuiz)
newAnswer1 = tk.Text(root, height=0, width=50)
answer1Label = tk.Label(root, text="Answer 1")
newAnswer2 = tk.Text(root, height=0, width=50)
answer2Label = tk.Label(root, text="Answer 2")
newAnswer3 = tk.Text(root, height=0, width=50)
answer3Label = tk.Label(root, text="Answer 3")
newAnswer4 = tk.Text(root, height=0, width=50)
answer4Label = tk.Label(root, text="Answer 4")
SolutionLabel = tk.Label(root, text="Type either 1,2,3,4 to indicate which answer is correct")
label = tk.Label(root, font=("Arial", 20))
button_frame = tk.Frame(root)
button1 = tk.Button(button_frame)
button2 = tk.Button(button_frame)
button3 = tk.Button(button_frame)
button4 = tk.Button(button_frame)

root.mainloop()
