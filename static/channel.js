document.addEventListener('DOMContentLoaded', () => {

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', () => {

        socket.emit('joined');

        document.querySelector('#newChannel').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });

        document.querySelector('#leave').addEventListener('click', () => {
            socket.emit('left');

            localStorage.removeItem('last_channel');
            window.location.replace('/');
        })

        document.querySelector('#logout').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });

        document.getElementById("send-button").onclick = () => {
            let timestamp = new Date;
            timestamp = timestamp.toLocaleTimeString();

            let msg = document.getElementById("comment").value;

            socket.emit('send message', msg, timestamp);

            document.getElementById("comment").value = '';
        }; 
    });
    
    socket.on('status', data => {
        const row = `${data.msg}`;
        document.querySelector('#chat').value += row + '\n';

        localStorage.setItem('last_channel', data.channel);
    })

    socket.on('announce message', data => {

        const row = `${data.user}` + ' at ' + `${data.timestamp}:` + ` ${data.msg}`;
        document.querySelector('#chat').value += row + '\n';
    });
});