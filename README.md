# El País Article Scraper & Analyzer

A Streamlit-based web application that scrapes articles from El País Opinion section, translates headers, and analyzes word frequency.

## Features

- 📥 **Web Scraping**: Fetch articles from El País Opinion section
- 🌐 **Translation**: Translate Spanish article headers to English using MyMemory Translation API
- 📊 **Word Analysis**: Analyze word frequency and find repeated words
- 🖼️ **Image Download**: Download cover images for articles
- 🧪 **Cross-Browser Testing**: BrowserStack integration for testing across multiple browsers

## Installation

1. Clone or download this project

2. Install dependencies:
```
bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```
bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Application Workflow

1. **Scrape Articles**: Click "Scrape Articles" to fetch articles from El País Opinion section
2. **Translate Titles**: Click "Translate Titles" to translate article headers to English
3. **Analyze Words**: Click "Analyze Words" to see word frequency analysis

### BrowserStack Testing

1. Enter your BrowserStack credentials in the sidebar
2. Click "Test BrowserStack Connection" to verify
3. Configure test settings (URL, parallel threads)
4. Click "Run Tests" to execute cross-browser tests

## Environment Variables

For BrowserStack testing, you can set:
- `BROWSERSTACK_USERNAME`: Your BrowserStack username
- `BROWSERSTACK_ACCESS_KEY`: Your BrowserStack access key

Or enter them directly in the Streamlit sidebar.

## Project Structure

```
Browserstack_1/
├── app.py                 # Main Streamlit application
├── scraper.py            # Web scraping module
├── translator.py         # Translation API module
├── analyzer.py           # Word analysis module
├── browserstack.py       # BrowserStack integration
├── requirements.txt      # Python dependencies
├── downloads/            # Downloaded images folder
├── SPEC.md              # Project specification
└── README.md            # This file
```

## API Used

- **Translation**: MyMemory Translation API (Free)
  - No API key required
  - Rate limit: 1000 words/day for free tier

## Screenshots

The application features:
- Clean Spanish news interface with El País branding
- Article cards with title, content, and cover images
- Translation panel showing original and translated text
- Word frequency visualization with bar charts

## License

This project is for educational purposes. Please respect El País's terms of service when scraping.
