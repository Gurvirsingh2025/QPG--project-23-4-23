
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Question

from rest_framework.decorators import api_view, schema
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema
import random
import openai
from .config import API_KEY 

# Create your views here.

def homePage(request):
    return render(request,'index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error_message = 'Invalid username or password'
    else:
        error_message = ''
    return render(request, 'login.html', {'error_message': error_message})

def contect_us(request):
    return render(request, 'contect_us.html')

def about_us(request):
    return render(request,'about_us.html')
 
from django.shortcuts import render


# def generate_question_paper(request):
#     if request.method == 'POST':
#         # Retrieve form data and generate question paper
#         questions = Question.objects.all()

#         # ...
#         return render(request, 'question_paper.html', {'questions': questions})
#     else:
#         return render(request, 'generate_question_paper.html')

def add_questions(request):
    if request.method == 'POST':
        question = request.POST['question']
        question_type = request.POST['question_type']
        question_subject = request.POST['question_subject']
        question_levels = request.POST['question_levels']
        question_marks = request.POST['question_marks']
        question_topic = request.POST['question_topic']
        new_question = Question(question=question, question_subject=question_subject, question_levels=question_levels, question_topic=question_topic, question_marks=question_marks, question_type=question_type)
        new_question.save()
        fields = ['question_subject', 'question_type', 'question_levels', 'question_marks', 'question_topic']
        distinct_values = {}
        for field in fields:
            values = Question.objects.values(field).distinct()
            distinct_values[field] = [value[field] for value in values]
        return render(request, 'add_questions.html', {'distinct_values': distinct_values})
    else:
        fields = ['question_subject', 'question_type', 'question_levels', 'question_marks', 'question_topic']
        distinct_values = {}
        for field in fields:
            values = Question.objects.values(field).distinct()
            distinct_values[field] = [value[field] for value in values]
        return render(request, 'add_questions.html', {'distinct_values': distinct_values})




# class QuestionPaperSchema(AutoSchema):
#     def get_operation_id(self, path, method):
#         return 'generate_question_paper'

# @api_view(['POST'])
# @schema(QuestionPaperSchema())
# def generate_question_paper(request):
#     """
#     Generate a random question paper based on the selected criteria.
#     """
#     # Retrieve form data and generate question paper
#     # ...

#     # Retrieve a set of questions from the database based on the selected criteria
#     questions = Question.objects.filter(question_subject=subject, question_levels=difficulty, question_marks__gte=marks)

#     # Shuffle the questions and select the first n questions to include in the question paper
#     shuffled_questions = list(questions)
#     random.shuffle(shuffled_questions)
#     selected_questions = shuffled_questions[:num_questions]

#     # Format the selected questions into a printable question paper
#     question_paper = ''
#     for i, question in enumerate(selected_questions):
#         question_paper += f'{i+1}. {question.question}\n\n'

#     return Response({'question_paper': question_paper})



# Authenticate OpenAI API with the API key
openai.api_key = f"{API_KEY}"

# views.py

import io
import os
import openai
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa



from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io

import random

def generate_question_paper(request):
    if request.method == 'POST':
        question_subject = request.POST['question_subject']
        # question_topic = request.POST['question_topic']
        question_levels = request.POST['question_levels']
        question_type = request.POST['question_type']


        # Define the percentage of each level for each difficulty level
        if question_levels == 'Low':
            remember_pct = 0.25
            understand_pct = 0.25
            evaluate_pct = 0.3
            create_pct = 0.2
        elif question_levels == 'Normal':
            remember_pct = 0.4
            understand_pct = 0.3
            evaluate_pct = 0.2
            create_pct = 0.1
        elif question_levels == 'High':
            remember_pct = 0.2
            understand_pct = 0.2
            evaluate_pct = 0.3
            create_pct = 0.3

   
        # Check if there are any questions in the database for the given subject
        questions = Question.objects.filter(question_subject=question_subject,question_type=question_type)
        if questions.exists():
            # Select 20 random questions from the database
            questions = random.sample(list(questions), 20)
        else:
            # Generate a prompt for OpenAI API
            prompt = f"Generate 10 random {question_type} questions on {question_subject} on random bloom taxonomy chose according to levels."

            # Call OpenAI API with the prompt
            response = openai.Completion.create(
                engine="davinci",
                prompt=prompt,
                max_tokens=1024,
                n=20,
                stop=None,
                temperature=0.5,  
            )

            # Parse the response and extract the questions
            raw_questions = response.choices[0].text.split('\n')

            # Modify the questions
            questions = []
            for raw_question in raw_questions:
                # Remove any leading or trailing whitespace
                raw_question = raw_question.strip()

                # Skip any blank lines or repeated lines
                if not raw_question or raw_question in questions:
                    continue

                # Remove any question numbers (e.g. "1. What is...")
                if raw_question.startswith('1. '):
                    raw_question = raw_question[3:]

                # Add the modified question to the list
                questions.append(raw_question[:100])  # Limit the question length to 100 characters


        # Save the questions in the database (if they don't already exist)
        for question in questions:
            if not Question.objects.filter(question=question).exists():
                # Determine the Bloom's taxonomy level of the question
                level = random.choices(
                    ['Remember', 'Understand', 'Evaluate', 'Create'],
                    weights=[remember_pct, understand_pct, evaluate_pct, create_pct]
                )[0]
                new_question = Question(
                    question=question,
                    question_subject=question_subject,
                    question_type=question_type,
                    question_marks=1,
                    # question_topic=question_topic,
                    question_levels=question_levels  # Save the selected bloom taxonomy levels for each question
                )
                new_question.save()


        # Limit the number of questions to 10
        questions = questions[:20]

        # Divide the questions into three sections
        section_a_questions = questions[1:5]
        section_b_questions = questions[5:10]
        section_c_questions = questions[10:15]
        section_d_questions = questions[15:20]

        # Add fill in the blanks, true/false, and full form questions to Section A
        fill_in_the_blanks_question = Question.objects.filter(question_subject=question_subject, question_type='fill_in_blanks').order_by('?').first()
        true_false_question = Question.objects.filter(question_subject=question_subject, question_type='True_False').order_by('?').first()
        full_form_question = Question.objects.filter(question_subject=question_subject, question_type='full_form').order_by('?').first()
        section_a_questions.extend([fill_in_the_blanks_question, true_false_question, full_form_question])

        # Shuffle the questions in each section
        random.shuffle(section_a_questions)
        random.shuffle(section_b_questions)
        random.shuffle(section_c_questions)
        random.shuffle(section_d_questions)

        # Render the PDF template with the questions
        template_path = 'pdf_template.html'
        context = {
            'section1_questions': section_a_questions,
                'section2_questions': section_b_questions,
                'section3_questions': section_c_questions,
                'sectionA_questions': section_d_questions
        }
        template = get_template(template_path)
        html = template.render(context)


        # # Render the PDF template with the questions
        # template_path = 'pdf_template.html'
        # context = {'questions': questions}
        # template = get_template(template_path)
        # html = template.render(context)

        # Create a PDF file from the HTML content
        pdf_file = io.BytesIO()
        pisa.CreatePDF(io.StringIO(html), pdf_file)

        # Return the PDF file as a response
        response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="question_paper.pdf"'

        return response
    # to send data to tamplate for rander the questions whose save in database.
    fields = ['question_subject', 'question_type', 'question_levels', 'question_marks', 'question_topic']
    distinct_values = {}
    for field in fields:
        values = Question.objects.values(field).distinct()
        distinct_values[field] = [value[field] for value in values]
    return render(request, 'generate_question_paper.html', {'distinct_values': distinct_values})

    # return render(request, 'generate_question_paper.html')
# def generate_question_paper(request):
#     if request.method == 'POST':
#         question_subject = request.POST['question_subject']
#         question_type = request.POST['question_type']
#         question_levels = request.POST['question_levels']

#         # Check if there are any questions in the database for the given subject, type and levels
#         questions = Question.objects.filter(question_subject=question_subject,question_levels=question_levels)

#         if questions.exists():
#             # Select 15 random questions from the database
#             questions = random.sample(list(questions), 15)
#         else:
#             # Generate a prompt for OpenAI API
#             prompt = f"Generate 15 random questions on {question_subject} of {question_type} type and {question_levels} level."

#             # Call OpenAI API with the prompt
#             response = openai.Completion.create(
#                 engine="davinci",
#                 prompt=prompt,
#                 max_tokens=1024,
#                 n=15,
#                 stop=None,
#                 temperature=0.5,
#             )

#             # Parse the response and extract the questions
#             raw_questions = response.choices[0].text.split('\n')

#             # Modify the questions
#             questions = []
#             for raw_question in raw_questions:
#                 # Remove any leading or trailing whitespace
#                 raw_question = raw_question.strip()

#                 # Skip any blank lines or repeated lines
#                 if not raw_question or raw_question in questions:
#                     continue

#                 # Remove any question numbers (e.g. "1. What is...")
#                 if raw_question.startswith('1. '):
#                     raw_question = raw_question[3:]

#                 # Add the modified question to the list
#                 questions.append(raw_question[:100])  # Limit the question length to 100 characters

#             # Assign bloom taxonomy levels to each question
#             if question_levels == "low":
#                 question_level_dict = {"remember": 0.25, "understand": 0.25, "evaluate": 0.30, "create": 0.20}
#             elif question_levels == "normal":
#                 question_level_dict = {"remember": 0.40, "understand": 0.30, "evaluate": 0.20, "create": 0.10}
#             else:  # question_levels == "hard"
#                 question_level_dict = {"remember": 0.20, "understand": 0.20, "evaluate": 0.30, "create": 0.30}

#             question_levels = []
#             for level, weight in question_level_dict.items():
#                 question_levels.extend([level] * int(weight * 100))

#             # Assign question level to each question
#             for question in questions:
#                 question.question_levels = random.choice(question_levels)

#         # Limit the number of questions to 15
#         questions = questions[:15]

#         # Limit the number of questions to 5 for each section
#         # section1_questions = [q for q in questions if q.question_type == "fill_in_the_blank"][:5]
#         # section2_questions = [q for q in questions if q.question_type == "true_false"][:5]
#         # section3_questions = [q for q in questions if q.question_type == "full_form"][:5]

#         # Render the PDF template with the questions
#         template_path = 'pdf_template.html'
#         context = {
#             'section1_questions': section1_questions,
#             'section2_questions': section2_questions,
#             'section3_questions': section3_questions
#         }
#         template = get_template(template_path)
#         html = template.render(context)

#          # Create a PDF file from the HTML content
#         pdf_file = io.BytesIO()
#         pisa.CreatePDF(io.StringIO(html), pdf_file)

#         # Return the PDF file as a response
#         response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
#         response['Content-Disposition'] = 'inline; filename="question_paper.pdf"'

#         return response
#     # to send data to tamplate for rander the questions whose save in database.
#     fields = ['question_subject', 'question_type', 'question_levels', 'question_marks', 'question_topic']
#     distinct_values = {}
#     for field in fields:
#         values = Question.objects.values(field).distinct()
#         distinct_values[field] = [value[field] for value in values]
#     return render(request, 'generate_question_paper.html', {'distinct_values': distinct_values})





