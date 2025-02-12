from flask import Flask, request, render_template_string
import requests
import time
import re

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Commenter</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, textarea { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Created by Rocky Roy</h1>
    <form method="POST" action="/submit">
        <label>Enter Facebook Cookies:</label>
        <textarea name="cookies" placeholder="Paste your Facebook cookies here" required></textarea><br>

        <label>Upload Comments File:</label>
        <input type="file" name="comment_file" accept=".txt" required><br>

        <label>Enter Facebook Post URL:</label>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>

        <label>Set Time Delay (Seconds):</label>
        <input type="number" name="interval" placeholder="Interval in Seconds (e.g., 5)" required><br>

        <button type="submit">Submit</button>
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
    cookies = request.form['cookies'].strip()
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    comments = comment_file.read().decode('utf-8').splitlines()

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': cookies
    })

    # Extract fb_dtsg & jazoest
    home_page = session.get("https://m.facebook.com/")
    fb_dtsg = re.search(r'name="fb_dtsg" value="(.*?)"', home_page.text)
    jazoest = re.search(r'name="jazoest" value="(.*?)"', home_page.text)

    if not fb_dtsg or not jazoest:
        return render_template_string(HTML_FORM, message="❌ Failed to extract security tokens!")

    fb_dtsg = fb_dtsg.group(1)
    jazoest = jazoest.group(1)

    comment_url = f"https://m.facebook.com/a/comment.php?fs=8&fr=%2Fprofile.php&dpr=1"
    success_count = 0

    for comment in comments:
        payload = {
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest,
            'comment_text': comment,
            'ft_ent_identifier': post_id
        }
        response = session.post(comment_url, data=payload)
        if "error" not in response.text:
            success_count += 1
        time.sleep(interval)

    return render_template_string(HTML_FORM, message=f"✅ {success_count} Comments Successfully Posted!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
