from flask import Flask, request, jsonify
app = Flask(__name__)



# --------------------------------------------------------------------
# Run the Flask application
# --------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)