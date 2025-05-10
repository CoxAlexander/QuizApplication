# Imports
import tkinter as tk  # GUI framework for building the quiz interface
import itertools  # Used for creating cycles of questions and answers
import sqlite3  # Provides functionality for database operations
from tkinter import PhotoImage  # Allows image integration in Tkinter
from PIL import Image, ImageTk  # For handling and resizing images (Pillow library)

# Window Setup first
root = tk.Tk()  # Create the main application window
root.title("Quiz App")  # Set window title
root.geometry("750x500")  # Set window size

# Globals before anything else because otherwise it doesn't work
score = 0  # Keeps track of the user's score
question_count = 0  # Keeps track of the current question index
selected_quiz_id = tk.IntVar(value=1)  # Stores the selected quiz ID from user input
questions = []  # List of question text loaded from the database
answers_flat = []  # Flattened list of answer options for all questions
correct_answers = []  # List of correct answer indices for all questions
num_questions = 0  # Total number of questions in the selected quiz
quit_button = None  # Placeholder for the quit button widget
good_pil = Image.open("Good.png").resize((100, 100))  # Load and resize the "good score" image
bad_pil = Image.open("Bad.png").resize((100, 100))  # Load and resize the "bad score" image
goodimage = ImageTk.PhotoImage(good_pil)  # Tkinter-compatible version of the "good" image
badimage = ImageTk.PhotoImage(bad_pil)  # Tkinter-compatible version of the "bad" image
image_label = None  # Placeholder for the image label widget
on_main_menu = True  # Boolean flag to track if the user is on the main menu

# Backend Logic
class Backend:
    @staticmethod
    def load(quizId=None):
        """
        Load either quiz options or specific quiz questions and answers
        depending on whether a quizId is provided.
        """
        if quizId is None:
            try:
                conn = sqlite3.connect("QuizDatabase.db")  # Connect to the database
                cursor = conn.cursor()
                cursor.execute("SELECT QuizID, QuizName, Score FROM Quiz")  # Fetch quiz options
                options = cursor.fetchall()
                conn.close()
                return options
            except:
                return [(1, "Default Quiz")]  # Fallback option if DB query fails

        try:
            conn = sqlite3.connect("QuizDatabase.db")
            cursor = conn.cursor()

            # Fetch answers and correct solution index
            cursor.execute("""
                SELECT Solutions.Ans1, Solutions.Ans2, Solutions.Ans3, Solutions.Ans4, Solutions.SolutionNum
                FROM Solutions WHERE Solutions.QuizId == ?
            """, (quizId,))
            solution_rows = cursor.fetchall()

            # Fetch corresponding questions
            cursor.execute("""
                SELECT Questions.QuestionText 
                FROM Questions WHERE Questions.QuizId == ?
            """, (quizId,))
            question_rows = cursor.fetchall()
            conn.close()

            if not solution_rows and not question_rows:
                return ["No data available"], [], [], 0

            questions = [row[0] for row in question_rows]  # Extract question text
            answers_flat = [ans for row in solution_rows for ans in row[0:4]]  # Flatten answers
            correct_answers = [row[4] for row in solution_rows]  # Extract correct answer indices
            num_questions = len(question_rows)
            return questions, answers_flat, correct_answers, num_questions

        except sqlite3.Error:
            return ["Database error"], [], [], 0

    @staticmethod
    def start():
        """
        Start the quiz by initializing question data and updating the UI.
        """
        global question_count, score, questions, answers_flat, correct_answers, num_questions
        global text_cycle, button_cycle, solution_cycle
        global on_main_menu
        on_main_menu = False

        question_count = 0  # Reset question count
        score = 0  # Reset score

        quizId = selected_quiz_id.get()  # Get the selected quiz ID
        questions, answers_flat, correct_answers, num_questions = Backend.load(quizId)

        # Hide main menu widgets
        start_button.pack_forget()
        start_label.pack_forget()
        quiz_select_label.pack_forget()
        newQuiz_button.pack_forget()

        for widget in root.pack_slaves():
            if isinstance(widget, tk.Radiobutton):
                widget.pack_forget()

        # Create cycling iterators for questions and answers
        text_cycle = itertools.cycle(questions)
        button_cycle = itertools.cycle(answers_flat)
        solution_cycle = itertools.cycle(correct_answers)

        FrontEnd.Main_Window()  # Launch the main quiz UI

    @staticmethod
    def Next():
        """
        Proceed to the next question or show results if the quiz is over.
        """
        global question_count, score
        global image_label
        quizId = selected_quiz_id.get()
        if question_count >= num_questions:
            # Display quiz results
            score_percent = (score / num_questions) * 100
            label.config(text=f"Quiz Complete! Your Score: {score}/{num_questions} {score_percent:.2f}%")
            Backend.show_quit_button()

            for button in [button1, button2, button3, button4]:
                button.config(state=tk.DISABLED)

            if image_label:
                image_label.pack_forget()

            # Show image depending on score
            if score_percent >= 75:
                image_label = tk.Label(root, image=goodimage, borderwidth=0)
                image_label.image = goodimage
            else:
                image_label = tk.Label(root, image=badimage, borderwidth=0)
                image_label.image = badimage
            image_label.place(relx=1.0, y=0, anchor='ne')

            # Update high score in database
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

        # Display next question
        question_count += 1
        label.config(text=next(text_cycle))
        button1_text = next(button_cycle)
        button2_text = next(button_cycle)
        button3_text = next(button_cycle)
        button4_text = next(button_cycle)
        correct_choice = int(next(solution_cycle))

        # Update button labels and bind their click event
        button1.config(text=button1_text, state=tk.NORMAL, command=lambda: Backend.Selected(1, correct_choice))
        button2.config(text=button2_text, state=tk.NORMAL, command=lambda: Backend.Selected(2, correct_choice))
        button3.config(text=button3_text, state=tk.NORMAL, command=lambda: Backend.Selected(3, correct_choice))
        button4.config(text=button4_text, state=tk.NORMAL, command=lambda: Backend.Selected(4, correct_choice))

    @staticmethod
    def Selected(choice, correct_choice):
        #Handles the user's answer selection and checks if it's correct.
        global score
        if choice == correct_choice:
            score += 1  # Increment score for correct answer
        Backend.Next()  # Proceed to next question

    @staticmethod
    def new():
        #Start the new quiz creation process and update UI accordingly.
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
        #Add a new quiz entry to the database.
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
        #Transition UI to accept question input for the new quiz.
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
        #Add a question to the database and prepare to collect its answers.
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
        #Show UI elements to input answers and indicate the correct one.
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
        #Save the provided answers to the database.
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
        # Saves the current question and its answers to the database, then exits quiz creation
        answer1Text = newAnswer1.get("1.0", "end-1c")  # Get text from Answer 1 input field
        answer2Text = newAnswer2.get("1.0", "end-1c")  # Get text from Answer 2 input field
        answer3Text = newAnswer3.get("1.0", "end-1c")  # Get text from Answer 3 input field
        answer4Text = newAnswer4.get("1.0", "end-1c")  # Get text from Answer 4 input field
        SolutionNum = newQuizName.get("1.0", "end-1c")  # Get correct answer number from text input
        newAnswer1.delete("1.0","end")  # Clear Answer 1 input
        newAnswer2.delete("1.0","end")  # Clear Answer 2 input
        newAnswer3.delete("1.0","end")  # Clear Answer 3 input
        newAnswer4.delete("1.0","end")  # Clear Answer 4 input
        newQuizName.delete("1.0","end")  # Clear correct answer input
        if ((answer1Text and answer2Text and answer3Text and answer4Text) and SolutionNum in ("1", "2", "3", "4")):
            try:
                # Insert the question and answers into the database
                conn = sqlite3.connect("QuizDatabase.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Solutions (SolutionNum,Ans1,Ans2,Ans3,Ans4,QuizId) VALUES (?,?,?,?,?,?) ", (int(SolutionNum),answer1Text,answer2Text,answer3Text,answer4Text,quizId[0],))
                conn.commit()
                conn.close()
                Backend.addQuestions(quizId)  # Continue to question creation interface
            except:
                errorLabel = tk.Label(text="An weird error has occured")  # Error message if DB fails
                errorLabel.pack()

    def BackToStart():
        # Returns to the main menu screen and resets all visible widgets
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

        # Load quiz options and regenerate radio buttons
        quiz_options = Backend.load()
        for widget in root.pack_slaves():
            if isinstance(widget, tk.Radiobutton):
                widget.destroy()

        start_label.pack(pady=10)  # Show welcome/start label
        quiz_select_label.pack(pady=5)  # Show quiz selection prompt
        for quiz_id, quiz_name, quiz_score in quiz_options:
            tk.Radiobutton(root, text=quiz_name + " : " + str(quiz_score) + "%", variable=selected_quiz_id, value=quiz_id).pack(anchor='c', pady=2)  # Quiz selection options
        start_button.pack(pady=10)  # Show start button
        newQuiz_button.pack(pady=10)  # Show new quiz creation button

    def show_quit_button():
        # Displays the quit button during quiz creation or after finishing
        quit_button.pack(pady=10)

    @staticmethod
    def quit_logic():
        # Logic to handle quitting from either main menu or quiz creation view
        global on_main_menu, quit_button
        if on_main_menu:
            root.destroy()  # Close the application if on main menu
        else:
            quit_button.pack_forget()  # Hide the quit button
            Backend.BackToStart()  # Return to the main menu interface

# Frontend GUI
class FrontEnd:
    @staticmethod
    def Main_Window():
        # Display the main quiz question label and the answer buttons
        label.pack(pady=25)
        button_frame.pack(pady=50)

        # Configure button colors and sizes
        button1.config(width=25, height=3, bg="red", fg="white")
        button2.config(width=25, height=3, bg="blue", fg="white")
        button3.config(width=25, height=3, bg="green", fg="white")
        button4.config(width=25, height=3, bg="yellow")

        # Arrange buttons in a 2x2 grid layout
        button1.grid(row=0, column=0, padx=20, pady=5)
        button2.grid(row=0, column=1, padx=20, pady=5)
        button3.grid(row=1, column=0, padx=20, pady=5)
        button4.grid(row=1, column=1, padx=20, pady=5)

        # Load and display the first quiz question
        Backend.Next()

# Start screen
start_label = tk.Label(root, text="All questions are subject to change.")  # Introductory label
start_label.pack(pady=10)

quiz_select_label = tk.Label(root, text="Select a Quiz:", font=("Arial", 20))  # Quiz selection prompt
quiz_select_label.pack()

quiz_options = Backend.load()  # Load available quizzes from the database
for quiz_id, quiz_name, quiz_score in quiz_options:
    # Create a radio button for each quiz with its name and score
    tk.Radiobutton(root, text=quiz_name + " : " + str(quiz_score)+"%", variable=selected_quiz_id, value=quiz_id).pack(anchor='c')

# Start quiz button
start_button = tk.Button(root, text="begin", width=10, height=3, command=Backend.start)
start_button.pack(pady=10)

# Button to initiate new quiz creation
newQuiz_button = tk.Button(root, text="Make New Quiz", width=15, height=3, command=Backend.new)
newQuiz_button.pack(pady=10)

# Quit button (initially not packed)
quit_button = tk.Button(root, text="Quit", width=10, height=3, command=lambda: Backend.quit_logic())

# Other widgets setup for quiz creation input fields (initially hidden)
newQuizName = tk.Text(root, height=0, width=50)  # Input for quiz name
newQuizLabel = tk.Label(root, text="Enter the Quiz name")  # Label for quiz name input
confirmButton = tk.Button(root, text="Confirm", command=Backend.addQuiz)  # Button to confirm quiz creation

# Text fields and labels for the four possible answers
newAnswer1 = tk.Text(root, height=0, width=50)
answer1Label = tk.Label(root, text="Answer 1")
newAnswer2 = tk.Text(root, height=0, width=50)
answer2Label = tk.Label(root, text="Answer 2")
newAnswer3 = tk.Text(root, height=0, width=50)
answer3Label = tk.Label(root, text="Answer 3")
newAnswer4 = tk.Text(root, height=0, width=50)
answer4Label = tk.Label(root, text="Answer 4")

# Instructional label for selecting the correct answer number
SolutionLabel = tk.Label(root, text="Type either 1,2,3,4 to indicate which answer is correct")

# Label to display quiz questions
label = tk.Label(root, font=("Arial", 20))

# Frame to hold the answer buttons
button_frame = tk.Frame(root)

# Answer buttons (to be configured in Main_Window)
button1 = tk.Button(button_frame)
button2 = tk.Button(button_frame)
button3 = tk.Button(button_frame)
button4 = tk.Button(button_frame)

# Run the GUI event loop
root.mainloop()
