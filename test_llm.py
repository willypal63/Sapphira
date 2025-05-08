from bot_core.model_llamacpp import init_llm

# Step 1: Initialize the model
generate = init_llm()

# Step 2: Test with a simple prompt
prompt = "What is the capital of France?"

# Step 3: Run and print response
result = generate(prompt)
print("\n--- BOT RESPONSE ---\n")
print(result)
