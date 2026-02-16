import os
from flask import Flask, request, jsonify
# ... बाकी सारे imports (cloudscraper, selenium, etc.) ...

app = Flask(__name__)

def get_real_target_url(initial_url):
    # आपका पुराना फंक्शन यहाँ रहेगा
    pass

@app.route('/extract', methods=['GET'])
def extract_api():
    url_input = request.args.get('url')
    if not url_input:
        return jsonify({"error": "URL parameter is missing"}), 400

    target_url = get_real_target_url(url_input)
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Render के लिए Chromedriver path को dynamic रखें
    service = Service("/usr/bin/chromedriver") 
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(target_url)
        time.sleep(7)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        link_tag = soup.find('a', id='vd')
        
        if link_tag and link_tag.get('href'):
            return jsonify({"final_link": link_tag.get('href')})
        else:
            return jsonify({"error": "Link not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
