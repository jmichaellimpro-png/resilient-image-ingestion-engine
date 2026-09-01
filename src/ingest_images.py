import os
import sys
import logging
import requests
from datetime import datetime
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from PIL import Image, ImageDraw, ImageFont, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

API_URL = os.getenv("HYDRO_VIEW_API_URL", "https://hydro-view.com/api/v1/data/query_images?group_id=DKJ3tsVYAzVk48rw9X4yhz9hUXC6zMofhP71gPn5ni8p")
BLOB_API_URL_TEMPLATE = "https://hydro-view.com/api/v1/data/get_image?blob_id={blob_id}"
BEARER_TOKEN = os.getenv("HYDRO_VIEW_BEARER_TOKEN")
OUTPUT_FOLDER = os.getenv("OUTPUT_IMAGE_FOLDER", "./output_images")

SITE_FILENAME_MAP = {
    "vBmHRDhnfnAxN54wonpWzrKEoP4tVpnB5xb6stjz4G4": "Site_02_30163.jpg",
    "DR4hGfwZQiFMnHQtsXiYvBywPPeJu3WAXQWPRJNjEBzW": "Site_04_30164.jpg",
    "BzMeF21KQstbD4cDXRBnJiZcDTfzxiUBuDqUSpuJwG1i": "Site_06_30165.jpg",
    "6NSJmZK1q3jH8RZLmXb4WvGLRgtDatfhcp6uPbsjnoSz": "Site_08_30166.jpg",
    "GZ1X1NuArJ68eDicCyjZHFkpLk6ERGEKRS2jYVUMvwyL": "Site_10_30167.jpg",
    "CMdYZChbN8t95gfX1wvxkQmh8sQD24B9RXPDW7eSwY13": "Site_12_30168.jpg"
}

def get_resilient_session(retries=250, backoff_factor=0.2):
    """Configures HTTP adapter with multi-retry resilience for field dropouts."""
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def add_timestamp(image_path: str, timestamp_str: str):
    try:
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 40)
            except IOError:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), timestamp_str, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            bar_height = text_height + 20

            draw.rectangle([(0, 0), (img.width, bar_height)], fill="white")
            text_position = ((img.width - text_width) // 2, (bar_height - text_height) // 2)
            draw.text(text_position, timestamp_str, font=font, fill="black")

            img.save(image_path)
            logging.info(f"Timestamp applied: {image_path}")
    except Exception as e:
        logging.error(f"Timestamp error: {e}")

def run():
    if not BEARER_TOKEN:
        logging.error("Missing HYDRO_VIEW_BEARER_TOKEN secret.")
        sys.exit(1)

    session = get_resilient_session()
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    try:
        response = session.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        sites = response.json().get('sites', [])

        for site_info in sites:
            site_id = site_info.get('site_id')
            blob_id = site_info.get('blob_id')

            if site_id in SITE_FILENAME_MAP:
                blob_url = BLOB_API_URL_TEMPLATE.format(blob_id=blob_id)
                img_resp = session.get(blob_url, headers=headers, timeout=30)

                if img_resp.status_code == 200:
                    out_path = os.path.join(OUTPUT_FOLDER, SITE_FILENAME_MAP[site_id])
                    with open(out_path, 'wb') as f:
                        f.write(img_resp.content)

                    add_timestamp(out_path, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        logging.error(f"Ingestion stream failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()
