# chatbot/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os

@csrf_exempt
def chatbot(request):
    if request.method == 'GET':
        return render(request, 'chatbot/chatbot.html')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question')
            if question:
                # Carregar o arquivo JSON com as respostas
                with open(os.path.join(os.path.dirname(__file__), 'respostas.json'), 'r', encoding='utf-8') as f:
                    respostas = json.load(f)
                
                # Procurar a resposta no JSON
                answer = respostas.get(question.lower(), 'Desculpe, não encontrei uma resposta para sua pergunta.')
                response = {'answer': answer}
            else:
                response = {'answer': 'Pergunta inválida.'}
        except json.JSONDecodeError:
            response = {'answer': 'Erro ao decodificar JSON.'}
        
        return JsonResponse(response)
    
    return JsonResponse({'error': 'Método não permitido.'}, status=405)
