import os
import asyncio
from elasticsearch import AsyncElasticsearch, helpers
from elasticsearch.exceptions import ConnectionTimeout
from bs4 import BeautifulSoup
import nltk
import re
import hashlib
import logging
from dateutil import parser as date_parser
import dateutil.parser
from datetime import datetime, timezone
import dateutil.parser
import html
import logging
import httpx
import csv
from dotenv import load_dotenv

load_dotenv()
nltk.download('punkt')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


ES_PASSWORD = os.getenv('ES_PASSWORD')
ES_CLOUD_ID = os.getenv('ES_CLOUD_ID')
API_AUTH_URL = "https://contentapi.cision.com/api/v1.0/auth/login"
API_RELEASES_URL = "https://contentapi.cision.com/api/v1.0/releases"
USERNAME = os.getenv('CISION_USERNAME')
PASSWORD = os.getenv('CISION_PASSWORD')
INDEX = "search-finance"

DEFAULT_IMG = "https://aef8cbb778975f3e4df2041ad0bae1ca.cdn.bubble.io/f1706204093859x790451107332714700/article_img_placeholder.jpg"

max_word_count = 400

auth_token = None
token_expiration = None

async def is_token_expired():
    global token_expiration
    if token_expiration is None:
        return True
    return datetime.now(timezone.utc) >= token_expiration

async def get_auth_token():
    global auth_token, token_expiration
    if await is_token_expired():
        auth_token, token_expiration = await authenticate_to_api()
    return auth_token

async def authenticate_to_api():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                API_AUTH_URL,
                headers={"X-Client": USERNAME, "Content-Type": "application/json"},
                json={"login": USERNAME, "pwd": PASSWORD}
            )
            response.raise_for_status()
            data = response.json()
            auth_token = data["auth_token"]
            expires = dateutil.parser.isoparse(data["expires"])
            return auth_token, expires
        except httpx.HTTPError as e:
            logging.error(f"HTTP error occurred during authentication: {e}")
        except Exception as e:
            logging.error(f"An error occurred during authentication: {e}")
        return None, None
    
async def fetch_article_list(auth_token):
    auth_token = await get_auth_token()
    if not auth_token:
        logging.error("Failed to obtain authentication token")
        return []
    
    initial_params = {
        "show_del": "false",
        "startdate": "20240101T010000-0000",
        "language": "en",
        "industry": "FIN|FNT",
        "keyword_not": "thinking about",
        "keyword_fields": "title",
        "fields": "title|industry|release_id|subject|summary|dateline|multimedia",
        "size": 100,
        "from": 0
        }
    
    articles = []
    next_url = API_RELEASES_URL

    async with httpx.AsyncClient() as client:
        while next_url:
            try:
                response = await client.get(
                    next_url,
                    headers={
                        "X-Client": USERNAME,
                        "Authorization": f"Bearer {auth_token}",
                        "Content-Type": "application/json"
                    },
                    params=initial_params if next_url == API_RELEASES_URL else None
                )
                response.raise_for_status()
                data = response.json()
                articles.extend(data["data"])

                # Update the next_url for the next iteration
                pagination = data.get("pagination", {})
                next_url = pagination.get("next")

                # Reset initial parameters after the first request
                if initial_params:
                    initial_params = None

            except httpx.HTTPError as e:
                logging.error(f"HTTP error occurred while fetching article list: {e}")
                break
            except Exception as e:
                logging.error(f"An error occurred while fetching article list: {e}")
                break

    return articles
    
async def fetch_full_article(auth_token, release_id):
    auth_token = await get_auth_token()
    if not auth_token:
        logging.error("Failed to obtain authentication token")
        return None
    
    article_url = f"{API_RELEASES_URL}/{release_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                article_url,
                headers={
                    "X-Client": USERNAME,
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logging.error(f"HTTP error occurred while fetching article {release_id}: {e}")
        except Exception as e:
            logging.error(f"An error occurred while fetching article {release_id}: {e}")
        return None

def write_errors_to_csv(failed_indexing, file_name='failed_prn_indexing.csv'):
    fieldnames = ['url', 'title', 'error_details', 'error_reason']

    with open(file_name, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(failed_indexing)

async def bulk_index_to_elasticsearch(documents, index, failed_indexing):
    try:
        async with await get_elasticsearch_client() as es:
            RETRY_ON_TIMEOUT = 3
            failed_indexing = []
            total_successes = 0
            errors = []

            for doc in documents:
                action = {
                    "_op_type": "create",
                    "_index": index,
                    "_id": doc["_id"],
                    "_source": {key: value for key, value in doc.items() if key != "_id"},
                    "pipeline": "ml-inference-master" 
                }

                for attempt in range(RETRY_ON_TIMEOUT):
                    try:
                        successes, bulk_errors = await helpers.async_bulk(es, [action], timeout="5m", raise_on_error=False)
                        total_successes += successes
                        if bulk_errors:
                            for error in bulk_errors:
                                error_details = error.get('error', {})
                                error_reason = error_details.get('reason', 'Unknown Error')
                                failed_indexing.append({
                                    "url": doc.get("articleUrl", "No URL"),
                                    "title": doc.get("title", "No Title"),
                                    "error_details": str(error_details),
                                    "error_reason": str(error_reason)
                                })

                                # Log the error and append it to failed_docs
                                logging.error(f"Error for document: {error_reason}, Full Error: {error_details}")
                                

                        break  # Break the retry loop if successful or if an error other than timeout occurred
                    except ConnectionTimeout as e:
                        if attempt < RETRY_ON_TIMEOUT - 1:
                            logging.info(f"Timeout for document {doc['articleUrl']}. Retrying {attempt + 1}/{RETRY_ON_TIMEOUT}...")
                            continue
                        else:
                            errors.append(f"Connection timed out for document {doc['articleUrl']} after {RETRY_ON_TIMEOUT} attempts")
                            break
                    except Exception as e:
                        errors.append(f"Exception for document {doc['articleUrl']}: {str(e)}")
                        doc['error_reason'] = str(e)
                        break
    except Exception as e:
        logging.error(f"An error occurred in bulk_index_to_elasticsearch: {e}")
        errors.append(str(e))

    if failed_indexing:
        write_errors_to_csv(failed_indexing)
        logging.info("Failed document details written to CSV file")

    return total_successes, errors


async def get_elasticsearch_client():
    ES_CLOUD_ID = os.getenv('ES_CLOUD_ID')
    ES_PASSWORD = os.getenv('ES_PASSWORD')
    if not ES_CLOUD_ID or not ES_PASSWORD:
        raise ValueError("Elasticsearch cloud ID and password must be set as environment variables")

    return AsyncElasticsearch(
        cloud_id=ES_CLOUD_ID,
        basic_auth=("elastic", ES_PASSWORD)
    )

def format_date(date_string):
    if not date_string:
        return ""

    try:
        date_obj = date_parser.parse(date_string)
        return date_obj.strftime('%Y-%m-%dT%H:%M:%S%z')
    except ValueError as e:
        print(f"Date formatting error: {e}")
        return ""

def word_count(htmlContent):
    try:
        soup = BeautifulSoup(htmlContent, 'html.parser')
        text = soup.get_text()
        return len(re.findall(r'\w+', text))
    except Exception as e:
        logging.error(f"Error occurred in word_count: {e}")
        return 0

def remove_multimedia_elements(htmlContent):
    try:
        logging.info("Removing multimedia elements and hyperlinks...")
        
        # Check if htmlContent is empty
        if not htmlContent:
            logging.warning("htmlContent is empty or None")
            return ""
            
        soup = BeautifulSoup(htmlContent, 'html.parser')

        # Remove multimedia elements
        for multimedia in soup.find_all(['img', 'video', 'audio']):
            multimedia.replace_with(' ')

        # Remove hyperlinks and replace with their text
        for hyperlink in soup.find_all('a'):
            hyperlink.replace_with(hyperlink.get_text())

        return str(soup)
    
    except Exception as e:
        logging.error(f"Error occurred in remove_multimedia_elements: {e}")
        return ""

def split_html_by_paragraphs(htmlContent):
    try:
        paragraph_pattern = re.compile(r'(?=<p.*?>.*?</p>)')
        
        split_content = paragraph_pattern.split(htmlContent)

        chunks = []
        current_chunk = ""
        for content in split_content:
            if re.match(r'^<p.*?>.*?</p>', content.strip()):
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = content
            else:
                current_chunk += content
        if current_chunk:  # Add the last chunk if it's not empty
            chunks.append(current_chunk)

        return chunks
    
    except Exception as e:
        logging.error(f"Error occurred in split_html_by_paragraphs: {e}")
        return []
    
def combine_chunks_to_max_word_count(chunks, max_word_count):
    combined_chunks = []
    current_chunk = ""
    current_count = 0

    for chunk in chunks:
        chunk_word_count = word_count(chunk)

        # Check if adding the next chunk exceeds the max word count
        if current_count + chunk_word_count > max_word_count:
            if current_chunk: 
                combined_chunks.append(current_chunk.strip())
            current_chunk = chunk
            current_count = chunk_word_count
        else:
            current_chunk += (" " if current_chunk else "") + chunk
            current_count += chunk_word_count

    # Add the last chunk if it's not empty
    if current_chunk.strip():
        combined_chunks.append(current_chunk.strip())

    return combined_chunks


def html_to_text(htmlContent):
    try:
        logging.info("Converting HTML to text...")
        soup = BeautifulSoup(htmlContent, 'html.parser')
        text = soup.get_text(separator=' ', strip=True).replace('\n', ' ').replace('\r', ' ')

        # Decode HTML entities
        text = html.unescape(text)

        # Replace Unicode zero-width spaces
        text = text.replace('\u200b', '')  # For actual Unicode character
        text = text.replace('\\u200b', '')  # For literal string "\u200b"

        return text
    except Exception as e:
        logging.error(f"Error occurred in html_to_text: {e}")
        return ""
    
def extract_first_sentence(text):
    sentences = nltk.sent_tokenize(text)
    return sentences[0] if sentences else ''

def extract_url_from_body(body_html):
    soup = BeautifulSoup(body_html, 'html.parser')
    prnurl_tag = soup.find('a', id="PRNURL")
    if prnurl_tag and prnurl_tag.has_attr('href'):
        return prnurl_tag['href']
    return None

def process_html_content(htmlContent, max_word_count):
    try:
        logging.info("Processing HTML content...")

        content_without_multimedia = remove_multimedia_elements(htmlContent)
        #logging.info(f"After removing links and media: {(content_without_multimedia)}")

        chunks = split_html_by_paragraphs(content_without_multimedia)
        logging.info(f"Chunks count: {len(chunks)}")
        #logging.info(f"Chunks: {(chunks)}")

        combined_chunks = combine_chunks_to_max_word_count(chunks, max_word_count)
        logging.info(f"Chunks count after combining: {len(combined_chunks)}")
        #logging.info(f"Chunks after combining: {(combined_chunks)}")

        text_chunks = [html_to_text(chunk) for chunk in combined_chunks]
        logging.info(f"Final chunks count: {len(text_chunks)}")
        #logging.info(f"Final chunks: {(text_chunks)}")

        return text_chunks
    
    except Exception as e:
        logging.error(f"Error occurred in process_html_content: {e}")
        return []

# Create hash for unique id for each document
def create_hashed_id(*args):
    hash_input = ''.join(str(arg) for arg in args)
    return hashlib.sha256(hash_input.encode()).hexdigest()


async def process_api_data_and_index_to_elasticsearch(INDEX):
    auth_token = await authenticate_to_api()
    if auth_token is None:
        logging.error("Failed to authenticate to API")
        return 0, ["Failed to authenticate to API"]

    article_list = await fetch_article_list(auth_token)
    if not article_list:
        logging.error("No articles fetched")
        return 0, ["No articles fetched"]

    structured_documents = []
    failed_indexing = []
    
    try:
        for article in article_list:
            release_id = article["release_id"]

            summary_html = article["summary"]
            summary_text = html_to_text(summary_html)
            description = extract_first_sentence(summary_text)

            full_article = await fetch_full_article(auth_token, release_id)
            if full_article is None:
                logging.error(f"Failed to fetch full article for release ID {release_id}")
                continue

            htmlContent = full_article["data"]["body"]
            article_url = extract_url_from_body(htmlContent)

            unformated_date = full_article["data"]["date"]
            publication_date = format_date(unformated_date)

            author = full_article["data"].get("source_company", "")
            client = full_article["data"].get("source_company", "")
            title = full_article["data"]["title"]
            image = full_article["data"].get("multimedia", [])[0].get("url", DEFAULT_IMG) if full_article["data"].get("multimedia") else DEFAULT_IMG

            # Chunk and convert HTML content to text
            processed_chunks = process_html_content(htmlContent, max_word_count)
            logging.info(f"Processed {len(processed_chunks)} chunks for title: {title}")

            for chunk in processed_chunks:
                unique_id = create_hashed_id(chunk, title)
                chunked_content = chunk.strip()

                # Create the document only with required fields
                structured_doc = {
                    "_id": unique_id,
                    "chunkedContent": chunked_content,
                    "fullContent": remove_multimedia_elements(htmlContent),
                    "title": title,
                    "author": author,
                    "publicationDate": publication_date,
                    "description": description,
                    "image": image,
                    "articleUrl": article_url,
                    "client": client,
                    "contentType": "blog"
                }

                structured_documents.append(structured_doc)
                    
            logging.info(f"Total structured documents to index: {len(structured_documents)}")

    except Exception as e:
        logging.error(f"An exception occurred during processing: {e}")
        return 0, [f"An exception occurred: {e}"]

    # Bulk index the documents to Elasticsearch
    total_successes, errors = await bulk_index_to_elasticsearch(structured_documents, INDEX, failed_indexing)
    logging.info(f"Total documents indexed successfully: {total_successes}")
    if errors:
        logging.error(f"Errors encountered: {errors}")
    return total_successes, errors

def download_nltk_resources(resource_ids):
    for res in resource_ids:
        try:
            nltk.data.find(f'tokenizers/punkt/{res}.pickle')
        except LookupError:
            logging.info(f"Downloading NLTK resource: '{res}'")
            nltk.download(res)

# Run the main async function
async def main():
    download_nltk_resources(['punkt'])
    await process_api_data_and_index_to_elasticsearch(INDEX)

if __name__ == "__main__":
    asyncio.run(main())

