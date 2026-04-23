import requests
import json
import os
import sys
from medical_network_extractor import MedicalNetworkExtractor

def fetch_document_text(source):
    """
    Fetches text from a URL or reads from a local file.
    """
    if source.startswith('http'):
        print(f"Downloading document from network: {source}...")
        response = requests.get(source)
        response.raise_for_status()
        return response.text
    else:
        print(f"Reading local document: {source}...")
        if not os.path.exists(source):
            raise FileNotFoundError(f"Source file not found: {source}")
        with open(source, 'r', encoding='utf-8') as f:
            return f.read()

def process_text(text):
    """
    Processes the text using MedicalNetworkExtractor.
    """
    print("Processing document for entities and relationships...")
    extractor = MedicalNetworkExtractor()
    return extractor.extract(text)

def main():
    if len(sys.argv) < 2:
        print("Usage: python document_processor.py <source_path_or_url>")
        return

    document_source = sys.argv[1]

    try:
        # Step 1: Fetch document text
        raw_text = fetch_document_text(document_source)

        # Step 2: Extract data
        extracted_data_json = process_text(raw_text)

        # Step 3: Save results
        output_filename = "extracted_doctor_network.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(extracted_data_json)

        print(f"✅ Processing complete! Results saved to: {output_filename}")
        print("\nExtracted Data:")
        print(extracted_data_json)

    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    main()
