# --- 📌 PART 1: TRACKING BACKEND (Flask App) ---

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


# --- 📌 PART 2: Create pixel.png ---
# Save a 1x1 transparent PNG file as "pixel.png" in the same folder. You can use Pillow:

# from PIL import Image
# img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
# img.save('pixel.png')


# --- 📌 PART 3: EMBEDDED HTML (Streamlit Email Template Usage) ---

# Inside your Streamlit email sending code:
# (replace `yourdomain.com` with where your Flask app is hosted)

# email_html = f'''
# <html>
# <body>
#   <h2>Hello {{name}}</h2>
#   <p>We're glad to have you!</p>
#   <img src="https://yourdomain.com/track_open?email={{email}}" width="1" height="1">
#   <br><a href="https://yourdomain.com/redirect?email={{email}}&url=https://productlink.com">Click Here</a>
#   <br><a href="https://yourdomain.com/unsubscribe?email={{email}}">Unsubscribe</a>
# </body>
# </html>
# '''

# You can customize this in the Streamlit app when composing emails.


# --- 📌 PART 4: DELIVERY REPORT BUILDER ---
# After emails are sent and logs are collected:

def build_delivery_report(csv_emails):
    import pandas as pd

    df = pd.read_csv(csv_emails)  # original csv with email list
    df['opened'] = False
    df['clicked'] = False
    df['unsubscribed'] = False

    logs = pd.read_csv('email_tracking_log.csv')
    unsubscribed = pd.read_csv('unsubscribed.csv')

    for idx, row in df.iterrows():
        email = row['email']
        user_logs = logs[logs['email'] == email]
        if 'open' in user_logs['event'].values:
            df.at[idx, 'opened'] = True
        if 'click' in user_logs['event'].values:
            df.at[idx, 'clicked'] = True
        if email in unsubscribed['email'].values:
            df.at[idx, 'unsubscribed'] = True

    df.to_csv('delivery_report.csv', index=False)
    print("Delivery report saved as delivery_report.csv")
