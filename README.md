# 🔍 Page Pulse - URL Auditor

A powerful web tool that audits any URL and returns comprehensive SEO and performance metrics. Built with Python FastAPI.

## 🚀 Live Demo

**Deployed URL:** https://page-pulse-python.onrender.com 

## 📋 Features

- ✅ HTTP status code and response time
- ✅ Page title and meta description extraction
- ✅ H1 tag count
- ✅ Images missing alt text detection
- ✅ Approximate word count
- ✅ Comprehensive error handling
- ✅ Clean, responsive UI

## 🛠️ Technology Stack

- **Backend:** Python 3.11 + FastAPI
- **HTTP Client:** httpx (async)
- **HTML Parsing:** BeautifulSoup4 + lxml
- **Frontend:** Vanilla HTML + CSS + JavaScript
- **Deployment:** Render.com

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

- ## 🤖 AI Tools Used

I used AI tools (ChatGPT/Claude) as coding assistants throughout this project:

1. **Code generation** - Used for initial FastAPI boilerplate, test skeletons, and documentation templates
2. **Debugging support** - Helped troubleshoot Render deployment issues (Python version mismatch, lxml dependency problems, module import errors)
3. **Test case design** - Assisted in creating comprehensive test coverage including edge cases and failure scenarios
4. **Documentation structure** - Helped organize the README with clear API contracts and setup instructions

**My judgment and decisions** (not AI-generated):
- Choosing `html.parser` over `lxml` for deployment compatibility
- Designing the caching improvement (what I'd change with another day)
- Structuring code with separation of concerns (audit/models/main separation)
- Setting 15-second timeout for Indian users accessing international sites
- Prioritizing failure case tests over edge case tests

> ⚠️ **Note:** While AI assisted with boilerplate and debugging, all architectural decisions, error handling design, and test prioritization were my own.
