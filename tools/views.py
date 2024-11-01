from django.shortcuts import render
from django import forms
import json
import pandas as pd
from django.http import HttpResponse
from .forms import ExcelUploadForm ,WordUploadForm
import zipfile
from tools.libs.utils import excel_to_json
import os
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from tools.libs.utils import excel_to_json, word_to_json
from tools.libs import txtToJson
def excel_to_json_view(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            json_files = []

            for excel_file in form.cleaned_data['files']:  # Sử dụng cleaned_data
                try:
                    # Đọc dữ liệu từ file Excel
                    excel_data = pd.read_excel(excel_file, sheet_name=None)  # Đọc toàn bộ sheets của file Excel
                    print(f"EXCEL_DATA IS :{excel_data}")

                    for sheet_name, df in excel_data.items():
                        # Convert the sheet to JSON
                        json_output = excel_to_json(df)  # excel_to_json() expects a DataFrame
                        print(json_output)

                        # Create a separate JSON file for each sheet
                        json_filename = f"{excel_file.name.split('.')[0]}_{sheet_name}.json"
                        # json_string = json.dumps(json_output, indent=4, ensure_ascii=False)
                        json_files.append((json_filename, json_output))  # Append each sheet's JSON to the list

                except Exception as e:
                    print(f"Lỗi khi xử lý tệp Excel '{excel_file.name}': {e}")

            # Tạo tệp ZIP để chứa tất cả các file JSON
            file_name_without_extension = os.path.splitext(excel_file.name)[0]
            zip_filename = file_name_without_extension + '_converted.zip' 
            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'

            with zipfile.ZipFile(response, 'w') as zip_file:
                for json_filename, json_string in json_files:
                    # Add each JSON file for each sheet to the ZIP
                    zip_file.writestr(json_filename, json_string)

            return response

    else:
        form = ExcelUploadForm()

    return render(request, 'tool_excel_to_json.html', {'form': form})


from .libs.txtToJson import txt_to_json
from docx import Document
import json
import re

def read_docx_content(file):
    """Đọc nội dung từ tệp .docx."""
    document = Document(file)  # Mở tệp .docx
    content = []  # Khởi tạo danh sách để lưu nội dung

    # Lặp qua tất cả các đoạn văn và bảng trong tài liệu
    for paragraph in document.paragraphs:
        content.append(paragraph.text.strip())  # Thêm nội dung đoạn văn vào danh sách
    
    # Lặp qua tất cả các bảng trong tài liệu
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                content.append(cell.text.strip())  # Thêm nội dung của ô vào danh sách

    # Kết hợp tất cả nội dung thành một chuỗi, mỗi đoạn cách nhau bởi dấu xuống dòng
    return "\n".join(content)

def word_to_json_view(request):
    if request.method == 'POST':
        form = WordUploadForm(request.POST, request.FILES)
        if form.is_valid():
            json_files = []
            for uploaded_file in form.cleaned_data['files']:
                try:
                    # Đọc nội dung file .docx
                    if uploaded_file.name.endswith('.docx'):
                        content = read_docx_content(uploaded_file)
                    
                    # Gọi hàm word_to_json để chuyển đổi nội dung sang JSON
                    json_output = word_to_json(content)
                    print(json_output)
                    json_filename = f"{os.path.splitext(uploaded_file.name)[0]}.json"
                    json_files.append((json_filename, json_output))
                
                except Exception as e:
                    print(f"Lỗi khi xử lý tệp '{uploaded_file.name}': {e}")

            # Tạo file zip chứa các file JSON
            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="converted_files.zip"'
            with zipfile.ZipFile(response, 'w') as zip_file:
                for json_filename, json_string in json_files:
                    zip_file.writestr(json_filename, json_string)
            return response
    else:
        form = WordUploadForm()

    return render(request, 'tool_word_to_json.html', {'form': form})

def view_tools(request):
    return render(request,'view_tools.html')

def txt_to_json_view(request):
    """Xử lý việc chuyển đổi văn bản từ textarea sang JSON và trả về file ZIP."""
    if request.method == 'POST':
        # Lấy dữ liệu từ textarea
        texts = request.POST.getlist('texts')  # texts là danh sách các chuỗi từ textarea
        
        # Chuyển đổi danh sách các chuỗi thành JSON
        json_output = txt_to_json(texts, 'default_filename.txt')  # Gọi hàm với texts

        json_filename = 'converted_data.json'
        json_files = [(json_filename, json_output)]

        # Tạo file zip chứa file JSON
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="converted_files.zip"'
        
        with zipfile.ZipFile(response, 'w') as zip_file:
            for json_filename, json_string in json_files:
                zip_file.writestr(json_filename, json_string)

        return response

    return render(request, 'tool_txt_to_json.html')




