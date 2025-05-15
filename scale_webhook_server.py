from flask import Flask, request
import subprocess
import logging
import os

# Ganti ini dengan direktori tempat file .tf kamu berada
TERRAFORM_DIR = "/home/bona/auto scaling"
LOG_FILE = "/home/bona/webhook_scale.log"

# Pastikan folder log ada
log_folder = os.path.dirname(LOG_FILE)
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# Setup Flask app
app = Flask(__name__)

# Konfigurasi logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')

@app.route('/')
def home():
    return "Flask server is running!"

@app.route('/scale', methods=['POST'])
def scale():
    try:
        data = request.get_json()
        alerts = data.get("alerts", [])
        if not alerts:
            logging.warning("Tidak ada alerts dalam payload")
            return "No alerts found", 400

        for alert in alerts:
            status = alert.get("status")
            name = alert.get("labels", {}).get("alertname", "")
            if status == "firing" and name == "HighCPUUsage":
                logging.info("Menerima alert: HighCPUUsage - Menjalankan Terraform")
                try:
                    result = subprocess.run(
                        ["terraform", "apply", "-auto-approve"], 
                        cwd=TERRAFORM_DIR,
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    logging.info("Terraform berhasil dijalankan:\n" + result.stdout)
                except subprocess.CalledProcessError as e:
                    logging.error(f"Terraform gagal dijalankan:\n{e.output}\nError: {e.stderr}")
                    return "Terraform execution failed", 500
                break

        return "", 200

    except Exception as e:
        logging.error(f"Error dalam memproses webhook: {e}")
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

