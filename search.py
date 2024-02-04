from flask import Flask, render_template, request, jsonify, Response, redirect, url_for, session
from werkzeug.routing import BaseConverter
import requests
from openai import OpenAI
import os
import traceback
import json
import logging
import base64
from urllib.parse import quote
from authlib.integrations.flask_client import OAuth
from authlib.jose import jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv("AUTH0_APP_SECRET_KEY")

# Check if running in production
if os.getenv("FLASK_ENV") == "production":
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['REMEMBER_COOKIE_SECURE'] = True
else:
    # For local development, these can be False or not set
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['REMEMBER_COOKIE_SECURE'] = False

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

es_username = os.getenv("ES_USERNAME")
es_password = os.getenv("ES_PASSWORD")
es_basic_auth_header = 'Basic ' + base64.b64encode(f'{es_username}:{es_password}'.encode()).decode()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

bubble_api_key = os.getenv("BUBBLE_API_KEY")

class LowerCaseConverter(BaseConverter):
    def to_python(self, value):
        return value.lower()

    def to_url(self, value):
        return value.lower()
    
app.url_map.converters['lowercase'] = LowerCaseConverter


# @app.route('/')
# def index():
#    return redirect("http://mosaicnetwork.co", code=302)

@app.route("/login")
def login():
    nonce = base64.urlsafe_b64encode(os.urandom(16)).decode('utf-8')
    session['nonce'] = nonce
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True),
        nonce=nonce
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    nonce = session.pop('nonce', None)
    session["user"] = token
    userinfo = oauth.auth0.parse_id_token(token, nonce=nonce)
    session["userinfo"] = userinfo
    return redirect("/finance")

@app.route("/logout")
def logout():
    session.clear()
    return_to_url = quote("https://mosaicnetwork.co", safe='')
    logout_url = f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?client_id={os.getenv('AUTH0_CLIENT_ID')}&returnTo={return_to_url}"
    return redirect(logout_url)

@app.route("/")
def home():
    return redirect("https://mosaicnetwork.co")

@app.route("/finance")
def finance():
    current_path = '/finance'
    if 'user' not in session:
        return redirect(url_for('login', next=request.url))
    return render_template("index.html", current_path=current_path, session=session)



@app.route('/<lowercase:path>')
def catch_all(path):
    if path == 'pymnts':
        return render_template('index.html', path='PYMNTS')
    elif path == 'finance':
        return render_template('index.html', path='Finance')
    elif path == 'bankless':
        return render_template('index.html', path='Bankless')
    elif path == 'polkadot':
        return render_template('index.html', path='Polkadot')
    elif path == 'linea':
        return render_template('index.html', path='Linea')
    elif path == 'celo':
        return render_template('index.html', path='Celo')
    elif path == 'stacks':
        return render_template('index.html', path='Stacks')
    elif path == 'rootstock':
        return render_template('index.html', path='Rootstock')
    else:
        return 'Page not found', 404

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
    origin = data.get('path')

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
        "sources_url": sources_url,
        "origin": origin
    }

    response = requests.post(endpoint, headers=headers, json=body)
    app.logger.info(f"API Response: {response.text}")
    return jsonify(response.json())

# Standard search
@app.route('/<lowercase:path>/search', methods=['GET', 'POST'])
def search(path):
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

    # Define Elasticsearch index and search template based on path
    if path == 'pymnts':
        es_index = 'search-pymnts'
        search_template_id = 'standard_blog_search_template'
    elif path == 'finance':
        es_index = 'search-finance'
        search_template_id = 'standard_blog_search_template'
    elif path == 'bankless':
        es_index = 'search-bankless'
        search_template_id = 'standard_blog_search_template'
    elif path == 'polkadot':
        es_index = 'search-polkadot'
        search_template_id = 'standard_docs_search_template'
    elif path == 'linea':
        es_index = 'search-linea'
        search_template_id = 'standard_docs_search_template'
    elif path == 'celo':
        es_index = 'search-celo'
        search_template_id = 'standard_docs_search_template'
    elif path == 'stacks':
        es_index = 'search-stacks'
        search_template_id = 'standard_docs_search_template'
    elif path == 'rootstock':
        es_index = 'search-rootstock'
        search_template_id = 'standard_docs_search_template'
    else:
        return jsonify({"error": "Invalid path"}), 400
    
    es_headers = {
        "Content-Type": "application/json",
        "Authorization": es_basic_auth_header
    }
    
    es_query = {
        "id": search_template_id,
        "params": {
            "knn_query": query,
            "text_query": query,
            "k": 10,
            "num_candidates": 100,
            "rrf_window_size": 50,
            "rrf_rank_constant": 20
            }
        }

    es_response = requests.get(f'https://my-deployment-7cce90.es.us-east-2.aws.elastic-cloud.com/{es_index}/_search/template',
                               json=es_query, headers=es_headers)
    es_data = es_response.json()

    unique_source_cards = {}
    DEFAULT_IMG = "https://aef8cbb778975f3e4df2041ad0bae1ca.cdn.bubble.io/f1706204093859x790451107332714700/article_img_placeholder.jpg"

    if 'hits' in es_data and 'hits' in es_data['hits']:
        for hit in es_data['hits']['hits']:
            source_data = hit['_source']
            title = source_data.get('title')
            image = source_data.get('image', DEFAULT_IMG)
            articleUrl = source_data.get('articleUrl')

            app.logger.info(f"Title: {title}")

            unique_key = title
            if unique_key not in unique_source_cards:
                source_card = {
                    "image": image if image else DEFAULT_IMG,
                    "articleUrl": articleUrl,
                    "title": title
                }
                unique_source_cards[unique_key] = source_card
    else:
        print("Error: 'hits' key not found or no results in Elasticsearch response.")
        print(es_data)
        return jsonify({"error": "No results found"}), 404
    
    source_cards_data = json.dumps(list(unique_source_cards.values()))
    
    context = extract_context(es_data)
    # context = "This is test context"

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
                    {"role": "system", "content": "You are an AI assistant with expertise in the payments, finance, and crypto industries. When questions come in, give a helpful answer, but keep responses concise and to the point. You'll receive extra content with each question that you can use as context. If the provided context does not answer the question, you can use your existing knowledge, you can say something like, 'I don't have knowledge of that.' Never apologize. Occasionally provide examples or quotes from the provided context. It's ok for you to give advice. Give actionabe reponses while helping the user understand nuances or considerations they should take into effect."},
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

# Most recent article search
@app.route('/<lowercase:path>/recent-articles-search', methods=['GET'])
def recent_articles_search(path):
    num_recent_articles = request.args.get('num_recent_articles', type=int)

    # Define Elasticsearch index based on path
    if path == 'pymnts':
        es_index = 'search-pymnts'
    elif path == 'bankless':
        es_index = 'search-bankless'
    else:
        return jsonify({"error": "Invalid path"}), 400
    
    es_headers = {
        "Content-Type": "application/json",
        "Authorization": es_basic_auth_header
    }
    
    es_query = {
        "id": "recent_articles_search_template",
        "params": {
            "num_recent_articles": num_recent_articles
        }
    }

    es_response = requests.get(f'https://my-deployment-7cce90.es.us-east-2.aws.elastic-cloud.com/{es_index}/_search/template',
                               json=es_query, headers=es_headers)
    es_data = es_response.json()
    for hit in es_data['hits']['hits']:
        title = hit['_source']['title']
        app.logger.info(f"Title: {title}")

    # print("Elasticsearch Response:", es_data)
    # logging.info(f"Elasticsearch Response: {es_data}")

    unique_source_cards = {}
    DEFAULT_IMG = "https://aef8cbb778975f3e4df2041ad0bae1ca.cdn.bubble.io/f1706204093859x790451107332714700/article_img_placeholder.jpg"

    if 'hits' in es_data and 'hits' in es_data['hits']:
        for hit in es_data['hits']['hits']:
            source_data = hit['_source']
            title = source_data.get('title')
            image = source_data.get('image', DEFAULT_IMG)
            articleUrl = source_data.get('articleUrl')

            app.logger.info(f"Title: {title}")

            unique_key = title
            if unique_key not in unique_source_cards:
                source_card = {
                    "image": image if image else DEFAULT_IMG,
                    "articleUrl": articleUrl,
                    "title": title
                }
                unique_source_cards[unique_key] = source_card
    else:
        print("Error: 'hits' key not found or no results in Elasticsearch response.")
        print(es_data)
        return jsonify({"error": "No results found"}), 404
    
    source_cards_data = json.dumps(list(unique_source_cards.values()))

    context = extract_context(es_data)
    # context = "This is test context"

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
                    {"role": "system", "content": "You are an AI assistant with expertise in the payments, finance, and crypto industries. When questions come in, give a helpful answer, but keep responses concise and to the point. You'll receive extra content with each question that you can use as context. Occassionaly give examples or quotes from the context in your answer."},
                    {"role": "user", "content": f"Using the following context, answer this question: 'What is the latest news?'. Here is the extra context: {context}"}
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
        title = hit['_source'].get('title', '')
        client = hit['_source'].get('client', '')
        chunked_content = hit['_source'].get('chunkedContent', '')
        # Adding a separator between hits
        context += f"Here is an excerpt from '{client}' titled '{title}'  Excerpt: {chunked_content}\n\n---\n\n"
    return context

if __name__ == '__main__':
    if os.getenv('FLASK_ENV') == 'development':
        app.run(debug=True)
    else:
        app.run()
