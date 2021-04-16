from flask import Flask
import ddg3

app = Flask('app')

def search(text):
    """
    Search DuckDuckGo for a given piece of text and return
    the abstract returned by DuckDuckGo as a suggested response
    for display in the Turn.io UI
    """
    result = ddg3.query(text)
    search_results = []
    if result.abstract.text:
        search_results.append(
            {
                "type": "TEXT",
                "body": result.abstract.text,
                "title": "Main Abstract",
                "confidence": 1.0,
            }
        )

    if result.results:
        search_results.extend(
            [
                {
                    "type": "TEXT",
                    "body": "%s - %s" % (r.text, r.url),
                    "title": "Search Result %s" % (index,),
                    "confidence": ((len(result.results) - index) / 10),
                }
                for index, r in enumerate(result.results)
            ]
        )
    return search_results

@app.route('/')
def index():
  return 'The Turn Context API endpoint is at /context'

@app.route('/context', methods=["POST"])
def context():
    from flask import request
    json = request.json
    if json.get("handshake", False):
        return {
            "version": "1.0.0-alpha",
            "capabilities": {
                "actions": False,
                "suggested_responses": True,
            }
        }

    text_messages = [
        m
        for m in json["messages"]
        if m["type"] == "text" and m["_vnd"]["v1"]["direction"] == "inbound"
    ]
    if text_messages:
        text = text_messages[0]["text"]["body"]
        results = search(text)
        print("Searching for %r returned %d results" % (text, len(results)))
    else:
        print("Most recent message was not a text message, skipping search")
        results = []
    return {
        "version": "1.0.0-alpha",
        "suggested_responses": results,
    }


app.run(host='0.0.0.0', port=8080)