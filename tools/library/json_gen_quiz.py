import streamlit as st
import json
import streamlit_ext as ste
import random
from mitosheet.streamlit.v1 import spreadsheet
from io import BytesIO, StringIO
import pandas as pd
from .utils import (
    excel_to_json
)
from tools.library.txtToJson import txt_to_json


def json_quiz_generator():
    st.title("Generate test/exam from JSON file")

    uploaded_file = st.file_uploader("Upload a JSON file to get started", type="json")
    if uploaded_file is not None:
        if 'generated_files_json' not in st.session_state:
            st.session_state.generated_files_json = []

        json_str = uploaded_file.read().decode("utf-8")
        # st.text(json_str)
        data = json.loads(json_str)
        make_quiz_from_json(data)

def excel_quiz_genrator():
    st.title("Generate test/exam from EXCEL file")

    # Provide a link to the template Excel file
    st.markdown(
        """
        Please download and use the [Excel template](https://docs.google.com/spreadsheets/d/1THYBdUTsXGOsAEDq8ZG9PYoeytKicxZT/edit?usp=sharing&ouid=108881121725790457331&rtpof=true&sd=true) for your quiz.
        The Excel file must contain exactly one sheet with the required columns.
        """,
        unsafe_allow_html=True
    )
    uploaded_file = st.file_uploader("Upload an EXCEL file to get started", type="xlsx")

    if uploaded_file is not None:
        # Initialize session state for generated files
        if 'generated_files_json' not in st.session_state:
            st.session_state.generated_files_json = []
        
        # Load the Excel file
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names

        # Check the number of sheets
        if len(sheet_names) != 1:
            st.error("The uploaded file must contain exactly one sheet.")
            return
        
        # Read the single sheet
        sheet_name = sheet_names[0]
        data = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        
        # Process the data
        json_output = excel_to_json(data)
        
        # st.text(json_output)

        data = json.loads(json_output)
        make_quiz_from_json(data)
        
        st.success("Quiz generated successfully!")

def txt_quiz_generator():
    st.title("Generate test/exam from TXT file")

    uploaded_file_convert = st.file_uploader("Upload TXT files to get started", type="txt")
    if uploaded_file_convert is not None:
        file_name = uploaded_file_convert.name[:-4]  # Get the file name without extension
        file_like = StringIO(uploaded_file_convert.getvalue().decode('utf-8',errors='ignore'))
        json_output = txt_to_json(file_like, file_name)
        data = json.loads(json_output)
        make_quiz_from_json(data)
        st.success("Quiz generated successfully!")

def make_quiz_from_json(data):
    if 'mc_questions' not in data or not data['mc_questions']:
        st.error("The JSON file does not contain any questions or the questions list is empty.")
        return

    # Assign correct answers if not explicitly provided
    for question in data["mc_questions"]:
        if "Correct Answer" not in question:
            question["Correct Answer"] = question["answers"][0]

    questions = data.get("mc_questions", [])

    if 'quiz' not in st.session_state:
        st.session_state.quiz = []
        st.session_state.user_choice = []
        st.session_state.shuffled_answers = []
        st.session_state.correct_answers = []
        st.session_state.submit = []

# Button to generate the quiz
    if st.button("Generate the quiz"):
        # Generate a new quiz and reset the user's choices
        st.session_state.quiz = random.sample(questions, len(questions))
        st.session_state.user_choice = [None] * len(st.session_state.quiz)
        st.session_state.shuffled_answers = []
        st.session_state.correct_answers = []
        st.session_state.submit = []

        for question in st.session_state.quiz:
            # Scramble the answers
            answers = question['answers'][:]
            random.shuffle(answers)
            st.session_state.shuffled_answers.append(answers)
            st.session_state.correct_answers.append(question["Correct Answer"])

# Display the quiz if it has been generated
    if st.session_state.quiz:
        st.session_state.submit = None
        for id, question in enumerate(st.session_state.quiz):
            # Add question number before the question text and apply bold and size styles
            question_text = f"<div style='background-color: black; color: white; padding: 20px; border-radius: 10px; margin: 10px 0;'><strong>Q{id + 1}:</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{question['question']} </div>"
            st.markdown(question_text, unsafe_allow_html=True)

            # Display the radio buttons with the user's previous selection if any
            selected_answer = st.radio(
                label="",
                options=st.session_state.shuffled_answers[id],
                index=st.session_state.shuffled_answers[id].index(st.session_state.user_choice[id])
                if st.session_state.user_choice[id] else None,
                key=f"question_{id}"  # Use a unique key for each question
            )
            
            # Update the selected answer in session state
            st.session_state.user_choice[id] = selected_answer

            # Display result after the answer choices
            

        # Button to submit the quiz
        if st.button("Submit"):
            show_results()
    else:
        st.session_state.quiz = None
        st.session_state.user_choice = None
        st.session_state.shuffled_answers = None

def show_results():

    st.session_state.submit =[]
                # Display results for all questions
    st.write("### Quiz Results")

    correct_count = sum(user_answer == correct_answer for user_answer, correct_answer in zip(st.session_state.user_choice, st.session_state.correct_answers))
    total_questions = len(st.session_state.quiz)
    st.write(f"### Summary")
    st.write(f"You got {correct_count} out of {total_questions} questions correct.")    
    
    for id, question in enumerate(st.session_state.quiz):
        correct_answer = st.session_state.correct_answers[id]
        user_answer = st.session_state.user_choice[id]
        is_correct = user_answer == correct_answer
                    
                    # Display the result in a colored block
        result_color = 'green' if is_correct else 'red'
        result_text = f"""
                    <div style='background-color: black; color: white; padding: 20px; border-radius: 10px; margin: 10px 0;'><strong>Q{id + 1}:</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{question['question']} </div>
                    <div style='color: {result_color};'>
                        <strong>Your Answer:</strong> {user_answer}<br>
                        <strong>Correct Answer:</strong> {correct_answer}<br>
                        <strong>Result:</strong> {'Correct' if is_correct else 'Incorrect'}
                    </div>
                    """
                
        st.markdown(result_text, unsafe_allow_html=True)
                # Optionally, display a summary
