# utils.py
import pandas as pd
from io import BytesIO
import json
import re


def generator(excel_file, number_of_questions):
    temp = []
    for name, question_count in number_of_questions.items():
        # Read the specific sheet into a DataFrame
        data = pd.read_excel(excel_file, sheet_name=name)
        # Extract the specified number of random rows from the sheet
        extract = data.sample(question_count)
        # Append the extracted rows to the list
        temp.append(extract)
    
    # Combine all the DataFrames in the list into a single DataFrame
    df_combined = pd.concat(temp, ignore_index=True) # nó sẽ lùi index xún 1 hàng là 0 -> 1 thay vì hàng đầu 1 ->2

    # Write the combined DataFrame to a new Excel file in memory
    output = BytesIO()
    df_combined.to_excel(output, index=False) # index = False giúp cho excel không tự động thêm một cột id vào duẽ liệu
    output.seek(0) # đtwj con trỏ vào vị trí đầu tiên để chạy xún dưới
    
    return output, df_combined


def arrange_answers(answers, correct_label):
    correct_index = ord(correct_label.upper()) - ord('A')
    answers.insert(0, answers.pop(correct_index))
    return answers

def clean_text(text):
    text = re.sub(r'<', '&lt;', text)
    text = re.sub(r'>', '&gt;', text)
    text = re.sub(r'\r', '', text)
    text = re.sub(r'\n', '<br>', text)
    return text.strip()

def excel_to_json(data):
    # Prepare the JSON structure
    output_structure = {"mc_questions": []}

    for index, row in data.iterrows():
        try:
            # Extract question and answers
            answers = [row[f'options[{label.lower()}]'] for label in 'ABCDEFG' if pd.notnull(row[f'options[{label.lower()}]'])]
            correct_label = row['correct'].strip().upper()
            # Arrange answers based on the correct label
            arranged_answers = arrange_answers(answers, correct_label) if correct_label in 'ABCDEFG' else answers

            cleaned_question = clean_text(str(row['question']))
            cleaned_answers = [clean_text(str(answer)) for answer in arranged_answers]


            question_data = {
                "question": cleaned_question,
                "answers": cleaned_answers
            }
            # Add the question data to the list
            output_structure["mc_questions"].append(question_data)
        except KeyError as e:
            print(f"KeyError: {e} at row {index}")
        except Exception as e:
            print(f"Unexpected error: {e} at row {index}")

    # Convert the output structure to a JSON string
    json_data = json.dumps(output_structure, indent=4, ensure_ascii=False)
    
    return json_data

