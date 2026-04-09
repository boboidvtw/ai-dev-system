# 🤖 AI Dev System — 5 步驟 AI 軟體工程師

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-23%20passed-brightgreen.svg)](#-執行測試)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 一個遵循**結構化 5 步驟工程流程**的 AI 軟體工程系統，交付 production-grade 品質的程式碼 — 不只是產生片段，而是**像資深工程師一樣思考**。

[📖 English Documentation](README.md)

---

## 🎯 專案願景

大多數 AI 程式碼生成器只會直接丟出 code。這個系統不一樣 — 它實作了資深開發者遵循的**完整工程流程**：

1. 寫程式碼之前，**先理解問題**
2. **設計解法**，包含架構和複雜度分析
3. **全域代碼理解 (RAG)**：索引整個 Repo，從全局視角理解 codebase
4. 使用 production-quality 標準**實作**
5. **多 Agent 協作**：PM、Dev、QA 專業代理人協同作業
6. **自動化 GitHub 整合**：從讀取 Issue 到自動提交 PR 與 CI/CD
7. **自我審查**程式碼品質與優化空間

最終結果？程式碼是**乾淨的、可維護的、可測試的，而且真的能跑**。

---

## 🏗 系統架構

### 5 步驟工程流水線

```
┌─────────────────────────────────────────────────────┐
│                   使用者需求                          │
│              「修復登入驗證功能」                       │
└─────────────────┬───────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────┐
│  Step 1：需求理解（Problem Understanding）             │
│  → 需求、假設、邊界條件                                │
│  → 信心分數（< 70% 會觸發提問）                        │
└─────────────────┬───────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────┐
│  Step 2：解法設計（Solution Design）                   │
│  → 架構、資料結構、演算法                               │
│  → 時間與空間複雜度分析                                 │
└─────────────────┬───────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────┐
│  Step 3：程式碼實作（Implementation）                  │
│  → Production-quality 程式碼（支援多檔案）              │
│  → 強制 PEP8、typing、錯誤處理                         │
└─────────────────┬───────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────┐
│  Step 4：測試案例（Test Cases）                        │
│  → 自動產生 pytest 測試                                │
│  → 覆蓋 Step 1 識別的所有邊界條件                       │
└─────────────────┬───────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────┐
│  Step 5：優化建議（Optimization Review）               │
│  → 品質評分（1-10）、問題偵測                           │
│  → 最終裁定：可交付 / 需修改 / 需大改                    │
└─────────────────┬───────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────┐
│  後處理                                               │
│  → 執行測試 → 自動修復迴圈（最多 3 次重試）              │
│  → Git 建立分支 → Commit → Push → 建立 PR              │
└─────────────────────────────────────────────────────┘
```

### 行為準則

AI Agent 在每個步驟都遵循以下準則：

| 準則 | 執行方式 |
|------|---------|
| **需求理解優先** | Step 1 識別缺口；信心 < 70% 觸發釐清問題 |
| **乾淨程式碼** | Step 3 的 prompt 強制 PEP8、清楚命名、適度註解 |
| **錯誤處理** | Step 1 的每個邊界條件都必須在 Step 3 處理 |
| **可測試程式碼** | Step 4 自動產生涵蓋所有邊界條件的測試 |
| **自我審查** | Step 5 評分品質並給出可交付/不可交付的裁定 |
| **禁止未驗證程式碼** | 自動修復迴圈對失敗的測試最多重試 3 次 |

---

## 🚀 快速開始

### 環境需求

- Python 3.9 以上
- LLM API 金鑰（OpenAI、Anthropic 等）**或**透過 [Ollama](https://ollama.com) 使用本地模型

### 安裝

```bash
# 複製專案
git clone https://github.com/YOUR_USERNAME/ai-dev-system.git
cd ai-dev-system

# 安裝依賴
pip3 install litellm python-dotenv PyGithub rich pytest

# 設定環境變數
cp .env.example .env
# 編輯 .env — 設定你的 LLM_MODEL 和 API 金鑰
```

### 使用方式

```bash
# 🔍 預覽模式 — 只顯示產出的程式碼，不寫入檔案
python3 main.py "實作 email 驗證功能" src/validator.py --dry-run

# 🛠 本地開發 — 執行 pipeline，跳過建立 PR
python3 main.py "修復 SQL injection 漏洞" src/db.py --skip-pr

# 🚀 完整流程 — 程式碼 + 測試 + 自動修復 + PR
python3 main.py "加入 rate limiting 中介層" src/middleware.py

# 💬 互動模式 — AI 信心不足時暫停等待確認
python3 main.py "重構支付模組" src/payment.py --interactive

# 📝 儲存工程報告
python3 main.py "優化快取策略" src/cache.py --report report.md

# ⚡ 快速模式 — 跳過 Step 5 審查
python3 main.py "加入 input validation" src/forms.py --skip-review --skip-pr
```

### CLI 參數

| 參數 | 說明 |
|------|------|
| `--dry-run` | 預覽產出的程式碼，不寫入檔案 |
| `--skip-pr` | 跳過 GitHub PR 建立 |
| `--skip-review` | 跳過 Step 5 優化審查 |
| `--interactive` | 信心不足時暫停等待使用者確認 |
| `--report FILE` | 將結構化工程報告儲存到檔案 |
| `--test-path PATH` | 自訂測試目錄（預設：`tests/`）|
| `--log-level LEVEL` | 設定日誌等級：`DEBUG`、`INFO`、`WARNING` |

---

## 📁 專案結構

```
ai-dev-system/
├── main.py                      # 協調器 — 5 步驟 pipeline + CLI
├── config.py                    # 型別化的 .env 設定管理
│
├── agents/
│   ├── dev_agent.py             # 5 步驟 AI 工程師（核心）
│   ├── prompts.py               # 各步驟專用 prompt 模板
│   └── pipeline_models.py       # 各步驟的型別化資料模型
│
├── tools/
│   ├── github_tool.py           # Git CLI + PyGithub API 操作
│   ├── test_runner.py           # pytest 執行器（結構化結果）
│   └── file_manager.py          # 檔案 I/O + 備份支援
│
├── tests/                       # 23 個單元測試（全部 mock，無需 API）
│   ├── test_dev_agent.py        # 14 個測試 — pipeline + 各步驟
│   ├── test_file_manager.py     # 5 個測試 — 檔案操作
│   └── test_runner_test.py      # 4 個測試 — 測試執行器邊界條件
│
├── pyproject.toml               # Python 專案設定
├── .env.example                 # 環境變數模板
├── .gitignore
├── LICENSE
├── README.md                    # 英文文件
└── README-ZH.md                 # 本文件（繁體中文）
```

---

## 🔧 支援的模型

本系統使用 [litellm](https://docs.litellm.ai/docs/providers) 實現模型無關的 LLM 整合，支援所有主流供應商：

| 供應商 | 模型字串範例 | 備註 |
|-------|------------|------|
| **OpenAI** | `gpt-4o`、`gpt-4o-mini` | 品質最佳，需要 API 金鑰 |
| **Ollama** | `ollama/llama3`、`ollama/codellama` | 本地執行、隱私、免費 |
| **Anthropic** | `claude-3-haiku-20240307` | 速度快、結構化輸出佳 |
| **Groq** | `groq/llama3-70b-8192` | 超高速推論 |
| **DeepSeek** | `deepseek/deepseek-coder` | 程式碼專用 |

### 本地模型範例（不需要 API 金鑰）

```bash
# 安裝 Ollama 並拉取模型
ollama pull llama3

# 在 .env 中設定
LLM_MODEL=ollama/llama3

# 執行
python3 main.py "建立 REST API endpoint" src/api.py --skip-pr
```

---

## 🧪 執行測試

```bash
# 執行所有測試
python3 -m pytest tests/ -v

# 含覆蓋率報告
python3 -m pytest tests/ -v --cov

# 執行特定測試類別
python3 -m pytest tests/test_dev_agent.py::TestFullPipeline -v
```

所有 23 個測試都已完全 mock — **執行測試套件不需要任何 LLM API 呼叫**。

---

## 📊 Pipeline 輸出範例

執行系統時，你會看到每個步驟的結構化輸出：

```
╭──────── Pipeline Start ────────╮
│ 🤖 AI 軟體工程師                │
│                                 │
│ 任務:   修復登入驗證功能          │
│ 檔案:   src/auth.py             │
│ 模型:   gpt-4o-mini             │
╰─────────────────────────────────╯

━━━ 執行 5 步驟工程 Pipeline ━━━

┌──── Step 1：需求理解 ─────────────┐
│ 摘要:     修復登入驗證             │
│ 信心度:   🟢 92%                  │
│ 邊界條件: • 空白 email             │
│           • SQL injection         │
│           • unicode 字元           │
└───────────────────────────────────┘

┌──── Step 2：解法設計 ─────────────┐
│ 方法:     加入輸入驗證             │
│ 時間:     O(n)                    │
│ 空間:     O(1)                    │
└───────────────────────────────────┘

📄 auth.py (342 字元)              ← Step 3
🧪 tests/test_auth.py (289 字元)   ← Step 4

┌──── Step 5：優化審查 ─────────────┐
│ 品質評分:   8/10                  │
│ 裁定:       ✅ 可交付              │
└───────────────────────────────────┘

🧪 執行測試... ✅ 全部通過！
📤 建立 PR...
🎉 PR 已建立: https://github.com/.../pull/1
```

---

## 🔮 發展藍圖

- [x] **5 步驟 Pipeline** — 結構化工程流程
- [ ] **RAG 整合 (v1.1)** — 索引整個 repo 以提供完整 codebase context
- [ ] **GitHub Issue 整合 (v1.2)** — 自動讀取並嘗試修復 Open Issues
- [ ] **多 Agent 協作 (v2.0)** — PM → Dev → QA 工作流程
- [ ] **獨立 QA Agent** — 專責找 Bug 的驗證代理人
- [ ] **GitHub Actions 整合** — 從 PR 評論或 Issue 觸發 pipeline

---

## 🤝 貢獻指南

歡迎貢獻！請隨時提交 Pull Request。

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 執行測試 (`python3 -m pytest tests/ -v`)
4. Commit 變更 (`git commit -m 'Add amazing feature'`)
5. Push 到分支 (`git push origin feature/amazing-feature`)
6. 開啟 Pull Request

---

## 📜 授權

本專案採用 MIT 授權條款 — 詳見 [LICENSE](LICENSE) 檔案。

---

## 🙏 致謝

- [litellm](https://github.com/BerriAI/litellm) — 通用 LLM API 介面
- [Rich](https://github.com/Textualize/rich) — 精美的終端輸出
- [PyGithub](https://github.com/PyGithub/PyGithub) — GitHub API 客戶端

---

<p align="center">
  由 🤖 AI 建造，人類審查。
</p>
