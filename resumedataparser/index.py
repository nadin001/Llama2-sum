import os
import csv
import json
import re
import subprocess
import docx2txt
import nltk
from pdfminer.high_level import extract_text


nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

RESERVED_WORDS = [
    'school',
    'college',
    'univers',
    'academy',
    'faculty',
    'institute',
    'faculdades',
    'Schola',
    'schule',
    'lise',
    'lyceum',
    'lycee',
    'polytechnic',
    'kolej',
    'ünivers',
    'okul',
]

SPECIAL_EDUCATION_WORDS = [
    "of",
    "city",
]

SKILL_NAMES = [
    'highlights',
    'skills',
    'languages',
    'environment'
]

SKILLS_CSV_FILE = 'skills.csv'


PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')

def load_local_skills():
    with open(SKILLS_CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        skills = {row[0].lower(): int(row[1]) for row in reader}
    return skills

LOCAL_SKILLS_DB = load_local_skills()

def skill_exists(skill):
    return skill.lower() in LOCAL_SKILLS_DB

def extract_text_from_docx(docx_path):
    txt = docx2txt.process(docx_path)
    if txt:
        return txt.replace('\t', ' ')
    return None

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def doc_to_text_catdoc(file_path):
    try:
        process = subprocess.Popen(
            ['catdoc', '-w', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    except (
        FileNotFoundError,
        ValueError,
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
    ) as err:
        return (None, str(err))
    else:
        stdout, stderr = process.communicate()
        return (stdout.strip(), stderr.strip())

def clear_str(str):
    string_encode = str.encode("ascii", "ignore")
    string_decode = string_encode.decode()
    string_decode
    return string_decode

def extract_names(txt):
    person_names = []
    for sent in nltk.sent_tokenize(txt):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label') and chunk.label() == 'PERSON':
                person_names.append(
                    ' '.join(chunk_leave[0] for chunk_leave in chunk.leaves())
                )
    return person_names

def extract_phone_number(resume_text):
    phone = re.findall(PHONE_REG, resume_text)
    if phone:
        number = ''.join(phone[0])
        if resume_text.find(number) >= 0 and len(number) < 16:
            return number
    return None

def extract_emails(resume_text):
    return re.findall(EMAIL_REG, resume_text)

def extract_skills(input_text):
    stop_words = set(nltk.corpus.stopwords.words('english'))
    word_tokens = nltk.tokenize.word_tokenize(input_text)


    filtered_tokens = [w for w in word_tokens if w not in stop_words]

    found_skills = set()

    count = 0
    for token in filtered_tokens:
        if token.lower() in SKILL_NAMES:
            count = 10
        else:
            if count > 0:
                count -= 1
                if skill_exists(token.lower()) and len(token) != 1:
                    found_skills.add(clear_str(token.lower()))

    output = ""
    for word in found_skills:
        output += word
        output += ", "
    return output


def extract_education(input_text):
    organizations = []
    for sent in nltk.sent_tokenize(input_text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label') and chunk.label() == 'ORGANIZATION':
                organizations.append(' '.join(clear_str(c[0]) for c in chunk.leaves()))

    education = set()
    for org in organizations:
        for word in RESERVED_WORDS:
            if org.lower().find(word) >= 0:
                for stopWord in SPECIAL_EDUCATION_WORDS:
                    wordsOrg = org.lower().split(" ")
                    if stopWord in wordsOrg and len(wordsOrg) == 2:
                        wordsOrg.remove(stopWord)
                        education.add(wordsOrg[0])
                    else:
                        education.add(org.lower())

    resultEducation = set()
    for org1 in education:
        twink = 0
        for org2 in education:
            if org1 in org2 and org1 != org2:
                twink = 1
        if twink == 0:
            resultEducation.add(org1)

    output = ""
    for word in resultEducation:
        output += word
        output += ", "
    return output

def extract_context(input_text):
    currentCntext = set()
    for sent in nltk.sent_tokenize(input_text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label') and (chunk.label() == 'ORGANIZATION' or chunk.label() == "PERSON"):
                stop_words = set(nltk.corpus.stopwords.words('english'))
                word_tokens = nltk.tokenize.word_tokenize(sent)
                filtered_tokens = [w for w in word_tokens if w not in stop_words]
                str = ' '.join(filtered_tokens)
                string_encode = str.encode("ascii", "ignore")
                string_decode = string_encode.decode()
                currentCntext.add(string_decode)

    output = ""
    for word in currentCntext:
        output += word
        output += ". "
    return output

def process_resume(file_path):
    file_extension = file_path.split('.')[-1].lower()

    if file_extension == 'pdf':
        resume_text = extract_text_from_pdf(file_path)
    elif file_extension == 'docx':
        resume_text = extract_text_from_docx(file_path)
    else:
        return None, None, None

    if resume_text:
        skills = extract_skills(resume_text)
        education = extract_education(resume_text)
        context = extract_context(resume_text)
        return skills, education, context
    else:
        return None, None, None

def save_to_csv(data, csv_file='output_data.csv'):
    with open(csv_file, 'a', newline='') as csvfile:
        fieldnames = ['Name', 'Skills', 'Education', 'Context', 'Text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)


        if os.stat(csv_file).st_size == 0:
            writer.writeheader()


        writer.writerow(data)


resumes_folder = 'resumes'


DEFAULT_SYSTEM_PROMPT = """
Resume with skills
""".strip()




def generate_training_prompt(
    conversation: str, summary: str, system_prompt: str = DEFAULT_SYSTEM_PROMPT
) -> str:
    return f"""### Instruction: {system_prompt}


### Resume:
{conversation.strip()}


### Skills:
{summary}
""".strip()


for filename in os.listdir(resumes_folder):
    if filename.endswith('.pdf'):
        file_path = os.path.join(resumes_folder, filename)


        skills, education, context = process_resume(file_path)

        if (skills == None or education == None or context == None):
            if (not isinstance(skills, str) or not isinstance(education, str) or not isinstance(context, str)):
                continue


        name = os.path.splitext(filename)[0].replace('_', ' ')

        text = generate_training_prompt(context, skills)


        data = {'Name': name, 'Skills': skills, 'Education': education, 'Context': context, 'Text': text}

        save_to_csv(data)

print("Processing completed. Data saved to output_data.csv.")
