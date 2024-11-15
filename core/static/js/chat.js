document.addEventListener('DOMContentLoaded', () => {
    // Definir URL del WebSocket
    const socketUrl = `wss://inmersion-production.up.railway.app/ws/room/${room_id}/`;

    // Establecer la conexión WebSocket
    const socket = new WebSocket(socketUrl);

    // Conexión abierta
    socket.onopen = function () {
        console.log("Conexión WebSocket establecida para la sala:", room_id);
    };

    // Recibir mensajes
    socket.onmessage = function (event) {
        const messageData = JSON.parse(event.data);
        console.log("Mensaje recibido:", messageData.message);

        // Mostrar el mensaje en el contenedor
        const messageContainer = document.getElementById('boxMessages');
        const messageElement = document.createElement('div');
        messageElement.textContent = messageData.message;
        messageContainer.appendChild(messageElement);

        // Scroll hacia el último mensaje
        messageContainer.scrollTop = messageContainer.scrollHeight;
    };

    // Conexión cerrada
    socket.onclose = function (event) {
        console.log("Conexión WebSocket cerrada:", event);
    };

    // Manejar errores
    socket.onerror = function (error) {
        console.error("Error en WebSocket:", error);
    };

    // Enviar mensaje al hacer clic en "Enviar"
    document.getElementById('btnMessage').addEventListener('click', () => {
        const messageInput = document.getElementById('inputMessage');
        const message = messageInput.value.trim();

        if (message) {
            socket.send(JSON.stringify({ 'message': message }));
            messageInput.value = ''; // Limpiar el campo
        }
    });

    // Enviar mensaje al presionar "Enter"
    document.getElementById('inputMessage').addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault(); // Evitar envío de formulario
            document.getElementById('btnMessage').click(); // Simular clic
        }
    });
});
