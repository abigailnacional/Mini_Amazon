from app import create_app
import os

app = create_app()

@app.context_processor
def handle_context():
    return dict(os=os)
