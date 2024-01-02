from flask import Flask, render_template, request, jsonify, Response
import requests
from openai import OpenAI
import os
import traceback
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder='static')

es_endpoint = os.getenv("ES_PYMNTS_SEACH_APP_ENDPOINT")
es_search_app_api = os.getenv("ES_PYMNTS_SEARCH_APP_API")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
bubble_api_key = os.getenv("BUBBLE_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/page-visit', methods=['POST'])
def trigger_page_visit_api():
    flask_env = os.getenv('FLASK_ENV', 'development')
    
    if flask_env == 'production':
        endpoint = "https://mosaicnetwork.co/api/1.1/wf/page_visits"
    else:
        endpoint = "https://mosaicnetwork.co/version-test/api/1.1/wf/page_visits"

    headers = {
        "Authorization": f"Bearer {bubble_api_key}",
        "Content-Type": "application/json" 
    }

    response = requests.post(endpoint, headers=headers)
    app.logger.info(f"API Response: {response.text}")
    return jsonify(response.json())

@app.route('/gpt-stats', methods=['POST'])
def trigger_gpt_stats_api():
    data = request.json
    question = data.get('question')
    sources_title = data.get('sources_title')
    sources_url = data.get('sources_url')

    flask_env = os.getenv('FLASK_ENV', 'development')
    
    if flask_env == 'production':
        endpoint = "https://mosaicnetwork.co/api/1.1/wf/gpt_stats"
    else:
        endpoint = "https://mosaicnetwork.co/version-test/api/1.1/wf/gpt_stats"

    headers = {
        "Authorization": f"Bearer {bubble_api_key}",
        "Content-Type": "application/json" 
    }

    body = {
        "question": question,
        "sources_title": sources_title,
        "sources_url": sources_url
    }

    response = requests.post(endpoint, headers=headers, json=body)
    app.logger.info(f"API Response: {response.text}")
    return jsonify(response.json())

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = ""

    logging.info(f"Received {request.method} request with query: {query}")
    if request.method == 'POST':
        query = request.json.get('query')
        logging.info(f"Received {request.method} request with query: {query}")
        print(f"Received query: {query}")
    else:
        query = request.args.get('query', '')
        logging.info(f"Received GET request with query: {query}")
        print(f"Received query: {query}")
    
    # Elasticsearch request
    es_headers = {
        "Content-Type": "application/json",
        "Authorization": f"apiKey {es_search_app_api}"
    }
    es_body = {
        "params": {
            "knn_query": query,
            "text_query": query
            }
    }
    es_response = requests.post(es_endpoint, json=es_body, headers=es_headers)
    es_data = es_response.json()
    source_ids = [hit['_source']['id'] for hit in es_data['hits']['hits']]

    # print("Elasticsearch Response:", es_data)
    # logging.info(f"Elasticsearch Response: {es_data}")

    unique_source_cards = {}
    for source_id in source_ids:
        # Construct the request to Bubble API
        bubble_url = f"https://mosaicnetwork.co/version-test/api/1.1/obj/scrapedContent?constraints=[{{\"key\":\"_id\",\"constraint_type\":\"equals\",\"value\":\"{source_id}\"}}]"
        
        bubble_response = requests.get(bubble_url)
        logging.info(f"Bubble API Response for ID {source_id}: {bubble_response.json()}")

        if bubble_response.status_code == 200:
            record = bubble_response.json()['response']['results'][0]

            logging.info(f"Data from Bubble for ID {source_id}: {record}")

            image = record.get('image', 'default_image.jpg')
            articleUrl = record.get('articleUrl', '#')
            title = record.get('title')

            unique_key = title
            
            if unique_key not in unique_source_cards:
                source_card = {
                    "image": image,
                    "articleUrl": articleUrl,
                    "title": title
                }
            unique_source_cards[unique_key] = source_card

            # logging.info(f"Constructed source card: {unique_source_cards}")

        else:
            logging.error(f"Failed to fetch data from Bubble for source ID {source_id}: {bubble_response.status_code}")

            # Log all the source cards after processing
            # logging.info(f"All source cards: {unique_source_cards}")
    
    source_cards_data = json.dumps(list(unique_source_cards.values()))

    # context = extract_context(es_data)
    context = "This is test context"

    def format_text_to_html(text):
    # Convert bullet points to HTML list items
       # if text.startswith("-"):
            # text = "<ul>" + "".join(f"<li>{line[2:]}</li>" for line in text.split("\n") if line.startswith("-")) + "</ul>"

        # Convert quotes to blockquotes
        # text = text.replace('"', '<blockquote>').replace('"', '</blockquote>', 1)

        # Replace newline characters with HTML line breaks
        text = text.replace("\n", "<br>")

        return text
    
    # Stream response from OpenAI
    def generate():
        yield f"data: {source_cards_data}\n\n"

        try:
            stream = openai_client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "You are an expert in the payments and finance industries, and love teaching people all about it. When questions come in, give a helpful answer, but keep responses concise and to the point. You'll receive extra content with each question that you can use as context. Your answers should focus on the provided context, but you can also use your own knowledge when necessary to provide the user with a great answer. It's ok for you to give advice. Give actionabe reponses while helping the user understand nuances or considerations they should take into effect."},
                    {"role": "user", "content": f"Using the following context, answer this question: '{query}'. Here is the extra context: {context}"}
                ],
                stream=True
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    formatted_content = format_text_to_html(content)
                    yield f"data: {formatted_content}\n\n"
                if 'done' in chunk:  # Check if 'done' token is present
                    yield "data: [DONE]\n\n"
                    break
                    
        except Exception as e:
            logging.error(f"Streaming error: {traceback.format_exc()}")
            error_info = traceback.format_exc()
            print(f"Error occurred: {e}")
            print(f"Error occurred during streaming: {error_info}")
            yield f"data: Error: {str(e)}\n\n"

    return Response(generate(), content_type='text/event-stream')

def extract_context(es_data):
    context = ''
    for hit in es_data['hits']['hits']:
        article_url = hit['_source'].get('articleURL', '')
        chunked_content = hit['_source'].get('chunkedContent', '')
        # Adding a separator between hits
        context += f"Article URL: {article_url}. Excerpt: {chunked_content}\n\n---\n\n"
    return context

if __name__ == '__main__':
    app.run(debug=True)
