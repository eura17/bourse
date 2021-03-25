import socket

from app import app
from endpoints import simulation_endpoint

app.api.register_blueprint(blueprint=simulation_endpoint)

host = socket.gethostbyname(socket.gethostname())
app.run(host)
