import os
import time
import base64
import re
import cloudscraper
from flask import Flask, request, jsonify
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

# Selenium के ज़रूरी हिस्से
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

def get_real_target_url(initial_url):
    """HubCDN लिंक को डिकोड करने के लिए"""
    if "/dl/" in initial_url:
        return initial_url
    scraper = cloudscraper.create_scraper()
    try:
        resp = scraper.get(initial_url, timeout=30)
        match = re.search(r'var reurl = "(.*?)"', resp.text)
        if match:
            redirect_url = match.group(1)
            parsed = urlparse(redirect_url)
            qs = parse_qs(parsed.query)
            if 'r' in qs:
                b64_str = qs['r'][0]
                b64_str += "=" * ((4 - len(b64_str) % 4) % 4)
                return base64.b64decode(b64_str).decode('utf-8')
    except: pass
    return initial_url

@app.route('/')
def home():
    return "MFLIX Bypass API is Running!"

@app.route('/extract', methods=['GET'])
def extract_api():
    url_input = request.args.get('url')
    if not url_input:
        return jsonify({"error": "No URL provided"}), 400

    target_url = get_real_target_url(url_input)
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # RAM बचाने के लिए स्पेशल फ़्लैग्स
    options.add_argument('--disable-gpu')
    options.add_argument('--single-process')
    options.add_argument('--disable-extensions')
    options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 10; K)")

    service = Service("/usr/bin/chromedriver")
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30) # ब्राउज़र को अटकने से बचाएगा
        driver.get(target_url)
        
        time.sleep(7) # बटन लोड होने का इंतज़ार
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        link_tag = soup.find('a', id='vd')
        
        if link_tag and link_tag.get('href'):
            return jsonify({"status": "success", "final_link": link_tag.get('href')})
        return jsonify({"status": "failed", "message": "Link not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500
    finally:
        if driver: driver.quit()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
