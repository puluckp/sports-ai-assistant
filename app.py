from flask import Flask, request, jsonify
from pyngrok import ngrok
from agent import get_response

app = Flask(__name__)

@app.route("/")
def home():
    return '''
<!DOCTYPE html>
<html>
<head><title>My Agent</title>
<style>
  body { font-family: sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; }
  #chat { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 10px; margin-bottom: 10px; border-radius: 8px; }
  .user { text-align: right; margin: 8px 0; }
  .agent { text-align: left; margin: 8px 0; color: #333; }
  input { width: 80%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
  button { padding: 8px 16px; background: #000; color: white; border: none; border-radius: 4px; cursor: pointer; }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
</head>
<body>
  <h2>My Agent</h2>
  <div id="chat"></div>
  <input id="input" placeholder="Ask something..." onkeydown="if(event.key===\'Enter\') send()" />
  <button onclick="send()">Send</button>
<script>
function send() {
  const msg = document.getElementById("input").value;
  if (!msg) return;
  const chat = document.getElementById("chat");
  chat.innerHTML += `<div class="user"><b>You:</b> ${msg}</div>`;
  document.getElementById("input").value = "";
  fetch("/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message: msg})
  })
  .then(r => r.json())
  .then(data => {
    chat.innerHTML += `<div class="agent"><b>Agent:</b> ${marked.parse(data.reply)}</div>`;
    chat.scrollTop = chat.scrollHeight;
  });
}
</script>
</body>
</html>
'''

previous_response_id = None


@app.route("/chat", methods=["POST"])
def chat():
    global previous_response_id
    data = request.json
    user_message = data["message"]
    reply, previous_response_id = get_response(user_message, previous_response_id)
    return jsonify({"reply": reply})


from dotenv import load_dotenv
import os

load_dotenv()
my_ngrok_token=os.environ.get("NGROK_TOKEN")

ngrok.set_auth_token(my_ngrok_token)
public_url = ngrok.connect(5000)
print("Your URL:", public_url)
app.run(debug=False)
