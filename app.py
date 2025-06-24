import os
from app import create_app, db
from app.models import User, Class, Student, Schedule, Attendance, Event, Finance
from config import Config

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Class': Class,
        'Student': Student,
        'Schedule': Schedule,
        'Attendance': Attendance,
        'Event': Event,
        'Finance': Finance
    }

if __name__ == '__main__':
    app.run(debug=True)
