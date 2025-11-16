import requests

NEWS_API_KEY = "c18b947004944f7d80ac7c96cb79f564"

def fetch_cybersecurity_news():
    url = (
        "https://newsapi.org/v2/everything?"
        "q=cyber attack OR data breach OR ransomware OR cybersecurity&"
        "language=en&"
        "sortBy=publishedAt&"
        "pageSize=10"
    )

    headers = {"Authorization": NEWS_API_KEY}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data.get("articles", [])
    except Exception as e:
        print("News fetch error:", e)
        return []
