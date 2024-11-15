document.addEventListener("DOMContentLoaded", function() {
    // Asegúrate de que el valor del room-id esté disponible después de que el DOM esté cargado
    const roomId = document.getElementById("room_id").value;

    // Verifica si el roomId existe antes de intentar crear la conexión
    if (roomId) {
        const socket = new WebSocket(
            `wss://${window.location.host}/ws/room/${roomId}/`
        );

        socket.onopen = function(e) {
            console.log("WebSocket conectado.");
        };

        socket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            console.log("Mensaje recibido:", data.message);
        };

        socket.onclose = function(e) {
            console.error("WebSocket cerrado:", e);
        };

        socket.onerror = function(e) {
            console.error("Error en WebSocket:", e);
        };
    } else {
        console.error("No se pudo obtener el roomId.");
    }
});
