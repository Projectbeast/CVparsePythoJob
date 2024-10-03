import PyPDF2

def pdf_to_text(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

pdf_path = r'F:\Personal\Interview Preparation\Interview Preparation Sep-2021\Int\Interview Candiates Profiles\pdftotextsample\Rajestpdf.pdf'
pdf_text = pdf_to_text(pdf_path)
print(pdf_text)
