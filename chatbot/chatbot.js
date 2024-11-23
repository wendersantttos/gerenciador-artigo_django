// static/js/chatbot.js
document.addEventListener("DOMContentLoaded", function () {
    const chatInput = document.getElementById("chat-input");
    const chatButton = document.getElementById("send-button"); // Atualizado para coincidir com o ID correto do botão de envio
    const chatDisplay = document.getElementById("chat-messages");

    const attendants = ["Wender", "Erica", "Gabriel"];
    let currentAttendantIndex = 0;

    // Função para criar a HTML da mensagem
    function createMessage(content, isUserMessage = true) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add(isUserMessage ? "user" : "bot");
        messageDiv.classList.add("message");

        if (isUserMessage) {
            messageDiv.textContent = content;
        } else {
            messageDiv.innerHTML = `<strong>${content.pergunta}</strong><br>${content.resposta}`;
        }

        return messageDiv;
    }

    // Função para enviar a mensagem do usuário e obter resposta do backend
    async function sendMessage(userMessage) {
        try {
            // Exibir a mensagem do usuário
            chatDisplay.appendChild(createMessage(userMessage, true));

            // Mostrar "digitando..." enquanto espera a resposta
            const botMessage = document.createElement('div');
            botMessage.className = 'message bot typing';
            botMessage.innerText = `${attendants[currentAttendantIndex]} está digitando...`;
            chatDisplay.appendChild(botMessage);
            chatDisplay.scrollTop = chatDisplay.scrollHeight;

            // Enviar a pergunta ao backend
            const response = await fetch("/chatbot/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"), // Função que pega o token CSRF
                },
                body: JSON.stringify({ question: userMessage }),
            });

            const data = await response.json();

            // Atualizar a mensagem do bot com a resposta recebida
            setTimeout(() => {
                botMessage.classList.remove('typing');
                botMessage.innerText = `${attendants[currentAttendantIndex]}: ${data.answer}`;
                chatDisplay.scrollTop = chatDisplay.scrollHeight;

                if (currentAttendantIndex === attendants.length - 1) {
                    askForFeedback();
                }

                currentAttendantIndex = (currentAttendantIndex + 1) % attendants.length;
            }, 1000);

            // Limpar o campo de entrada
            chatInput.value = "";
        } catch (error) {
            console.error("Erro ao enviar mensagem:", error);
            // Exibir uma mensagem de erro caso haja falha na requisição
            chatDisplay.appendChild(createMessage("Desculpe, algo deu errado. Tente novamente.", false));
        }
    }

    // Evento para quando o botão de enviar for clicado
    chatButton.addEventListener("click", function () {
        const userMessage = chatInput.value.trim();
        if (userMessage) {
            sendMessage(userMessage); // Enviar a mensagem do usuário
        }
    });

    // Permitir envio ao pressionar "Enter" também
    chatInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && chatInput.value.trim()) {
            e.preventDefault(); // Evita a quebra de linha
            sendMessage(chatInput.value.trim());
        }
    });

    function askForFeedback() {
        chatDisplay.appendChild(createMessage("Você precisa de mais alguma coisa?", false));
        chatDisplay.scrollTop = chatDisplay.scrollHeight;

        setTimeout(() => {
            document.getElementById('chat-input-container').style.display = 'none';
            document.getElementById('rating-container').style.display = 'flex';
        }, 2000);
    }

    function sendRating() {
        const rating = document.getElementById('rating').value;
        chatDisplay.appendChild(createMessage(`Obrigado por sua avaliação de ${rating}!`, false));
        chatDisplay.scrollTop = chatDisplay.scrollHeight;

        document.getElementById('rating-container').style.display = 'none';
        document.getElementById('chat-input-container').style.display = 'flex';

        chatDisplay.appendChild(createMessage("Agradecemos por usar o nosso sistema!", false));
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }

    document.getElementById('send-rating').addEventListener('click', sendRating); // Adicionado para lidar com a avaliação
});

// Função para pegar o cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
