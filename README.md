# 🤖 Autonomous B2B Procurement Agent (Claude 3.5 Sonnet)

An AI-native agent built to automate Request-for-Quotes (RFQs) in complex B2B marketplaces. The system processes unstructured multi-item buyer emails, translates them into precise data structures, and executes parallel API/Database tool calls.

## 🚀 Key Technical Features
- **Parallel Tool Calling:** Intercepts intent from complex, multi-item customer prompts and initiates multiple database checks simultaneously.
- **Deterministic Guardrails:** Implements a strict schema layout for external function executions (`check_inventory`).
- **Business-Logic Layer (Shortage Mitigation):** Automatically calculates supply shortfalls and dynamically changes prompt context to offer alternative routing options.

## 🛠️ Tech Stack
- **Core Engine:** Anthropic Claude API (`claude-3-5-sonnet-latest`)
- **Environment:** Python 3.13 / PyCharm
