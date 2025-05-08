# config.py

# Path to your AI model file
MODEL_PATH = "D:/Models/CodeLlama-13B/codellama-13b.Q4_K_M.gguf"

# Number of layers to load onto GPU
GPU_LAYERS = 0

# Amount of context the bot remembers
CTX_SIZE = 16384

# Batch size for tokens (higher is faster, uses more memory)
N_BATCH = 512

# Controls randomness in bot's responses (0.0 - predictable, higher - creative)
TEMPERATURE = 0.7

# Controls diversity of generated tokens (close to 1 for best results)
TOP_P = 0.95

# Discourages repetition in responses (higher is less repetition)
REPEAT_PENALTY = 1.1

# Number of CPU threads used by the model
N_THREADS = 8

# Number of tokens predicted per interaction
N_PREDICT = 256

# Maximum token size for user prompts
MAX_PROMPT_TOKENS = 1800

# How many chunks of memory or documents to retrieve
MAX_RETRIEVED_CHUNKS = 5

# Max number of characters per chunk
MAX_CHUNK_CHARS = 800
