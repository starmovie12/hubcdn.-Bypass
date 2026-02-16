import os
import time
import base64
import re
import cloudscraper
from flask import Flask, request, jsonify
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

def get_real_target_url(initial_url):
    if "/dl/" in initial_url: return initial_url
    scraper = cloudscraper.create_scraper()
    try:
        resp = scraper.get(initial_url, timeout=20)
        match = re.search(r'var reurl = "(.*?)"', resp.text)
        if match:
            redirect_url = match.group(1)
            qs = parse_qs(urlparse(redirect_url).query)
            if 'r' in qs:
                b64 = qs['r'][0] + "=" * ((4 - len(qs['r'][0]) % 4) % 4)
                return base64.b64decode(b64).decode('utf-8')
    except: pass
    return initial_url

@app.route('/')
def home():
    return "MFLIX Bypass API is Active!"

@app.route('/extract', methods=['GET'])
def extract_api():
    url_input = request.args.get('url')
    if not url_input: return jsonify({"error": "URL missing"}), 400

    target_url = get_real_target_url(url_input)
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--single-process') # RAM बचाने के लिए सबसे ज़रूरी
    options.add_argument('--disable-extensions')
    options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 10; K)")

    service = Service("/usr/bin/chromedriver")
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        driver.get(target_url)
        
        time.sleep(8) # बटन लोड होने का इंतज़ार
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        link_tag = soup.find('a', id='vd')
        
        if link_tag and link_tag.get('href'):
            return jsonify({"status": "success", "final_link": link_tag.get('href')})
        return jsonify({"status": "failed", "message": "Link id='vd' not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500
    finally:
        if driver:
            try: driver.quit()
            except: pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
