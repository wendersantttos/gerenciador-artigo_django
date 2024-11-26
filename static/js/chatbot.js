document.addEventListener("DOMContentLoaded", function () {
    const chatInput = document.getElementById("chat-input");
    const chatButton = document.getElementById("send-button");
    const chatDisplay = document.getElementById("chat-messages");

    const attendants = [
        { name: "Wender", avatar: "wender-avatar.png" },
        { name: "Erica", avatar: "erica-avatar.png" },
        { name: "Gabriel", avatar: "gabriel-avatar.png" }
    ];
    let currentAttendantIndex = 0;

    // Função para criar a HTML da mensagem
    function createMessage(content, isUserMessage = true) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", isUserMessage ? "user" : "bot");

        const avatar = document.createElement("img");
        avatar.classList.add("avatar");
        avatar.src = attendants[currentAttendantIndex].avatar;

        const textDiv = document.createElement("div");
        textDiv.classList.add("message-text");

        textDiv.innerHTML = isUserMessage 
            ? content 
            : `<strong>${attendants[currentAttendantIndex].name}:</strong> ${content}`;

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(textDiv);
        return messageDiv;
    }

    // Função para rolar automaticamente
    function scrollToBottom() {
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }

    // Função para enviar a mensagem do usuário e obter a resposta
    async function sendMessage(userMessage) {
        try {
            // Exibir a mensagem do usuário
            chatDisplay.appendChild(createMessage(userMessage, true));
            scrollToBottom();

            // Mostrar "digitando..." enquanto espera a resposta
            const typingMessage = document.createElement("div");
            typingMessage.className = "message bot typing";
            typingMessage.innerText = `${attendants[currentAttendantIndex].name} está digitando...`;
            chatDisplay.appendChild(typingMessage);
            scrollToBottom();

            // Enviar a pergunta ao backend
            const response = await fetch("/chatbot/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({ question: userMessage }),
            });

            const data = await response.json();

            // Atualizar a mensagem do bot com a resposta
            setTimeout(() => {
                chatDisplay.removeChild(typingMessage);
                chatDisplay.appendChild(createMessage(data.answer, false));
                scrollToBottom();

                // Alternar entre atendentes e solicitar feedback
                currentAttendantIndex = (currentAttendantIndex + 1) % attendants.length;
                if (currentAttendantIndex === 0) askForFeedback();
            }, 1000);

            // Limpar o campo de entrada
            chatInput.value = "";
        } catch (error) {
            console.error("Erro ao enviar mensagem:", error);
            chatDisplay.appendChild(createMessage("Desculpe, algo deu errado. Tente novamente.", false));
            scrollToBottom();
        }
    }

    // Evento para quando o botão de enviar for clicado
    chatButton.addEventListener("click", function () {
        const userMessage = chatInput.value.trim();
        if (userMessage) sendMessage(userMessage);
    });

    // Permitir envio ao pressionar "Enter"
    chatInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && chatInput.value.trim()) {
            e.preventDefault(); // Evita a quebra de linha
            sendMessage(chatInput.value.trim());
        }
    });

    // Função para solicitar feedback ao usuário
    function askForFeedback() {
        const feedbackMessage = createMessage("Você precisa de mais alguma coisa?", false);
        chatDisplay.appendChild(feedbackMessage);
        scrollToBottom();

        setTimeout(() => {
            document.getElementById("chat-input-container").style.display = "none";
            document.getElementById("rating-container").style.display = "flex";
        }, 2000);
    }

    // Função para enviar a avaliação do usuário
    function sendRating() {
        const rating = document.getElementById("rating").value;
        const thankYouMessage = createMessage(`Obrigado por sua avaliação de ${rating}!`, false);
        chatDisplay.appendChild(thankYouMessage);
        scrollToBottom();

        setTimeout(() => {
            const appreciationMessage = createMessage(
                `Agradecemos sua opinião! ${rating >= 4 ? "Ficamos felizes que tenha gostado!" : "Vamos melhorar para você!"}`,
                false
            );
            chatDisplay.appendChild(appreciationMessage);
            scrollToBottom();

            document.getElementById("rating-container").style.display = "none";
            document.getElementById("chat-input-container").style.display = "flex";

            chatDisplay.appendChild(createMessage("Agradecemos por usar o nosso sistema!", false));
            scrollToBottom();
        }, 1000);
    }

    // Evento para enviar a avaliação
    document.getElementById("send-rating").addEventListener("click", sendRating);
});

// Função para pegar o cookie CSRF
function getCookie(name) {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(`${name}=`)) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return null;
}
