
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Question

from rest_framework.decorators import api_view, schema
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema
import random
import openai

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
        # question_type = request.POST['question_type']
        question_subject = request.POST['question_subject']
        question_levels = request.POST['question_levels']
        # question_marks = request.POST['question_marks']
        question_topic = request.POST['question_topic']
        new_question = Question(question=question, question_subject=question_subject, question_levels=question_levels, question_topic=question_topic)
        new_question.save()
        return redirect('add_questions')
    else:
        return render(request, 'add_questions.html')




class QuestionPaperSchema(AutoSchema):
    def get_operation_id(self, path, method):
        return 'generate_question_paper'

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
my_api_keys= "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"
openai.api_key = f"{my_api_keys}"

# views.py

import io
import os
import openai
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


# Authenticate OpenAI API with the API key
openai.api_key = "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"

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io

import random

def generate_question_paper(request):
    if request.method == 'POST':
        question_subject = request.POST['question_subject']
        # question_topic = request.POST['question_type']
        question_levels = request.POST['question_levels']
        # question_type = request.POST['question_type']

        # Check if there are any questions in the database for the given subject
        questions = Question.objects.filter(question_subject=question_subject)
        if questions.exists():
            # Select 10 random questions from the database
            questions = random.sample(list(questions), 10)
        else:
            # Generate a prompt for OpenAI API
            prompt = f"Generate 10 random questions on {question_subject}."

            # Call OpenAI API with the prompt
            response = openai.Completion.create(
                engine="davinci",
                prompt=prompt,
                max_tokens=1024,
                n=10,
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
                new_question = Question(
                    question=question,
                    question_subject=question_subject,
                    # question_type=question_type,
                    # question_topic=question_topic,
                    # bloom_taxonomy=bloom_taxonomy  # Save the selected bloom taxonomy levels for each question
                )
                new_question.save()

        # Limit the number of questions to 10
        questions = questions[:10]

        # Render the PDF template with the questions
        template_path = 'pdf_template.html'
        context = {'questions': questions}
        template = get_template(template_path)
        html = template.render(context)

        # Create a PDF file from the HTML content
        pdf_file = io.BytesIO()
        pisa.CreatePDF(io.StringIO(html), pdf_file)
        # print(f"there is the pdf_file{pdf_file}")
        # Return the PDF file as a response
        response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="question_paper.pdf"'
        # print(f"thare is the response{response}")
        return response

    return render(request, 'generate_question_paper.html')