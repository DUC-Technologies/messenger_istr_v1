def get_html_stub_chat_dev():
    html = """<!DOCTYPE html>
    <html>
    <head>
        <title>Chat</title>
        <style>
            body { font-family: Arial, sans-serif; }
            #chatId, #token, #messageText { margin-bottom: 10px; }
            form > label { display: block; }
            #messages { list-style-type: none; padding: 0; }
            #messages li { margin-bottom: 5px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
            form { margin-bottom: 20px; }
            button { cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <label>Chat ID: <input type="text" id="chatId" autocomplete="off" value="foo"/></label>
            <label>Token: <input type="text" id="token" autocomplete="off" value="some-key-token"/></label>
            <button type="button" onclick="connect(event)">Connect</button>
            <hr>
            <label>Message: <input type="text" id="messageText" autocomplete="off" onkeypress="handleEnter(event)"/></label>
            <button type="submit">Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
        var ws = null;
            function connect(event) {
                if (ws !== null && ws.readyState === WebSocket.OPEN) {
                    console.log("Соединение уже установлено.");
                    event.preventDefault();
                    return;
                }
                var chatId = document.getElementById("chatId");
                var token = document.getElementById("token");
                ws = new WebSocket("ws://localhost:46020/messenger/chats/" + chatId.value + "/ws?token=" + token.value);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages');
                    var message = document.createElement('li');
                    var content = document.createTextNode(event.data);
                    message.appendChild(content);
                    messages.appendChild(message);
                };
                event.preventDefault();
            }
            function sendMessage(event) {
                if (ws === null || ws.readyState !== WebSocket.OPEN) {
                    console.error("Соединение не установлено.");
                    event.preventDefault();
                    return;
                }
                var input = document.getElementById("messageText");
                ws.send(input.value);
                input.value = '';
                event.preventDefault();
            }
            function handleEnter(event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                    sendMessage(event);
                }
            }
        </script>
    </body>
    </html>

    """
    return html
