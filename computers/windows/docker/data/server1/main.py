from flask import Flask, jsonify
import logging
import os
from datetime import datetime
import setproctitle

# Setup logging
log_file = os.path.join("\\\\host.lan\\Data", "logs", "server_1.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Named the process for easier identification
setproctitle.setproctitle("server1")  

app = Flask(__name__)

@app.route('/')
def home():
    logging.info("Request received at route '/'")
    return 'Hello, this is a simple HTTP server!'

@app.route('/test')
def test():
    logging.info("Request received at route '/test'")
    return jsonify({"status": "success", "message": "Test endpoint reached!"})

if __name__ == '__main__':
    port = 6000
    logging.info(f"Server started on port {port} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    app.run(host='0.0.0.0', port=port)
