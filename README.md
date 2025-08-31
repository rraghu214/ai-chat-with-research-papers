# AI Chat with Research Papers

This app ingests a research paper URL (arXiv or any PDF/HTML), summarizes it at **LOW / MEDIUM / HIGH** complexity, and offers a **chat interface** grounded in the paper text.

---

## 1) Local Setup

```bash
# 1. Clone
git clone https://github.com/rraghu214/ai-chat-with-research-papers.git
cd ai-chat-with-research-papers

# 2. Install uv (fast Python package/dependency manager)
pip install uv

# 3. Sync dependencies from pyproject.toml
uv sync

# 4. Set environment variable (replace <GEMINI-KEY> with your key)
export GEMINI_API_KEY=<GEMINI-KEY>

# 5. Run the app
uv run python app.py


Now open http://localhost:5000
```

## 2) How it Works (Architecture)
```
- **Extraction**: 
    - `extractors.py` detects arXiv and converts `/abs/` to `/pdf/`. 
    - If direct PDF, downloads and extracts text via `pdfminer.six`.
     - If HTML, uses BeautifulSoup to collect paragraphs.
- **Summarization (Map-Reduce)**: 
    - `llm.summarize_map_reduce()` splits text into chunk.
    - Summarizes each with **Gemini Flash** using `client.models.generate_content`.
    - Synthesizes a final summary with the requested complexity (LOW/MEDIUM/HIGH).
- **Chat**: 
    - `/chat` endpoint builds a prompt with clipped paper context + the running chat history.
    - Calls the same Gemini API to answer questions grounded in the paper.
- **Caching**: 
    - In-memory caches store extracted text and per-level summaries.
    - For production, replace with Redis.
```
## 3) Connecting to AWS EC2
1. Create EC2 instance (Ubuntu 22, t3.micro — free tier is sufficient).

2. Generate PEM key while creating EC2.
3. On Windows, fix permissions:

```icacls "<ec2-access-key>.pem" /inheritance:r /grant <<username>>:R ```

4. From the directory where .pem file exists:
```ssh -i <ec2-access-key>.pem ubuntu@<EC2-HOST/IP>```
5. Update EC2 Security Group:
   - Go to EC2 → Security Groups → Inbound rules → Edit inbound rules
   - Add:
     - Type: Custom TCP
     - Port: 5000
     - Source: 0.0.0.0/0 (or restrict to your IP for safety)

## 4) Setup & Run on AWS EC2
```
# 1. Install system deps
sudo apt update && sudo apt -y install python3-venv python3-pip git

# 2. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Add uv to PATH
export PATH="$HOME/.local/bin:$PATH"

# 4. Clone repo
git clone https://github.com/rraghu214/ai-chat-with-research-papers.git
cd ai-chat-with-research-papers

# 5. Sync dependencies
uv sync

# 6. Set GEMINI API key
echo 'export GEMINI_API_KEY=<GEMINI-KEY>' >> ~/.bashrc
source ~/.bashrc
echo $GEMINI_API_KEY   # should display your key

# 7. Run
uv run python3 app.py


```
Now access your app at:
👉 http://<EC2-HOST/IP>:5000

## 5) Notes
- If your account exposes a newer model string (e.g., `gemini-2.5-flash`), set `GEMINI_MODEL` accordingly. The code uses `client.models.generate_content` exactly as required.
- For larger PDFs, increase chunk size or switch to a document store + retrieval. For a course assignment, current approach is typically sufficient.
- Replace in-memory caches with Redis and add auth if exposing publicly.