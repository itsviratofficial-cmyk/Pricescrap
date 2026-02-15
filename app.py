import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
# Sabse zaruri line: Taaki aapka frontend backend se connect ho sake
CORS(app, resources={r"/*": {"origins": "*"}})

def get_clean_price(soup, site):
    try:
        if "amazon" in site:
            # Amazon ke multiple price selectors
            p = soup.select_one(".a-price-whole") or soup.select_one("#priceblock_ourprice")
            return "₹" + p.get_text().strip() if p else "Check Site"
        elif "flipkart" in site:
            # Flipkart ke naye selectors
            p = soup.select_one(".Nx9Y0u") or soup.select_one("._30jeq3")
            return p.get_text().strip() if p else "Check Site"
        return "Check Site"
    except:
        return "Check Site"

@app.route('/fetch-any-product', methods=['GET'])
def fetch_any_product():
    url = request.args.get('url')
    if not url: return jsonify({"error": "URL missing"}), 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        # Name and Image (Meta tags are most reliable)
        name = soup.find("meta", property="og:title")
        name = name["content"] if name else (soup.title.string if soup.title else "Product")
        
        image = soup.find("meta", property="og:image")
        image = image["content"] if image else "https://via.placeholder.com/300"

        domain = url.split("//")[-1].split("/")[0].replace("www.", "").lower()
        price = get_clean_price(soup, domain)

        return jsonify({
            "name": name.strip()[:80],
            "image": image,
            "source": domain.split('.')[0].capitalize(),
            "price": price,
            "link": url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
                                
