from llama_cpp import Llama

llm = Llama(
    model_path= r"D:\Models\CodeLlama-13B\codellama-13b.Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=8,
)

output = llm("Explain Barney style setup:", max_tokens=100)
print(output["choices"][0]["text"])
