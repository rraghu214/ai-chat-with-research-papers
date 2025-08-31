# Paper Summarizer (Flask + Gemini Flash)

This app ingests a research paper URL (arXiv or any PDF/HTML), summarizes it at **LOW/MEDIUM/HIGH** complexity, and offers a **chat** interface grounded in the paper text.

## 1) Local Setup

```bash
# 1. Clone
git clone https://github.com/rraghu214/flask-paper-summarizer.git
cd flask-paper-summarizer

# 2. Python env
python3 -m venv venv
source venv/bin/activate

# 3. Install deps
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# edit .env and add GEMINI_API_KEY (and set GEMINI_MODEL if needed)

# 5. Run
export $(grep -v '^#' .env | xargs -d '\n')
python app.py
```

Open http://localhost:5000

## 2) How it Works (Architecture)
- **Extraction**: `extractors.py` detects arXiv and converts `/abs/` to `/pdf/`. If direct PDF, downloads and extracts text via `pdfminer.six`. If HTML, uses BeautifulSoup to collect paragraphs.
- **Summarization (Map-Reduce)**: `llm.summarize_map_reduce()` splits text into chunks, summarizes each with **Gemini Flash** using `client.models.generate_content`, then synthesizes a final summary with the requested complexity (LOW/MEDIUM/HIGH).
- **Chat**: `/chat` endpoint builds a prompt with clipped paper context + the running chat history, and calls the same Gemini API to answer questions grounded in the paper.
- **Caching**: In-memory caches store extracted text and per-level summaries. For production, replace with Redis.

## 3) Deploy on AWS EC2 (Ubuntu 22.04)
1. **Launch EC2**: t3.small (or similar). Open ports 22, 80 (and 443 for TLS).
2. **System packages**:
   ```bash
   sudo apt update && sudo apt install -y python3-venv python3-pip nginx
   ```
3. **App directory**:
   ```bash
   sudo mkdir -p /opt/flask-paper-summarizer && sudo chown $USER:$USER /opt/flask-paper-summarizer
   cd /opt/flask-paper-summarizer
   git clone <your_repo_url> .
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Gunicorn as a service**:
   ```bash
   sudo cp deploy/paper-summarizer.service /etc/systemd/system/
   sudo nano /etc/systemd/system/paper-summarizer.service  # set env vars
   sudo systemctl daemon-reload
   sudo systemctl enable --now paper-summarizer
   ```
5. **Nginx reverse proxy**:
   ```bash
   sudo cp deploy/nginx.conf.sample /etc/nginx/sites-available/paper-summarizer
   sudo ln -s /etc/nginx/sites-available/paper-summarizer /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```
6. **(Optional) HTTPS** with certbot:
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d your.domain.com
   ```

## 4) Notes
- If your account exposes a newer model string (e.g., `gemini-2.5-flash`), set `GEMINI_MODEL` accordingly. The code uses `client.models.generate_content` exactly as required.
- For larger PDFs, increase chunk size or switch to a document store + retrieval. For a course assignment, current approach is typically sufficient.
- Replace in-memory caches with Redis and add auth if exposing publicly.