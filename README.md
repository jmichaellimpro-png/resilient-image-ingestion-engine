# resilient-image-ingestion-engine
Network resilience under poor field connectivity, automated multi-retry handling (up to 250 retries), and stream failure recovery

# Resilient Image Ingestion Engine

An automated, fault-tolerant image ingestion pipeline designed to reliably harvest, process, and timestamp remote camera feed data under poor or unstable field connectivity. Built to run headlessly via GitHub Actions.

## Key Features

* **Network Resilience:** Uses standard HTTP retry adapters configured for up to 250 backoff retries to recover from stream failure and field connectivity dropouts.
* **Automated Processing & Timestamping:** Parses binary image blobs, validates headers, and applies clean top-banner visual timestamps natively using Pillow (`PIL`).
* **CI/CD Integration:** Operates on an automated 15-minute cron schedule via GitHub Actions, eliminating the need for persistent local servers.
* **Zero Hardcoded Secrets:** Designed around environment variables and GitHub Repository Secrets for secure deployment.

---

## Architecture & Directory Structure

```text
resilient-image-ingestion-engine/
├── .github/
│   └── workflows/
│       └── image_ingestion.yml   # 15-minute cron automation
├── src/
│   ├── __init__.py
│   └── ingest_images.py          # Core ingestion & retry logic
├── .gitignore
├── README.md
└── requirements.txt

```

---

## Setup & Configuration

### 1. Environment Variables & Secrets

The engine requires an API authorization token to query the Hydro-View API.

For local development, set the environment variable:

```bash
export HYDRO_VIEW_BEARER_TOKEN="your_bearer_token_here"

```

For production (GitHub Actions), add the key to your repository:

1. Go to **Settings > Secrets and variables > Actions**.
2. Click **New repository secret**.
3. Name: `HYDRO_VIEW_BEARER_TOKEN`
4. Value: `<your-api-bearer-token>`

---

## Local Development

### Prerequisites

* Python 3.10+

### Installation

1. Clone the repository:
```bash
git clone [https://github.com/your-username/resilient-image-ingestion-engine.git](https://github.com/your-username/resilient-image-ingestion-engine.git)
cd resilient-image-ingestion-engine

```


2. Install dependencies:
```bash
pip install -r requirements.txt

```


3. Run the ingestion engine:
```bash
python src/ingest_images.py

```


Processed images will be saved to the `./output_images/` directory.

---

## GitHub Actions Workflow

The engine executes every 15 minutes using `.github/workflows/image_ingestion.yml`.

* **Manual Execution:** Navigate to **Actions > Ingest Hydro-View Images** and click **Run workflow**.
* **Artifact Output:** After each run, the ingested images are saved and available for download under the workflow run's **Artifacts** section as `camera-feeds`.

---

## License

MIT License. Free for industrial and personal modification.

```

```
