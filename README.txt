# 🧠 Offline Code Assistant

A fully offline, local-first AI coding assistant for Windows, powered by CodeLLaMA in GGUF format via `llama-cpp-python`. Supports memory, semantic retrieval, file editing, and learning from your documents, PDFs, images, and more.

---

## 📂 Folder Structure

```bash
offline_codebot_prototype/
├── main.py
├── run.bat
├── config.json                 # Model path, GPU config, context size
├── requirements.txt
│
├── bot_core/                   # All assistant logic modules
│   ├── interface.py            # CLI loop
│   ├── model_llamacpp.py       # Inference core + memory
│   ├── llama_wrapper.py        # llama-cpp-python wrapper
│   ├── command_dispatcher.py   # /command router
│   ├── constants_config.py     # Constants + help
│   ├── logger_utils.py         # Logging to logs/
│   ├── memory.py               # Conversation memory + FAISS export
│   ├── memory_vector_store.py  # SentenceTransformer vector search
│   ├── learning.py             # Learning from .txt/.pdf/.epub/etc.
│   ├── ocr_tools.py            # Image/PDF OCR handling
│   ├── knowledge_tools.py      # Status + preview of learned files
│   ├── epub_converter.py       # EPUB to text
│   ├── paths.py                # Workspace layout setup
│   ├── io.py                   # File list/read/write utilities
│
├── workspace/                 # Your editable .py projects
├── knowledge/                 # Place .txt/.pdf/.epub/etc. here
├── embeddings/                # Saved FAISS DB + ids.json
├── sessions/                  # Future chat history storage
├── logs/
│   ├── conversation_log.txt   # Full interaction log
│   ├── error_log.txt          # Exceptions + debug errors
│   ├── history_memory.txt     # Persistent conversation state
│   └── exports/               # Memory exports (timestamped)
```

---

## ⚙️ Setup

### 1. Install Python packages
```bash
cd D:/offline_codebot_prototype
pip install -r requirements.txt
```

### 2. Download GGUF Model
- Recommended: `CodeLLaMA 13B Q4_K_M`
- From: https://huggingface.co/TheBloke/CodeLlama-13B-GGUF
- Save to: `D:/Models/CodeLlama-13B/codellama-13b.Q4_K_M.gguf`

### 3. Update config.json
```json
{
  "model_path": "D:/Models/CodeLlama-13B/codellama-13b.Q4_K_M.gguf",
  "gpu_layers": 40,
  "ctx_size": 2048
}
```

---

## 🚀 Launch

Double-click `run.bat` or run:
```bash
python main.py
```

---

## 💬 CLI Usage

You’ll be greeted with:
```
Offline Coding Assistant Bot Ready.
>>>
```
Type natural prompts or use commands:

### 🔧 Commands (from /help)
```
/memory list       List saved memory files
/forget            Clear memory history
/remember on|off   Enable/disable memory
/memory export     Save memory to file
/memory open       Open last exported memory
/offline on|off    Toggle offline mode
/knowledge status  Show loaded documents
/learn all         Learn from all supported files
/learn <file>      Learn from a specific .txt
/build_index       Build search index for learned docs
/ocr extract all   OCR all image/pdf files
/ocr test          Test OCR setup
/config show       Show current config
/help              Show this help
```

---

## 🧠 Learning Materials

Supported formats:
- `.txt`, `.md`, `.html`, `.json`, `.py`
- `.pdf` (native and OCRed)
- `.epub` → auto converted
- `.png`, `.jpg`, `.jpeg` → OCR

Place in `knowledge/` and run:
```bash
/learn all
/build_index
```

Then you can ask:
```
What does the book say about decorators?
```

---

## 🛠 Developer Tips

- Customize logic in `model_llamacpp.py`
- Extend knowledge ingestion via `learning.py`
- Replace GGUF model by updating `config.json`
- Extend CLI or embed into GUI via `interface.py`

---

## ✅ Status

This bot runs:
- Fully offline
- Fast on CPU or GPU (llama.cpp)
- Remembers conversations across sessions
- Learns from your files

Ready for customization or extension.

---

## 📜 License
Private use project. All models and third-party libraries subject to original licenses.

---

Need help? Paste errors or ideas and continue building your assistant.
