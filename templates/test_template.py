from flask import Flask, render_template, session
import os

app = Flask(__name__, template_folder='.')
app.secret_key = 'test'

@app.route('/test')
def test():
    session['user_id'] = 1
    session['name'] = 'Test User'
    session['role'] = 'admin'
    return render_template('base.html')

if __name__ == '__main__':
    with app.test_request_context('/test'):
        try:
            print(app.dispatch_request())
            print("Template rendered successfully!")
        except Exception as e:
            print(f"Error rendering template: {e}")
