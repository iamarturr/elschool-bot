from sanic import Sanic, response
from sanic.response import json, html, text
import asyncio
import json
import urllib.parse
from sanic import Sanic
from sanic_jinja2 import SanicJinja2
import socket


app = Sanic(name="g")
jinja = SanicJinja2(app, pkg_name="pkg")

@app.route('/')
async def form(request):
    return text("hello world")

@app.post('/api/')
async def form(request):
    js = request.json
    js = sorted(js, key=lambda d: d['name'])
    js = {"result": js}
    return jinja.render("example.html", request, lists=js)

if __name__ == "__main__":
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    app.run(host=str(local_ip), port=8000)