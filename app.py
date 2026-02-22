import streamlit as st
from scraper import ElPaisScraper, create_downloads_folder
from translator import MyMemoryTranslator
from analyzer import find_repeated_words, get_top_words
from pdf_generator import generate_analysis_pdf
import os

# Page configuration
st.set_page_config(
    page_title="El País Scraper & Analyzer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling with visible colors
st.markdown("""
<style>
    /* Main background and text colors */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #000000 !important;
        text-align: center;
        padding: 1rem;
        border-bottom: 3px solid #1E3A5F;
        margin-bottom: 2rem;
    }
    
    /* Section header styling */
    .section-header {
        font-size: 1.5rem;
        color: #000000 !important;
        font-weight: bold;
        padding: 0.75rem;
        background-color: #E8F4FD;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 5px solid #1E3A5F;
    }
    
    /* Article card styling */
    .article-card {
        padding: 1rem;
        border: 2px solid #1E3A5F;
        border-radius: 10px;
        margin-bottom: 1rem;
        background-color: #F5F9FC;
    }
    
    .article-card h3 {
        color: #000000 !important;
        font-weight: bold;
    }
    
    .article-card p {
        color: #333333 !important;
    }
    
    /* Translation box styling */
    .translation-box {
        padding: 1rem;
        background-color: #E8F4FD;
        border-left: 5px solid #1E3A5F;
        margin: 0.75rem 0;
        border-radius: 5px;
    }
    
    .translation-box p {
        color: #000000 !important;
        margin: 0.5rem 0;
    }
    
    /* Text visibility improvements */
    .stMarkdown {
        color: #000000 !important;
    }
    
    p, div, span {
        color: #000000 !important;
    }
    
    /* Headers in main content */
    h1, h2, h3, h4 {
        color: #000000 !important;
    }
    
    /* Info and warning boxes */
    .stAlert {
        color: #000000 !important;
    }
    
    /* Sidebar text */
    .css-17lntkn {
        color: #000000 !important;
    }
    
    /* Streamlit components */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        color: #000000 !important;
        font-weight: bold;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #F0F4F8;
    }
    
    /* Success/Error/Info messages */
    .stSuccess {
        background-color: #D4EDDA;
        color: #155724 !important;
    }
    
    .stWarning {
        background-color: #FFF3CD;
        color: #856404 !important;
    }
    
    .stInfo {
        background-color: #D1ECF1;
        color: #0C5460 !important;
    }
    
    /* Custom status indicator */
    .status-item {
        color: #000000 !important;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
    
    /* Analysis result styling */
    .analysis-result {
        padding: 1rem;
        background-color: #F5F9FC;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .analysis-result p {
        color: #000000 !important;
        margin: 0.25rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "articles" not in st.session_state:
    st.session_state.articles = []
if "translated" not in st.session_state:
    st.session_state.translated = []
if "analysis" not in st.session_state:
    st.session_state.analysis = {}
if "current_page" not in st.session_state:
    st.session_state.current_page = "Scrape"

# Sidebar navigation
st.sidebar.title("📰 El País Tools")
st.sidebar.markdown("---")

# Navigation menu
pages = ["Scrape", "Translate", "Analyze", "Export"]
selected_page = st.sidebar.radio("Navigation", pages, index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0)

# Update current page
st.session_state.current_page = selected_page

# Show current status in sidebar
st.sidebar.markdown("### 📊 Status")
if st.session_state.articles:
    st.sidebar.success(f"✅ Scraped: {len(st.session_state.articles)} articles")
else:
    st.sidebar.error("❌ No articles scraped")

if st.session_state.translated:
    st.sidebar.success(f"✅ Translated: {len(st.session_state.translated)} titles")
else:
    st.sidebar.error("❌ Not translated")

if st.session_state.analysis:
    st.sidebar.success("✅ Analyzed")
else:
    st.sidebar.error("❌ Not analyzed")

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.markdown("""
This app scrapes articles from El País Opinion section, translates titles, and performs word analysis.
""")

# Main content
st.markdown('<p class="main-header">📰 El País Scraper & Analyzer</p>', unsafe_allow_html=True)

# === SCRAPE PAGE ===
if selected_page == "Scrape":
    st.markdown('<p class="section-header">1️⃣ Scrape Articles</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        num = st.slider("Number of articles", 1, 10, 5)
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🕷️ Scrape Articles", type="primary", key="scrape_btn"):
            with st.spinner("Scraping articles from El País..."):
                scraper = ElPaisScraper()
                st.session_state.articles = scraper.scrape_opinion_articles(num)
                st.session_state.translated = []
                st.session_state.analysis = {}
            st.success(f"✅ Successfully scraped {len(st.session_state.articles)} articles!")
    
    st.markdown("---")
    
    # Display scraped articles
    if st.session_state.articles:
        st.markdown(f"### 📄 Found {len(st.session_state.articles)} Articles")
        
        for i, a in enumerate(st.session_state.articles):
            with st.container():
                st.markdown(f"""
                <div class="article-card">
                    <h3>{i+1}. {a['title']}</h3>
                    <p><strong>Author:</strong> {a.get('author', 'Unknown')} | <strong>Date:</strong> {a.get('date', 'Unknown')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show image if available
                if a.get("image_url"):
                    st.image(a["image_url"], caption=a.get("title", "Article cover"), width=400)
                
                with st.expander("📝 View Article Content"):
                    st.write(a["content"])
                
                st.markdown("---")
    else:
        st.info("👆 Click 'Scrape Articles' to fetch articles from El País Opinion section")

# === TRANSLATE PAGE ===
elif selected_page == "Translate":
    st.markdown('<p class="section-header">2️⃣ Translate Titles</p>', unsafe_allow_html=True)
    
    if not st.session_state.articles:
        st.warning("⚠️ Please scrape articles first!")
    else:
        if st.button("🌐 Translate Titles", type="primary", key="translate_btn"):
            with st.spinner("Translating titles..."):
                t = MyMemoryTranslator()
                titles = [a["title"] for a in st.session_state.articles]
                st.session_state.translated = t.translate_batch(titles)
            st.success("✅ Translation complete!")
        
        st.markdown("---")
        
        if st.session_state.translated and len(st.session_state.translated) > 0:
            st.markdown("### 🌎 Translated Titles")
            
            for i, (es, en) in enumerate(zip([a["title"] for a in st.session_state.articles], st.session_state.translated)):
                st.markdown(f"""
                <div class="translation-box">
                    <p><strong>Original (Spanish):</strong> {es}</p>
                    <p><strong>Translated (English):</strong> {en}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👆 Click 'Translate Titles' to translate article titles")

# === ANALYZE PAGE ===
elif selected_page == "Analyze":
    st.markdown('<p class="section-header">3️⃣ Analyze Words</p>', unsafe_allow_html=True)
    
    if not st.session_state.translated:
        st.warning("⚠️ Please translate titles first!")
    else:
        if st.button("📊 Analyze Words", type="primary", key="analyze_btn"):
            with st.spinner("Analyzing word frequency..."):
                rpt = find_repeated_words(st.session_state.translated)
                top = get_top_words(st.session_state.translated)
                st.session_state.analysis = {"repeated": rpt, "top": top}
            st.success("✅ Analysis complete!")
        
        st.markdown("---")
        
        if st.session_state.analysis and len(st.session_state.analysis) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🔁 Repeated Words")
                if st.session_state.analysis.get("repeated") and len(st.session_state.analysis["repeated"]) > 0:
                    for w, c in st.session_state.analysis["repeated"].items():
                        st.markdown(f"""
                        <div class="analysis-result">
                            <p><strong>{w}</strong>: {c} occurrences</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("No repeated words found.")
            
            with col2:
                st.markdown("### 🏆 Top Words")
                if st.session_state.analysis.get("top") and len(st.session_state.analysis["top"]) > 0:
                    for w, c in st.session_state.analysis["top"]:
                        st.markdown(f"""
                        <div class="analysis-result">
                            <p><strong>{w}</strong>: {c} occurrences</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("No top words found.")
        else:
            st.info("👆 Click 'Analyze Words' to perform word analysis")

# === EXPORT PAGE ===
elif selected_page == "Export":
    st.markdown('<p class="section-header">4️⃣ Export PDF</p>', unsafe_allow_html=True)
    
    if not st.session_state.articles:
        st.warning("⚠️ Please scrape articles first!")
    elif not st.session_state.translated:
        st.warning("⚠️ Please translate titles first!")
    else:
        if st.button("📄 Generate PDF", type="primary", key="pdf_btn"):
            with st.spinner("Generating PDF report..."):
                path = generate_analysis_pdf(
                    st.session_state.articles,
                    st.session_state.translated,
                    st.session_state.analysis
                )
                with open(path, "rb") as f:
                    st.download_button(
                        label="💾 Download PDF Report",
                        data=f,
                        file_name="el_pais_report.pdf",
                        type="primary"
                    )
            st.success("✅ PDF generated successfully!")
        
        st.markdown("---")
        st.info("💡 The PDF report includes all scraped articles, translations, and word analysis.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #000000; padding: 1rem; background-color: #F0F4F8; border-radius: 8px;">
    <p><strong>El País Scraper & Analyzer</strong> | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
