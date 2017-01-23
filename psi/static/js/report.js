var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function () {
    socket.emit('dashboard connected', {data: 'I\'m connected!'});
});
socket.on('refresh dashboard', function(data){
    console.log("data received from server: " + data);
});
$("#send_to_back").on("click", function () {
    socket.emit('refresh dashboard', {data: 'Change data range to month'});
});