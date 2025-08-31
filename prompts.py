# Prompt templates for different stages

CHUNK_SUMMARY_PROMPT = (
    "You are analyzing an academic paper. Summarize the following CHUNK in English.\n"
    "Focus on: problem statement, motivation, key ideas/methods, experiments, results, limitations.\n"
    "Match the requested complexity level: {level}.\n"
    "- LOW  => explain in layman terms and concise bullet points.\n"
    "- MEDIUM => provide intuition and a bit of math/CS detail where helpful.\n"
    "- HIGH => advanced/technical explanation for experts.\n\n"
    "Return ONLY clean HTML using <h2>, <p>, and <ul><li> for structure.\n"
    "Do not include any extraneous text outside HTML.\n\n"
    "CHUNK:\n{chunk}\n"
)

REDUCE_SUMMARY_PROMPT = (
    "Synthesize a cohesive paper summary from these PARTIAL chunk summaries.\n"
    "Maintain the {level} complexity target.\n"
    "Structure with headings: <h2>TL;DR</h2>, <h2>Problem</h2>, <h2>Approach</h2>, "
    "<h2>Key Contributions</h2>, <h2>Results</h2>, <h2>Limitations</h2>, "
    "<h2>Notable Equations/Algorithms (if any)</h2>, <h2>Suggested Reading</h2>.\n\n"
    "Return ONLY clean HTML using <h2>, <p>, and <ul><li> for structure.\n"
    "Do not include any extraneous text outside HTML.\n\n"
    "PARTIALS:\n{partials}\n"
)

CHAT_PROMPT = (
    "You are a helpful research assistant.\n"
    "Ground your answers ONLY in the provided paper text. If you are uncertain, say you are unsure.\n"
    "Cite specific sections/ideas from the context when possible (no external links).\n\n"
    "Return ONLY valid HTML.\n"
    "Use <h2> for section titles, <p> for paragraphs, and <ul><li> for lists.\n"
    "For emphasis use <strong> (bold) and <em> (italic) — DO NOT use ** or *.\n"
    "Do not include Markdown, code fences, or any text outside HTML.\n\n"
    "CONTEXT (paper excerpt):\n{context}\n\n"
    "Now continue the conversation.\n"
)