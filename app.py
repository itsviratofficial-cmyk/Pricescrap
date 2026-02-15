import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/fetch-any-product', methods=['GET'])
def fetch_any_product():
    url = request.args.get('url')
    if not url: return jsonify({"error": "URL missing"}), 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        # 1. Product Info (Universal)
        name = soup.find("meta", property="og:title")
        name = name["content"] if name else (soup.title.string if soup.title else "Product")
        
        image = soup.find("meta", property="og:image")
        image = image["content"] if image else "https://via.placeholder.com/300"

        # 2. Universal Price Detection
        price = "Check Site"
        # Common price selectors across many Indian e-commerce sites
        price_tags = [
            {"tag": "span", "class": "a-price-whole"}, # Amazon
            {"tag": "div", "class": "Nx9Y0u"},        # Flipkart New
            {"tag": "div", "class": "_30jeq3"},       # Flipkart Old
            {"tag": "span", "class": "pdp-price"},    # Myntra
            {"tag": "div", "class": "price-info"}     # General
        ]

        for p in price_tags:
            found = soup.find(p["tag"], class_=p["class"])
            if found:
                price = found.get_text().strip()
                break

        domain = url.split("//")[-1].split("/")[0].replace("www.", "").split('.')[0].capitalize()

        return jsonify({
            "name": name.strip()[:80],
            "image": image,
            "source": domain,
            "price": price,
            "link": url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
        
