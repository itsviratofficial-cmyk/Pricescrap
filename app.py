import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "PriceScanner API is Active and Running!"

@app.route('/fetch-any-product', methods=['GET'])
def fetch_any_product():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL missing"}), 400

    # Browser ki tarah act karne ke liye Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        # 1. Product Name nikalna (Universal Method)
        name_tag = soup.find("meta", property="og:title")
        name = name_tag["content"] if name_tag else (soup.title.string if soup.title else "Product Name Not Found")
        
        # 2. Product Image nikalna
        image_tag = soup.find("meta", property="og:image")
        image = image_tag["content"] if image_tag else "https://via.placeholder.com/300?text=No+Image"

        # 3. Domain Detect karna
        domain = url.split("//")[-1].split("/")[0].replace("www.", "")
        
        # --- AFFILIATE AUTO-INJECTION LOGIC ---
        # Yahan aap apne affiliate tags update kar sakte hain
        final_link = url
        if "amazon" in domain:
            final_link = url.split('?')[0] + "?tag=apka-amazon-21"
        elif "flipkart" in domain:
            final_link = url.split('?')[0] + "&affid=apka-flip-id"
        elif "myntra" in domain:
            final_link = url + "&aff=myntra-tag"

        return jsonify({
            "name": name.strip()[:150], # Pehle 150 characters
            "image": image,
            "source": domain.split('.')[0].capitalize(),
            "link": final_link
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Render ke liye port configuration
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
