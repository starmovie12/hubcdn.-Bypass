import os
import time
import base64
import re
import cloudscraper
from flask import Flask, request, jsonify
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

# Selenium के ज़रूरी हिस्से (यही मिसिंग थे)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

def get_real_target_url(initial_url):
    """HubCDN के लिंक को डिकोड करने के लिए"""
    print(f"🔄 Checking URL type: {initial_url}")
    
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
                real_url = base64.b64decode(b64_str).decode('utf-8')
                return real_url
    except Exception as e:
        print(f"⚠️ Decode Error: {e}")
    
    return initial_url

@app.route('/')
def home():
    return "MFLIX Bypass API is Running!"

@app.route('/extract', methods=['GET'])
def extract_api():
    # URL पैरामीटर प्राप्त करें
    url_input = request.args.get('url')
    if not url_input:
        return jsonify({"error": "Please provide a 'url' parameter"}), 400

    target_url = get_real_target_url(url_input)
    
    # Selenium Options सेट करें
    options = Options()
    options.add_argument('--headless') # बिना ब्राउज़र खोले चलेगा
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36")

    # Render/Docker के लिए Chromedriver का पाथ
    service = Service("/usr/bin/chromedriver")
    
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(target_url)
        
        # बटन लोड होने का इंतज़ार करें (7 सेकंड)
        print("⏳ Waiting 7 seconds for button...")
        time.sleep(7)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        link_tag = soup.find('a', id='vd')
        
        if link_tag and link_tag.get('href'):
            final_link = link_tag.get('href')
            return jsonify({
                "status": "success",
                "final_link": final_link
            })
        else:
            return jsonify({"status": "failed", "message": "id='vd' not found"}), 404
            
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    # Render के पोर्ट पर रन करें
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
