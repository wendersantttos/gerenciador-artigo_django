from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os

# Helper function to load the response JSON file
def load_responses(file_path):
    """
    Loads the JSON file containing responses.
    Returns a dictionary or raises an exception if the file is invalid.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"O arquivo de respostas não foi encontrado: {file_path}")
    except json.JSONDecodeError:
        raise ValueError("O arquivo de respostas não é um JSON válido.")

@csrf_exempt
def chatbot(request):
    """
    Handles chatbot interactions via GET and POST requests.
    """
    if request.method == 'GET':
        # Render the chatbot interface (chatbot.html)
        return render(request, 'chatbot/chatbot.html')

    elif request.method == 'POST':
        try:
            # Parse request body as JSON
            data = json.loads(request.body.decode('utf-8'))
            question = data.get('question')

            # Validate if the question is provided
            if not question:
                return JsonResponse({'error': 'Pergunta inválida. Por favor, envie uma pergunta válida.'}, status=400)

            # Define the path to the JSON file with responses
            file_path = os.path.join(os.path.dirname(__file__), 'data', 'respostas.json')

            # Load the responses from the file
            respostas = load_responses(file_path)

            # Look up the response, case insensitive
            answer = respostas.get(question.lower(), 'Desculpe, não encontrei uma resposta para sua pergunta.')

            # Return the answer as JSON
            return JsonResponse({'answer': answer}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Erro ao processar a solicitação. Certifique-se de que o corpo da requisição é um JSON válido.'}, status=400)
        except FileNotFoundError as e:
            return JsonResponse({'error': str(e)}, status=500)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # If the method is not GET or POST, return a 405 error
    return JsonResponse({'error': 'Método não permitido.'}, status=405)
