# Search Setup Guide: Google Search Grounding + Tavily

This guide explains how to set up and use the combined search functionality that queries both **Google Search** and **Tavily** simultaneously.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [What is Search Grounding?](#what-is-search-grounding)
3. [Setup Instructions](#setup-instructions)
4. [Usage Examples](#usage-examples)
5. [API Comparison](#api-comparison)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This project now supports **three search tools**:

1. **`web_search()`** - Tavily search only
2. **`google_search_grounding()`** - Google Custom Search only  
3. **`combined_web_search()`** - Both Tavily and Google simultaneously ⚡

### Why Use Combined Search?

- **🔄 Redundancy**: If one API fails, you still get results from the other
- **📊 Comparison**: Compare search quality between providers
- **🎯 Coverage**: Different engines find different information
- **⚡ Speed**: Parallel execution means total time ≈ slowest search (not sum of both)

---

## 🔍 What is Search Grounding?

**Grounding** means anchoring AI-generated responses in real, verifiable sources instead of allowing the AI to "hallucinate" information.

### How It Works:

```
User Query → Search APIs → Real Web Results → AI reads results → Grounded Answer
```

### Benefits:

- ✅ **Accuracy**: Responses based on real data
- ✅ **Credibility**: Users can verify sources
- ✅ **Currency**: Get latest information
- ✅ **Trust**: No hallucinations

---

## 🛠️ Setup Instructions

### Step 1: Install Dependencies

The required dependencies are already in `requirements.txt`. Install them:

```bash
# Activate your virtual environment first
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

Key packages installed:
- `tavily-python` - Tavily Search API client
- `requests` - For Google Custom Search API calls
- `google-cloud-discoveryengine` - Optional: For advanced Google features

### Step 2: Get API Keys

#### Option A: Tavily API (Recommended for Getting Started)

1. Go to [https://tavily.com](https://tavily.com)
2. Sign up for a free account
3. Get your API key from the dashboard
4. **Free tier**: 1,000 searches/month

#### Option B: Google Custom Search API

1. **Enable Google Custom Search API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing one
   - Enable "Custom Search API"
   - Go to "Credentials" → Create API Key

2. **Create Custom Search Engine**:
   - Go to [Programmable Search Engine](https://programmablesearchengine.google.com)
   - Click "Add" to create new search engine
   - Choose "Search the entire web"
   - Get your **Search Engine ID (CX)**

3. **Pricing**:
   - **Free tier**: 100 queries/day
   - **Paid**: $5 per 1,000 queries after free tier

#### Option C: Both (Recommended for Production)

Use both APIs for maximum coverage and redundancy!

### Step 3: Configure Environment Variables

Create or update your `.env` file in the project root:

```bash
# .env file

# OpenAI API Key (for the agent)
OPENAI_API_KEY=sk-your-openai-key-here

# Tavily Search API
TAVILY_API_KEY=tvly-your-tavily-key-here

# Google Custom Search API (optional)
GOOGLE_SEARCH_API_KEY=AIza-your-google-api-key-here
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id-here

# LangSmith (optional, for monitoring)
LANGCHAIN_API_KEY=ls_your-langsmith-key-here
```

### Step 4: Verify Configuration

Test your setup with the demo mode:

```bash
# Test with Tavily only
python main.py --demo "artificial intelligence"

# Test with Google only (if configured)
python main.py --demo "machine learning"

# Test combined (if both configured)
python main.py --demo "OpenAI GPT-4"
```

---

## 📚 Usage Examples

### Example 1: Command-Line Demo

Run a combined search from the command line:

```bash
python main.py --demo "Johnson City TN gas utility provider"
```

**Output shows**:
- ⏱️ Execution time
- 🟦 Tavily results (with relevance scores)
- 🟥 Google results (with snippets)
- 📈 Comparison summary

### Example 2: Python Code - Combined Search

```python
from tools.search_tools import combined_web_search

# Search both Tavily and Google simultaneously
result = combined_web_search("OpenAI GPT-4", max_results=5)

# Check overall status
print(f"Status: {result['status']}")  # "success", "partial", or "error"
print(f"Summary: {result['summary']}")

# Access Tavily results
if result['tavily']['status'] == 'success':
    print(f"\nTavily found {result['tavily']['count']} results:")
    for item in result['tavily']['results']:
        print(f"  - {item['title']}")
        print(f"    Score: {item['score']:.2f}")
        print(f"    URL: {item['url']}")

# Access Google results
if result['google']['status'] == 'success':
    print(f"\nGoogle found {result['google']['count']} results:")
    for item in result['google']['results']:
        print(f"  - {item['title']}")
        print(f"    Domain: {item['displayLink']}")
        print(f"    URL: {item['url']}")

# Access all results combined
print(f"\nTotal results: {result['total_count']}")
for item in result['combined_results']:
    print(f"  - {item['title']}")
```

### Example 3: Python Code - Tavily Only

```python
from tools.search_tools import web_search

# Search using Tavily only
result = web_search("machine learning tutorials", max_results=5)

if result['status'] == 'success':
    print(f"Found {result['count']} results:")
    for item in result['results']:
        print(f"  {item['title']} (score: {item['score']:.2f})")
        print(f"  {item['url']}")
        print(f"  {item['content'][:200]}...")
        print()
```

### Example 4: Python Code - Google Only

```python
from tools.search_tools import google_search_grounding

# Search using Google only
result = google_search_grounding("deep learning frameworks", max_results=5)

if result['status'] == 'success':
    print(f"Found {result['count']} results:")
    for item in result['results']:
        print(f"  {item['title']}")
        print(f"  Domain: {item['displayLink']}")
        print(f"  {item['snippet']}")
        print()
```

### Example 5: Handling Partial Success

The combined search can handle scenarios where one API succeeds and the other fails:

```python
from tools.search_tools import combined_web_search

result = combined_web_search("quantum computing", max_results=5)

if result['status'] == 'success':
    print("✅ Both searches succeeded!")
    
elif result['status'] == 'partial':
    print("⚠️ One search succeeded, one failed")
    print(f"Summary: {result['summary']}")
    # You still get results from the successful search
    
elif result['status'] == 'error':
    print("❌ Both searches failed")
    print(f"Tavily error: {result['tavily']['error']}")
    print(f"Google error: {result['google']['error']}")
```

---

## 📊 API Comparison

| Feature | Tavily | Google Custom Search |
|---------|--------|---------------------|
| **Designed for AI** | ✅ Yes | ❌ No (general purpose) |
| **Free tier** | 1,000 queries/month | 100 queries/day |
| **Relevance scores** | ✅ Yes (0.0-1.0) | ❌ No (ordered by relevance) |
| **Content snippets** | ✅ Yes (cleaned) | ✅ Yes (raw) |
| **Search depth** | ✅ Basic/Advanced | ❌ Single level |
| **Response format** | Clean, structured | Standard JSON |
| **Best for** | LLM applications | General web search |
| **Setup complexity** | 🟢 Easy (1 API key) | 🟡 Medium (API key + CX) |

### When to Use Which:

- **Tavily**: Best for LLM applications, RAG, AI agents
- **Google**: Best for comprehensive coverage, familiar results
- **Combined**: Best for production (redundancy + coverage)

---

## 🐛 Troubleshooting

### Issue 1: "No search API configured"

**Error message**:
```
❌ Error: No search API configured
Please set at least one of:
  - TAVILY_API_KEY
  - GOOGLE_SEARCH_API_KEY
  - GOOGLE_SEARCH_ENGINE_ID
```

**Solution**:
1. Check that `.env` file exists in project root
2. Verify API keys are set correctly (no spaces, no quotes)
3. Restart your Python session to reload environment variables

### Issue 2: "Search request failed: 401 Unauthorized"

**Tavily error**:
- Check `TAVILY_API_KEY` is correct
- Verify your account is active at [tavily.com](https://tavily.com)

**Google error**:
- Check `GOOGLE_SEARCH_API_KEY` is correct
- Verify API is enabled in Google Cloud Console
- Check billing is enabled (required even for free tier)

### Issue 3: "Invalid JSON response from Google API"

**Possible causes**:
- `GOOGLE_SEARCH_ENGINE_ID` (CX) is incorrect
- API quota exceeded
- API not enabled in Google Cloud Console

**Solution**:
1. Verify CX ID from [Programmable Search Engine](https://programmablesearchengine.google.com)
2. Check quota usage in Google Cloud Console
3. Enable Custom Search API in your project

### Issue 4: Tavily works but Google doesn't

**This is expected if**:
- You only configured Tavily (which is fine!)
- The combined search will show "partial" status
- You still get Tavily results

**To fix**:
- Follow Step 2 Option B to configure Google Search
- Or just use `web_search()` for Tavily-only searches

### Issue 5: Import errors

**Error**: `ModuleNotFoundError: No module named 'requests'`

**Solution**:
```bash
pip install -r requirements.txt
```

### Issue 6: Slow response times

**Possible causes**:
- Network latency
- API rate limiting
- Large max_results value

**Solutions**:
- Reduce `max_results` (default: 5)
- Use `search_depth="basic"` for Tavily (faster but less comprehensive)
- Check your internet connection

---

## 🚀 Advanced Usage

### Custom Timeout

Modify timeout for Google Search (default: 10 seconds):

```python
# In tools/search_tools.py, line ~373
response = requests.get(
    _GOOGLE_SEARCH_URL,
    params=params,
    timeout=20  # Increase to 20 seconds
)
```

### Search Depth Control (Tavily)

```python
from tools.search_tools import web_search

# Fast search (basic depth)
result = web_search("query", max_results=5)

# Comprehensive search (advanced depth)
# Modify in search_tools.py line ~140-144
search_results = _tavily_client.results(
    query=query,
    max_results=max_results,
    search_depth="advanced"  # or "basic" for faster results
)
```

### Caching Results

To avoid repeated API calls, implement caching:

```python
import json
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query: str, max_results: int = 5):
    """Cache search results to avoid repeated API calls"""
    from tools.search_tools import combined_web_search
    return json.dumps(combined_web_search(query, max_results))

# Use it
result = json.loads(cached_search("my query"))
```

---

## 📝 Summary

You now have:

✅ **Three search functions**:
- `web_search()` - Tavily only
- `google_search_grounding()` - Google only
- `combined_web_search()` - Both simultaneously

✅ **Parallel execution**: Searches run simultaneously for speed

✅ **Comprehensive results**: Compare and contrast different sources

✅ **Robust error handling**: Graceful degradation if one API fails

✅ **Easy-to-use API**: Consistent return format across all functions

---

## 📖 Additional Resources

- **Tavily Documentation**: [https://docs.tavily.com](https://docs.tavily.com)
- **Google Custom Search API**: [https://developers.google.com/custom-search](https://developers.google.com/custom-search)
- **Project README**: See `README.md` for general project information
- **Architecture**: See `ARCHITECTURE.md` for system design

---

## 💡 Tips

1. **Start with Tavily**: Easier setup, designed for AI
2. **Add Google later**: For production redundancy
3. **Use demo mode**: Test APIs before integrating
4. **Monitor usage**: Check API quotas regularly
5. **Cache results**: Avoid unnecessary API calls
6. **Handle errors**: Always check `status` field before using results

---

**Happy Searching! 🔍**

For questions or issues, check the troubleshooting section above or review the inline code comments in `tools/search_tools.py`.

