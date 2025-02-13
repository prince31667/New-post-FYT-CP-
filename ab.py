from flask import Flask, request, render_template_string
import requests
import time
import random

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Auto Comment - Updated Version</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, textarea { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Updated Auto Commenter</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="token_file" accept=".txt" required><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="number" name="interval_min" placeholder="Min Interval (seconds)" required><br>
        <input type="number" name="interval_max" placeholder="Max Interval (seconds)" required><br>
        <button type="submit">Start Commenting</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    token_file = request.files['token_file']
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']
    interval_min = int(request.form['interval_min'])
    interval_max = int(request.form['interval_max'])

    tokens = token_file.read().decode('utf-8').splitlines()
    comments = comment_file.read().decode('utf-8').splitlines()

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://graph.facebook.com/{post_id}/comments"
    success_count = 0
    token_index = 0

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for comment in comments:
        if token_index >= len(tokens):  # Reset token index if we reach the end
            token_index = 0
        
        token = tokens[token_index]
        token_index += 1  # Move to next token for next request

        payload = {'message': comment, 'access_token': token}

        response = requests.post(url, data=payload, headers=headers)

        if response.status_code == 200:
            success_count += 1
            print(f"✅ Comment Posted: {comment}")
        elif response.status_code == 400:
            print(f"❌ Invalid Token: {token}, skipping...")
            continue  # Skip to next comment
        else:
            print(f"⚠️ Error: {response.status_code}, skipping comment...")

        # Random delay between comments
        sleep_time = random.randint(interval_min, interval_max)
        print(f"⏳ Waiting {sleep_time} seconds before next comment...")
        time.sleep(sleep_time)

    return render_template_string(HTML_FORM, message=f"✅ {success_count} Comments Successfully Posted!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
