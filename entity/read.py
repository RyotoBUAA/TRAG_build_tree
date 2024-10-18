import os
from docx import Document
import win32com.client
import PyPDF2
from rel_llm import chat
import csv

def read_doc(file_path):
    word = win32com.client.Dispatch("Word.Application")
    try:
        doc = word.Documents.Open(file_path)
        text = []
        for paragraph in doc.Paragraphs:
            text.append(paragraph.Range.Text)
        doc.Close()
        word.Quit()
        return '\n'.join(text)
    except Exception as e:
        print(f"Failed to convert {file_path}. Error: {e}")
        return ""


def read_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)


def search_doc_files(directory):
    doc_contents = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".docx"):
                print(f"Reading {file_path}: ")
                content = read_docx(file_path)
                doc_contents[file_path] = content
                print(content)
            elif file.endswith(".doc"):
                print(f"Reading {file_path}: ")
                content = read_doc(file_path)
                doc_contents[file_path] = content
                print(content)
    return doc_contents


def read_all_content(directory):
    contents = search_doc_files(directory)
    # 输出读取内容
    for file_path, content in contents.items():
        print(f"Content of {file_path}:\n{content}\n")
    return contents


def extract_text_from_pdf(pdf_path):
    text = ''
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ''
    return text


def output_relation(pdf_text):

    rows = []
    rows = rows+chat.relation_extract_str(pdf_text[:5000])

    while len(pdf_text) > 5000:
        pdf_text = pdf_text[5000:]
        print("切割文本")
        rows = rows + chat.relation_extract_str(pdf_text[:5000])

    with open('entities_file.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)
    print("写入的数据：")
    print(rows)


def extract_text_from_all_pdfs(directory):
    all_texts = {}
    cnt = 0
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            pdf_text = extract_text_from_pdf(pdf_path)
            print('现在读取'+str(pdf_path))
            # print(pdf_text)
            print('现在将prompt交给gpt-4')
            output_relation(pdf_text)
            all_texts[filename] = pdf_text
            cnt += 1
            print(f'读取进度：{cnt}/105')
    print('一共读取了'+str(cnt)+'个文件，已完成')
    return all_texts
