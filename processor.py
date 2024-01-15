import csv
import sys
import os
import asyncio
from elasticsearch import AsyncElasticsearch, helpers
from elasticsearch.exceptions import ConnectionTimeout
from bs4 import BeautifulSoup
import re
import hashlib
import logging
from dateutil import parser as date_parser
import html
import logging
import csv
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
csv.field_size_limit(sys.maxsize)

ES_PASSWORD = os.getenv('ES_PASSWORD')
ES_CLOUD_ID = os.getenv('ES_CLOUD_ID')
CSV_FILE_PATH = 'csv-files/Linea/Linea docs.csv'
INDEX = "search-linea"

max_word_count = 400

def write_errors_to_csv(failed_docs, file_name='failed_indexing.csv'):
    fieldnames = failed_docs[0].keys()  # Assuming all documents have the same fields

    with open(file_name, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(failed_docs)
    logging.info(f"Failed documents written to {file_name}")

async def bulk_index_to_elasticsearch(documents, index):
    try:
        async with await get_elasticsearch_client() as es:
            RETRY_ON_TIMEOUT = 3
            total_successes = 0
            errors = []
            failed_docs = []

            for doc in documents:
                current_doc = doc
                action = {
                    "_op_type": "create",
                    "_index": index,
                    "_id": doc["_id"],  # Using "_id" for Elasticsearch document ID
                    "_source": {key: value for key, value in doc.items() if key != "_id"},  # Include "id" in the source
                    "pipeline": "ml-inference-master"  # Update if you have a different pipeline
                }

                for attempt in range(RETRY_ON_TIMEOUT):
                    try:
                        successes, bulk_errors = await helpers.async_bulk(es, [action], timeout="5m", raise_on_error=False)
                        total_successes += successes
                        if bulk_errors:
                            for error in bulk_errors:
                                error_details = error.get('error', {})
                                error_reason = error_details.get('reason', 'Unknown Error')

                                # Log the error and append it to failed_docs
                                logging.error(f"Error for document: {error_reason}, Full Error: {error_details}")
                                current_doc['error_reason'] = error_reason
                                current_doc['error_details'] = error_details
                                failed_docs.append(current_doc)
                                

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
                        failed_docs.append(doc)
                        break
    except Exception as e:
        logging.error(f"An error occurred in bulk_index_to_elasticsearch: {e}")
        errors.append(str(e))

    finally:
        if failed_docs:
            write_errors_to_csv(failed_docs)

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
        # Return an empty string if the date is empty
        return ""

    try:
        date_obj = date_parser.parse(date_string)
        return date_obj.strftime('%Y-%m-%dT00:00:00.000Z')
    except ValueError as e:
        print(f"Date formatting error: {e}")
        # Optionally, you can return an empty string here as well
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

def split_html_by_headers(htmlContent):
    try:
        # Regular expression to match positions just before header tags like <h1>, <h2>, etc.
        header_pattern = re.compile(r'(?=<h\d.*?>.*?</h\d>)')
        
        # Split the content just before each header
        split_content = header_pattern.split(htmlContent)

        # Process the split content to ensure proper chunk formation
        chunks = []
        current_chunk = ""
        for content in split_content:
            if re.match(r'^<h\d.*?>.*?</h\d>', content.strip()):
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = content
            else:
                current_chunk += content
        if current_chunk:  # Add the last chunk if it's not empty
            chunks.append(current_chunk)

        return chunks
    
    except Exception as e:
        logging.error(f"Error occurred in split_html_by_headers: {e}")
        return []
    
def combine_chunks_to_max_word_count(chunks, max_word_count):
    combined_chunks = []
    current_chunk = ""
    current_count = 0

    for chunk in chunks:
        chunk_word_count = word_count(chunk)

        # Check if adding the next chunk exceeds the max word count
        if current_count + chunk_word_count > max_word_count:
            if current_chunk:  # Add the current chunk if it's not empty
                combined_chunks.append(current_chunk.strip())
            current_chunk = chunk
            current_count = chunk_word_count
        else:
            # Ensure there's a space between chunks if current_chunk is not empty
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

def process_html_content(htmlContent, max_word_count):
    try:
        logging.info("Processing HTML content...")

        content_without_multimedia = remove_multimedia_elements(htmlContent)
        #logging.info(f"After removing links and media: {(content_without_multimedia)}")

        chunks = split_html_by_headers(content_without_multimedia)
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


async def process_csv_and_index_to_elasticsearch(csv_file_path, index):
    structured_documents = []

    required_fields = ['title', 'description', 'image', 'content', 'html_content', 'article_url', 'client', 'content_type']

    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            logging.info("CSV file opened successfully.")

            for row in csv_reader:
                # Check for required fields in each row
                if not all(field in row for field in required_fields):
                    missing_fields = [field for field in required_fields if field not in row]
                    raise ValueError(f"Missing required field(s) in CSV row: {missing_fields}")

                title = row['title']
                htmlContent = row['html_content']

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
                        "fullContent": row['content'],
                        "title": title,
                        "description": row['description'],
                        "image": row['image'],
                        "articleURL": row['article_url'],
                        "client": row['client'],
                        "contentType": row['content_type']
                    }

                    field_name_mapping = {
                        'author': 'author',
                        'publication_date': 'publicationDate',
                        'breadcrumbs': 'breadcrumbs',
                        'tags': 'tags'
                    }

                    optional_fields = ['author', 'publication_date', 'breadcrumbs', 'tags']

                    for field in optional_fields:
                        field_value = row.get(field)
                        if field_value:
                            if field == 'publication_date':
                                field_value = format_date(field_value)
                            es_field_name = field_name_mapping.get(field, field)
                            structured_doc[es_field_name] = field_value


                    structured_documents.append(structured_doc)
                    
            logging.info(f"Total structured documents to index: {len(structured_documents)}")

    except csv.Error as e:
        current_article_url = row.get('article_url', 'Unknown URL')
        print(f"CSV error for article URL {current_article_url}: {e}")

    # Bulk index the documents to Elasticsearch
    total_successes, errors = await bulk_index_to_elasticsearch(structured_documents, index)
    logging.info(f"Total documents indexed successfully: {total_successes}")
    if errors:
        logging.error(f"Errors encountered: {errors}")
    return total_successes, errors

# Run the main async function
async def main():
    await process_csv_and_index_to_elasticsearch(CSV_FILE_PATH, INDEX)

if __name__ == "__main__":
    asyncio.run(main())

