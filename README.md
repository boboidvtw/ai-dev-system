# 🤖 AI Dev System — 5-Step AI Software Engineer

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-23%20passed-brightgreen.svg)](#-run-tests)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> An AI-powered software engineering system that follows a **structured 5-step pipeline** to deliver production-grade code — not just generating snippets, but **thinking like a senior engineer**.

[📖 繁體中文文件](README-ZH.md)

---

## 🎯 Project Vision

Most AI code generators just dump code. This system is different — it implements the **complete engineering process** that a senior developer follows:

1. **Understand the problem** before writing a single line
2. **Design the solution** with architecture and complexity analysis
3. **Implement** with production-quality standards
4. **Test** with comprehensive edge-case coverage
5. **Review** its own code for quality and optimization

The result? Code that's **clean, maintainable, testable, and actually works**.

---

## 🏗 Architecture

### 5-Step Engineering Pipeline

```
┌─────────────────────────────────────────────────────┐
│                   User Request                       │
│              "Fix the login validation"              │
└─────────────────┬───────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────┐
│  Step 1: Problem Understanding                       │
│  → Requirements, assumptions, edge cases             │
│  → Confidence score (< 70% triggers questions)       │
└─────────────────┬───────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────┐
│  Step 2: Solution Design                             │
│  → Architecture, data structures, algorithms         │
│  → Time & space complexity analysis                  │
└─────────────────┬───────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────┐
│  Step 3: Implementation                              │
│  → Production-quality code (multi-file support)      │
│  → PEP8, typing, error handling enforced             │
└─────────────────┬───────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────┐
│  Step 4: Test Cases                                  │
│  → Auto-generated pytest tests                       │
│  → Covers all edge cases from Step 1                 │
└─────────────────┬───────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────┐
│  Step 5: Optimization Review                         │
│  → Quality score (1-10), issue detection             │
│  → Ship / Needs Fixes / Major Rework verdict         │
└─────────────────┬───────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────┐
│  Post-Pipeline                                       │
│  → Run tests → Auto-fix loop (up to 3 retries)      │
│  → Git branch → Commit → Push → Create PR            │
└─────────────────────────────────────────────────────┘
```

### Behavioral Standards

The AI agent enforces these standards at every step:

| Standard | Enforcement |
|----------|-------------|
| **Requirements First** | Step 1 identifies gaps; confidence < 70% triggers clarifying questions |
| **Clean Code** | Step 3 prompts enforce PEP8, clear naming, minimal comments |
| **Error Handling** | Every edge case from Step 1 must be handled in Step 3 |
| **Testable Code** | Step 4 auto-generates tests covering all identified edge cases |
| **Self-Review** | Step 5 scores quality and gives a ship/no-ship verdict |
| **No Unverified Code** | Auto-fix loop retries failed tests up to 3 times |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- An LLM API key (OpenAI, Anthropic, etc.) **OR** a local model via [Ollama](https://ollama.com)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-dev-system.git
cd ai-dev-system

# Install dependencies
pip3 install litellm python-dotenv PyGithub rich pytest

# Configure environment
cp .env.example .env
# Edit .env — set your LLM_MODEL and API keys
```

### Usage

```bash
# 🔍 Dry run — preview generated code without writing files
python3 main.py "Implement email validation" src/validator.py --dry-run

# 🛠 Local development — run pipeline, skip PR creation
python3 main.py "Fix SQL injection vulnerability" src/db.py --skip-pr

# 🚀 Full pipeline — code + tests + auto-fix + PR
python3 main.py "Add rate limiting middleware" src/middleware.py

# 💬 Interactive mode — pause when AI has low confidence
python3 main.py "Refactor payment module" src/payment.py --interactive

# 📝 Save engineering report
python3 main.py "Optimize caching strategy" src/cache.py --report report.md

# ⚡ Quick mode — skip Step 5 review
python3 main.py "Add input validation" src/forms.py --skip-review --skip-pr
```

### CLI Reference

| Flag | Description |
|------|-------------|
| `--dry-run` | Preview generated code without writing files |
| `--skip-pr` | Skip GitHub PR creation |
| `--skip-review` | Skip Step 5 optimization review |
| `--interactive` | Pause when confidence is low for user input |
| `--report FILE` | Save structured engineering report to file |
| `--test-path PATH` | Custom test directory (default: `tests/`) |
| `--log-level LEVEL` | Set log level: `DEBUG`, `INFO`, `WARNING` |

---

## 📁 Project Structure

```
ai-dev-system/
├── main.py                      # Orchestrator — 5-step pipeline + CLI
├── config.py                    # Typed configuration from .env
│
├── agents/
│   ├── dev_agent.py             # 5-Step AI Engineer (core brain)
│   ├── prompts.py               # Step-specific prompt templates
│   └── pipeline_models.py       # Typed dataclass models for all steps
│
├── tools/
│   ├── github_tool.py           # Git CLI + PyGithub API operations
│   ├── test_runner.py           # pytest runner with structured results
│   └── file_manager.py          # File I/O with backup support
│
├── tests/                       # 23 unit tests (all mocked, no API needed)
│   ├── test_dev_agent.py        # 14 tests — pipeline + each step
│   ├── test_file_manager.py     # 5 tests — file operations
│   └── test_runner_test.py      # 4 tests — test runner edge cases
│
├── pyproject.toml               # Python project metadata
├── .env.example                 # Environment variable template
├── .gitignore
├── LICENSE
├── README.md                    # This file (English)
└── README-ZH.md                 # 繁體中文文件
```

---

## 🔧 Supported Models

This system uses [litellm](https://docs.litellm.ai/docs/providers) for model-agnostic LLM integration. Any supported provider works:

| Provider | Example Model String | Notes |
|----------|---------------------|-------|
| **OpenAI** | `gpt-4o`, `gpt-4o-mini` | Best quality, requires API key |
| **Ollama** | `ollama/llama3`, `ollama/codellama` | Local, private, free |
| **Anthropic** | `claude-3-haiku-20240307` | Fast, structured output |
| **Groq** | `groq/llama3-70b-8192` | Ultra-fast inference |
| **DeepSeek** | `deepseek/deepseek-coder` | Code-specialized |

### Local Model Example (No API Key)

```bash
# Install Ollama and pull a model
ollama pull llama3

# Set in .env
LLM_MODEL=ollama/llama3

# Run
python3 main.py "Build a REST API endpoint" src/api.py --skip-pr
```

---

## 🧪 Run Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ -v --cov

# Run specific test class
python3 -m pytest tests/test_dev_agent.py::TestFullPipeline -v
```

All 23 tests are fully mocked — **no LLM API calls needed** to run the test suite.

---

## 📊 Pipeline Output Example

When you run the system, you'll see structured output for each step:

```
╭──────── Pipeline Start ────────╮
│ 🤖 AI Software Engineer        │
│                                 │
│ Task:  Fix login validation     │
│ File:  src/auth.py              │
│ Model: gpt-4o-mini              │
╰─────────────────────────────────╯

━━━ Running 5-Step Engineering Pipeline ━━━

┌──── Step 1: Problem Understanding ────┐
│ Summary:     Fix login validation     │
│ Confidence:  🟢 92%                   │
│ Edge Cases:  • empty email            │
│              • SQL injection          │
│              • unicode characters     │
└───────────────────────────────────────┘

┌──── Step 2: Solution Design ──────────┐
│ Approach:     Add input validation    │
│ Time:         O(n)                    │
│ Space:        O(1)                    │
└───────────────────────────────────────┘

📄 auth.py (342 chars)         ← Step 3
🧪 tests/test_auth.py (289 chars) ← Step 4

┌──── Step 5: Optimization Review ──────┐
│ Quality Score:  8/10                  │
│ Verdict:        ✅ SHIP               │
└───────────────────────────────────────┘

🧪 Running tests... ✅ All tests passed!
📤 Creating PR...
🎉 PR created: https://github.com/.../pull/1
```

---

## 🔮 Roadmap

- [ ] **RAG Integration** — Index entire repo for full codebase context
- [ ] **QA Agent** — Independent test review agent
- [ ] **PM Agent** — Parse GitHub Issues into engineering tasks
- [ ] **Multi-Agent Orchestration** — PM → Dev → QA collaboration
- [ ] **GitHub Actions** — Trigger pipeline from PR comments
- [ ] **Web Dashboard** — Visual pipeline monitoring

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`python3 -m pytest tests/ -v`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [litellm](https://github.com/BerriAI/litellm) — Universal LLM API interface
- [Rich](https://github.com/Textualize/rich) — Beautiful terminal output
- [PyGithub](https://github.com/PyGithub/PyGithub) — GitHub API client

---

<p align="center">
  Built with 🤖 by AI, reviewed by humans.
</p>
