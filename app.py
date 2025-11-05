"""
ClauseWise - AI-Powered Legal Document Analyzer
Main Streamlit Application
"""

import streamlit as st
import os
from pathlib import Path
import json
import pandas as pd

# Import utility modules
from utils.document_processor import DocumentProcessor
from utils.clause_analyzer import ClauseAnalyzer
from utils.ner_extractor import LegalNERExtractor
from utils.doc_classifier import DocumentClassifier
from utils.granite_client import get_granite_client, GraniteConfig

# Page configuration
st.set_page_config(
    page_title="ClauseWise - Legal Document Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .entity-box {
        background-color: #e8f4f8;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .simplified-clause {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #4caf50;
    }
    .original-clause {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed_doc' not in st.session_state:
    st.session_state.processed_doc = None
if 'clauses' not in st.session_state:
    st.session_state.clauses = None
if 'entities' not in st.session_state:
    st.session_state.entities = None
if 'classification' not in st.session_state:
    st.session_state.classification = None

def main():
    """Main application function"""
    
    # Header
    st.markdown('<div class="main-header">⚖️ ClauseWise</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">AI-Powered Legal Document Analyzer | Simplify • Decode • Classify</div>',
        unsafe_allow_html=True
    )
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📋 Features")
        st.markdown("""
        - 📝 **Clause Simplification**
        - 🏷️ **Named Entity Recognition**
        - 📑 **Clause Extraction**
        - 🗂️ **Document Classification**
        - 📄 **Multi-Format Support**
        """)
        
        st.markdown("---")
        st.markdown("### 🔧 Powered By")
        st.markdown("""
        - IBM Granite AI
        - Streamlit
        - HuggingFace
        - Python
        """)
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("ClauseWise uses cutting-edge AI to make legal documents accessible to everyone.")
    
    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📤 Upload Document",
        "🗂️ Classification",
        "📑 Clause Analysis",
        "🏷️ Entity Extraction",
        "💡 Simplification"
    ])
    
    # Tab 1: Upload Document
    with tab1:
        st.markdown('<div class="section-header">Upload Legal Document</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a legal document (PDF, DOCX, or TXT)",
            type=['pdf', 'docx', 'txt'],
            help="Upload your legal document for analysis"
        )
        
        if uploaded_file:
            # Save uploaded file temporarily
            temp_path = Path("/tmp") / uploaded_file.name
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            with st.spinner("Processing document..."):
                try:
                    # Process document
                    processor = DocumentProcessor()
                    doc_data = processor.process_file(str(temp_path))
                    st.session_state.processed_doc = doc_data
                    
                    st.success("✅ Document processed successfully!")
                    
                    # Display document info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Word Count", f"{doc_data['metadata']['word_count']:,}")
                    with col2:
                        st.metric("Estimated Clauses", doc_data['metadata']['estimated_clauses'])
                    with col3:
                        st.metric("Legal Density", f"{doc_data['metadata']['legal_keyword_density']:.1f}%")
                    
                    # Display document preview
                    st.markdown("### 📄 Document Preview")
                    preview_text = doc_data['text'][:1000] + "..." if len(doc_data['text']) > 1000 else doc_data['text']
                    st.text_area("First 1000 characters", preview_text, height=200)
                    
                    # Analyze button
                    if st.button("🚀 Analyze Document", type="primary", use_container_width=True):
                        analyze_document(doc_data['text'])
                    
                except Exception as e:
                    st.error(f"Error processing document: {str(e)}")
                finally:
                    # Clean up temp file
                    if temp_path.exists():
                        temp_path.unlink()
        else:
            st.info("👆 Please upload a legal document to begin analysis")
            
            # Sample documents section
            st.markdown("---")
            st.markdown("### 📚 Try Sample Documents")
            st.markdown("Don't have a document? You can test with sample legal text below:")
            
            sample_type = st.selectbox("Select sample type", [
                "Non-Disclosure Agreement",
                "Service Agreement",
                "Employment Contract"
            ])
            
            if st.button("Load Sample"):
                sample_text = get_sample_document(sample_type)
                st.session_state.processed_doc = {
                    'text': sample_text,
                    'filename': f'sample_{sample_type.lower().replace(" ", "_")}.txt',
                    'file_type': '.txt',
                    'metadata': {
                        'word_count': len(sample_text.split()),
                        'char_count': len(sample_text),
                        'estimated_clauses': 10,
                        'legal_keyword_density': 75.0
                    }
                }
                analyze_document(sample_text)
                st.rerun()
    
    # Tab 2: Classification
    with tab2:
        st.markdown('<div class="section-header">Document Classification</div>', unsafe_allow_html=True)
        
        if st.session_state.classification:
            classification = st.session_state.classification
            
            # Display classification result
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"### 📋 Document Type")
                st.markdown(f'<div class="metric-card"><h2 style="color: #1f77b4; margin: 0;">{classification["document_type"]}</h2></div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"### 🎯 Confidence")
                st.markdown(f'<div class="metric-card"><h2 style="color: #4caf50; margin: 0;">{classification["confidence"]}%</h2></div>', unsafe_allow_html=True)
            
            # Classification details
            st.markdown("### 📊 Classification Details")
            st.markdown(f"**Method:** {classification['method']}")
            st.markdown(f"**Reasoning:** {classification.get('reasoning', 'N/A')}")
            
            # Rule-based scores
            if 'rule_based_scores' in classification:
                st.markdown("### 🔍 Alternative Matches")
                scores_df = pd.DataFrame([
                    {"Document Type": k, "Score": v}
                    for k, v in classification['rule_based_scores'].items()
                ])
                st.dataframe(scores_df, use_container_width=True, hide_index=True)
        else:
            st.info("Upload and analyze a document to see classification results")
    
    # Tab 3: Clause Analysis
    with tab3:
        st.markdown('<div class="section-header">Clause Extraction & Breakdown</div>', unsafe_allow_html=True)
        
        if st.session_state.clauses:
            clauses = st.session_state.clauses
            
            # Summary
            st.markdown("### 📊 Clause Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Clauses", len(clauses))
            with col2:
                total_words = sum(c.get('word_count', 0) for c in clauses)
                st.metric("Total Words", f"{total_words:,}")
            with col3:
                avg_words = total_words / len(clauses) if clauses else 0
                st.metric("Avg Words/Clause", f"{avg_words:.0f}")
            
            # Clause type distribution
            clause_types = {}
            for clause in clauses:
                ctype = clause.get('type', 'General')
                clause_types[ctype] = clause_types.get(ctype, 0) + 1
            
            if clause_types:
                st.markdown("### 📈 Clause Type Distribution")
                type_df = pd.DataFrame([
                    {"Clause Type": k, "Count": v}
                    for k, v in clause_types.items()
                ])
                st.bar_chart(type_df.set_index("Clause Type"))
            
            # Display clauses
            st.markdown("### 📑 Individual Clauses")
            
            for i, clause in enumerate(clauses[:10], 1):  # Show first 10
                with st.expander(f"Clause {i}: {clause.get('type', 'General')} ({clause.get('word_count', 0)} words)"):
                    st.markdown(f"**Number/Title:** {clause.get('number', clause.get('title', 'N/A'))}")
                    st.markdown("**Content:**")
                    st.text_area(f"clause_{i}", clause.get('content', ''), height=150, key=f"clause_text_{i}")
        else:
            st.info("Upload and analyze a document to extract clauses")
    
    # Tab 4: Entity Extraction
    with tab4:
        st.markdown('<div class="section-header">Named Entity Recognition</div>', unsafe_allow_html=True)
        
        if st.session_state.entities:
            entities = st.session_state.entities
            
            # Summary
            st.markdown("### 📊 Entity Summary")
            summary_cols = st.columns(6)
            entity_types = ['parties', 'dates', 'monetary_values', 'obligations', 'legal_terms', 'contact_info']
            entity_labels = ['👥 Parties', '📅 Dates', '💰 Money', '📜 Obligations', '⚖️ Legal Terms', '📞 Contacts']
            
            for col, etype, label in zip(summary_cols, entity_types, entity_labels):
                with col:
                    count = len(entities.get(etype, []))
                    st.metric(label, count)
            
            # Parties
            if entities.get('parties'):
                st.markdown("### 👥 Parties")
                for party in entities['parties'][:5]:
                    st.markdown(f"""
                    <div class="entity-box">
                        <strong>{party.get('name', 'N/A')}</strong><br>
                        <em>Role:</em> {party.get('role', 'N/A')}<br>
                        {f"<em>Alias:</em> {party.get('alias', '')}<br>" if 'alias' in party else ""}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Dates
            if entities.get('dates'):
                st.markdown("### 📅 Dates")
                dates_df = pd.DataFrame(entities['dates'][:10])
                st.dataframe(dates_df[['date', 'format']], use_container_width=True, hide_index=True)
            
            # Monetary Values
            if entities.get('monetary_values'):
                st.markdown("### 💰 Monetary Values")
                money_df = pd.DataFrame(entities['monetary_values'][:10])
                st.dataframe(money_df[['amount', 'currency']], use_container_width=True, hide_index=True)
            
            # Obligations
            if entities.get('obligations'):
                st.markdown("### 📜 Key Obligations")
                for i, obligation in enumerate(entities['obligations'][:5], 1):
                    with st.expander(f"Obligation {i}: {obligation.get('keyword', '')}"):
                        st.write(obligation.get('clause', ''))
            
            # Legal Terms
            if entities.get('legal_terms'):
                st.markdown("### ⚖️ Legal Terms")
                terms_df = pd.DataFrame(entities['legal_terms'][:10])
                st.dataframe(terms_df[['term', 'count']], use_container_width=True, hide_index=True)
        else:
            st.info("Upload and analyze a document to extract entities")
    
    # Tab 5: Simplification
    with tab5:
        st.markdown('<div class="section-header">Clause Simplification</div>', unsafe_allow_html=True)
        
        if st.session_state.clauses:
            st.markdown("### 🔄 Simplify Clauses")
            
            # Select clauses to simplify
            num_clauses = st.slider(
                "Number of clauses to simplify",
                min_value=1,
                max_value=min(10, len(st.session_state.clauses)),
                value=3
            )
            
            if st.button("✨ Simplify Selected Clauses", type="primary"):
                with st.spinner("Simplifying clauses using IBM Granite AI..."):
                    analyzer = ClauseAnalyzer()
                    simplified = analyzer.batch_simplify(st.session_state.clauses, max_clauses=num_clauses)
                    
                    for i, result in enumerate(simplified, 1):
                        st.markdown(f"### Clause {i}: {result.get('type', 'General')}")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown('<div class="original-clause">', unsafe_allow_html=True)
                            st.markdown("**📝 Original (Legal Text)**")
                            st.write(result['original'][:500] + "..." if len(result['original']) > 500 else result['original'])
                            st.markdown(f"*Length: {result['original_length']} characters*")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown('<div class="simplified-clause">', unsafe_allow_html=True)
                            st.markdown("**✅ Simplified (Plain Language)**")
                            st.write(result['simplified'])
                            st.markdown(f"*Length: {result['simplified_length']} characters*")
                            if result.get('reduction_percentage', 0) > 0:
                                st.markdown(f"*Reduced by: {result['reduction_percentage']}%*")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown("---")
        else:
            st.info("Upload and analyze a document first to simplify clauses")
            
            # Manual clause simplification
            st.markdown("### ✍️ Simplify Custom Text")
            custom_text = st.text_area(
                "Enter legal text to simplify",
                height=150,
                placeholder="Paste complex legal text here..."
            )
            
            if st.button("Simplify Text") and custom_text:
                with st.spinner("Simplifying..."):
                    analyzer = ClauseAnalyzer()
                    result = analyzer.simplify_clause(custom_text)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Original**")
                        st.write(result['original'])
                    with col2:
                        st.markdown("**Simplified**")
                        st.success(result['simplified'])

def analyze_document(text: str):
    """Analyze document and populate session state"""
    with st.spinner("🔍 Analyzing document..."):
        # Classification
        classifier = DocumentClassifier()
        st.session_state.classification = classifier.classify_document(text, use_ai=True)
        
        # Clause extraction
        analyzer = ClauseAnalyzer()
        st.session_state.clauses = analyzer.extract_clauses(text)
        
        # Entity extraction
        ner = LegalNERExtractor()
        st.session_state.entities = ner.extract_entities(text)
        
        st.success("✅ Analysis complete!")

def get_sample_document(doc_type: str) -> str:
    """Get sample legal document text"""
    samples = {
        "Non-Disclosure Agreement": """NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement (the "Agreement") is entered into as of January 15, 2025, by and between TechCorp Inc., a Delaware corporation ("Disclosing Party"), and Innovation Labs LLC, a California limited liability company ("Receiving Party").

WHEREAS, the Disclosing Party possesses certain confidential and proprietary information relating to its software technology; and

WHEREAS, the Receiving Party desires to receive such confidential information for the purpose of evaluating a potential business relationship;

NOW, THEREFORE, in consideration of the mutual covenants and agreements contained herein, the parties agree as follows:

1. CONFIDENTIAL INFORMATION
For purposes of this Agreement, "Confidential Information" shall mean all information disclosed by the Disclosing Party to the Receiving Party, including but not limited to: technical data, trade secrets, know-how, research, product plans, software, source code, customers, financial information, and business strategies.

2. OBLIGATIONS OF RECEIVING PARTY
The Receiving Party shall: (a) hold and maintain the Confidential Information in strict confidence; (b) not disclose the Confidential Information to any third parties without the prior written consent of the Disclosing Party; and (c) use the Confidential Information solely for the purpose of evaluating the potential business relationship between the parties.

3. TERM
This Agreement shall commence on the date first written above and shall continue for a period of two (2) years, unless earlier terminated by either party upon thirty (30) days written notice to the other party.

4. RETURN OF MATERIALS
Upon termination of this Agreement, the Receiving Party shall promptly return to the Disclosing Party all documents, materials, and other tangible items containing or representing Confidential Information.

5. NO LICENSE
Nothing in this Agreement shall be construed as granting any rights to the Receiving Party, by license or otherwise, to any Confidential Information disclosed hereunder, except as expressly provided herein.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.""",

        "Service Agreement": """PROFESSIONAL SERVICES AGREEMENT

This Professional Services Agreement (the "Agreement") is made and entered into as of February 1, 2025, by and between Digital Solutions Inc. ("Service Provider") and ABC Corporation ("Client").

1. SCOPE OF SERVICES
Service Provider agrees to provide the following professional services (the "Services") to Client:
- Web application development and deployment
- Technical consultation and support
- Quality assurance and testing
- Documentation and training

2. DELIVERABLES
Service Provider shall deliver to Client the following deliverables:
(a) Functional web application meeting specifications in Exhibit A
(b) Technical documentation and user manuals
(c) Training for up to 10 Client employees
(d) 30 days of post-launch support

3. COMPENSATION
Client agrees to pay Service Provider a total fee of $75,000 for the Services, payable as follows:
- $25,000 upon execution of this Agreement
- $25,000 upon delivery of functional prototype
- $25,000 upon final delivery and acceptance

4. TERM AND TERMINATION
This Agreement shall commence on February 1, 2025, and continue until completion of all Services, estimated to be June 30, 2025. Either party may terminate this Agreement upon 15 days written notice if the other party materially breaches any provision hereof.

5. INTELLECTUAL PROPERTY
All work product, including source code, documentation, and materials created by Service Provider in performing the Services shall be the sole property of Client upon full payment of all fees due hereunder.

6. WARRANTIES
Service Provider warrants that the Services will be performed in a professional and workmanlike manner consistent with industry standards.

7. LIMITATION OF LIABILITY
In no event shall either party be liable for any indirect, incidental, special, or consequential damages arising out of this Agreement, including but not limited to lost profits or business interruption.""",

        "Employment Contract": """EMPLOYMENT AGREEMENT

This Employment Agreement (the "Agreement") is entered into as of March 1, 2025, by and between GlobalTech Corporation, a Delaware corporation (the "Company"), and Sarah Johnson (the "Employee").

1. POSITION AND DUTIES
The Company hereby employs Employee in the position of Senior Software Engineer. Employee shall report to the Vice President of Engineering and shall perform such duties as are customarily associated with such position.

2. TERM
Employment under this Agreement shall commence on March 1, 2025, and shall continue on an at-will basis until terminated by either party in accordance with Section 7 below.

3. COMPENSATION
The Company shall pay Employee an annual base salary of $120,000, payable in accordance with the Company's standard payroll practices. Employee's salary shall be reviewed annually for potential adjustment.

4. BENEFITS
Employee shall be entitled to participate in all employee benefit plans maintained by the Company, including:
- Health, dental, and vision insurance
- 401(k) retirement plan with company matching
- 15 days of paid vacation per year
- 10 days of paid sick leave per year
- Professional development opportunities

5. WORK SCHEDULE
Employee's normal work schedule shall be Monday through Friday, 9:00 AM to 5:00 PM, with flexibility as approved by the supervisor. Employee may be required to work additional hours as necessary.

6. CONFIDENTIALITY
Employee acknowledges that during employment, Employee will have access to confidential and proprietary information of the Company. Employee agrees to maintain the confidentiality of such information both during and after employment.

7. TERMINATION
Either party may terminate this Agreement at any time, with or without cause, upon two weeks written notice to the other party.

8. GOVERNING LAW
This Agreement shall be governed by and construed in accordance with the laws of the State of California."""
    }
    
    return samples.get(doc_type, "")

if __name__ == "__main__":
    main()