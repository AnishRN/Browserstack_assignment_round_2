# El País Article Scraper & Analyzer - Specification

## Project Overview
- **Project Name**: El País Article Scraper & Analyzer
- **Type**: Streamlit Web Application
- **Core Functionality**: Scrape articles from El País Opinion section, translate headers, analyze repeated words
- **Target Users**: Data analysts, researchers, and anyone interested in Spanish news content

## Technology Stack
- **Frontend**: Streamlit (Python)
- **Web Scraping**: BeautifulSoup4, Requests
- **Translation**: MyMemory Translation API (free)
- **Image Download**: Requests
- **Browser Testing**: BrowserStack API

## UI/UX Specification

### Layout Structure
- **Header**: Project title with El País branding
- **Sidebar**: Navigation and configuration options
- **Main Content**: 
  - Article display section
  - Translation results
  - Word analysis results

### Visual Design
- **Primary Color**: #00309B (El País blue)
- **Secondary Color**: #C4151C (El País red)
- **Background**: Light gray #F5F5F5
- **Accent Colors**: 
  - Success: #28A745
  - Warning: #FFC107
  - Error: #DC3545

### Components
1. **Navigation Buttons**: Scrappe Articles, Translate, Analyze Words
2. **Article Cards**: Display title, content preview, cover image
3. **Translation Panel**: Original Spanish title, English translation
4. **Word Frequency Chart**: Bar chart of repeated words

## Functionality Specification

### Core Features

1. **Web Scraping Module**
   - Navigate to El País Opinion section (https://elpais.com/opinion/)
   - Fetch first 5 articles
   - Extract: title, content, cover image URL
   - Handle pagination if needed

2. **Translation Module**
   - Use MyMemory Translation API (free, no API key required)
   - Translate article titles from Spanish to English
   - Handle API errors gracefully

3. **Word Analysis Module**
   - Parse translated headers
   - Count word occurrences
   - Identify words appearing more than twice
   - Display results with counts

4. **Image Download Module**
   - Download cover images to local ./downloads folder
   - Handle missing images gracefully
   - Show download status

5. **BrowserStack Integration**
   - Configure BrowserStack credentials
   - Run tests across 5 parallel threads
   - Support desktop and mobile browsers
   - Display test results

## Acceptance Criteria

1. ✅ Successfully scrape 5 articles from El País Opinion section
2. ✅ Display article titles and content in Spanish
3. ✅ Download cover images when available
4. ✅ Translate headers to English using free API
5. ✅ Identify and display repeated words (count > 2)
6. ✅ Provide Streamlit UI with clear navigation
7. ✅ Support BrowserStack cross-browser testing

## File Structure
```
Browserstack_1/
├── app.py                 # Main Streamlit application
├── requirements.txt      # Python dependencies
├── scraper.py           # Web scraping module
├── translator.py        # Translation API module
├── analyzer.py          # Word analysis module
├── browserstack.py      # BrowserStack integration
├── downloads/           # Downloaded images folder
└── SPEC.md             # This specification
