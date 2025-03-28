from flask import Flask, request, redirect, send_file
import csv
import os
from datetime import datetime

app = Flask(__name__)

TRACK_CSV = 'email_tracking_log.csv'
UNSUBSCRIBE_FILE = 'unsubscribed.csv'

# Create CSV headers if not exists
if not os.path.exists(TRACK_CSV):
    with open(TRACK_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['email', 'event', 'timestamp'])

if not os.path.exists(UNSUBSCRIBE_FILE):
    with open(UNSUBSCRIBE_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['email'])


def log_event(email, event):
    with open(TRACK_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([email, event, datetime.now().isoformat()])


@app.route('/track_open')
def track_open():
    email = request.args.get('email')
    if email:
        log_event(email, 'open')
    return send_file('pixel.png', mimetype='image/png')  # transparent 1x1 image


@app.route('/redirect')
def redirect_click():
    email = request.args.get('email')
    url = request.args.get('url')
    if email:
        log_event(email, 'click')
    return redirect(url)


@app.route('/unsubscribe')
def unsubscribe():
    email = request.args.get('email')
    if email:
        with open(UNSUBSCRIBE_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([email])
        log_event(email, 'unsubscribe')
    return "You have been unsubscribed."


if __name__ == '__main__':
    app.run(debug=True)


# --- Create pixel.png ---
# Save a 1x1 transparent PNG file as "pixel.png" in the same folder. You can use Pillow:

# from PIL import Image
# img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
# img.save('pixel.png')
