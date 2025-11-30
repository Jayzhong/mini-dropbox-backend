You are my coding assistant for this project.
I have attached @ARCHITECTURE_RULES.md that defines our architecture and layering rules and @PRODUCT_CONTEXT specifying what we are going to create.

1. First, carefully read and summarize the most important constraints in 10–15 bullet points, focusing on:
   - Layering (domain / application / interfaces / infrastructure)
   - Where Pydantic is allowed
   - Entity vs ORM model vs Pydantic schema
   - Async-only and repository abstraction rules
2. Then, propose a minimal WALKING SKELETON for this “Dropbox-like backend” that:
   - Just exposes a simple health check endpoint
   - Passes through all four layers
   - Has empty or minimal implementations where business logic is not ready yet

VERY IMPORTANT:

- Do NOT generate any code yet.
- Only output: (a) summarized rules, (b) a file/folder plan, and (c) a step-by-step plan for what code to generate in the next steps.
