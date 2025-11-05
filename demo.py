"""
ClauseWise Demo & Test Script
Tests all components and demonstrates functionality
"""

import sys
from pathlib import Path

# Test sample document
SAMPLE_TEXT = """
NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement (the "Agreement") is entered into as of January 15, 2025, 
by and between TechCorp Inc., a Delaware corporation ("Disclosing Party"), and 
Innovation Labs LLC, a California limited liability company ("Receiving Party").

1. CONFIDENTIAL INFORMATION
The Receiving Party shall hold and maintain the Confidential Information in strict 
confidence and shall not disclose such information to any third parties without prior 
written consent.

2. PAYMENT TERMS
In consideration for access to Confidential Information, Receiving Party agrees to pay 
Disclosing Party the sum of $50,000 (fifty thousand dollars) within 30 days of execution.

3. TERM AND TERMINATION
This Agreement shall commence on January 15, 2025, and continue for a period of two (2) years. 
Either party may terminate this Agreement upon thirty (30) days written notice.
"""

def print_separator(title=""):
    """Print formatted separator"""
    if title:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")
    else:
        print(f"\n{'-'*70}\n")

def test_imports():
    """Test if all required modules can be imported"""
    print_separator("Testing Imports")
    
    modules_to_test = [
        ("streamlit", "Streamlit"),
        ("transformers", "HuggingFace Transformers"),
        ("pandas", "Pandas"),
        ("docx", "python-docx"),
        ("PyPDF2", "PyPDF2"),
        ("pdfplumber", "pdfplumber"),
    ]
    
    failed = []
    for module, name in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {name:<30} imported successfully")
        except ImportError as e:
            print(f"✗ {name:<30} import failed: {e}")
            failed.append(name)
    
    if failed:
        print(f"\n⚠️  Failed to import: {', '.join(failed)}")
        print("   Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✓ All required modules imported successfully!")
        return True

def test_document_processor():
    """Test document processor"""
    print_separator("Testing Document Processor")
    
    try:
        from utils.document_processor import DocumentProcessor
        
        # Create test text file
        test_file = Path("/tmp/test_clausewise.txt")
        test_file.write_text(SAMPLE_TEXT)
        
        processor = DocumentProcessor()
        result = processor.process_file(str(test_file))
        
        print(f"✓ Document processed successfully")
        print(f"  - Filename: {result['filename']}")
        print(f"  - File type: {result['file_type']}")
        print(f"  - Word count: {result['metadata']['word_count']}")
        print(f"  - Estimated clauses: {result['metadata']['estimated_clauses']}")
        
        # Clean up
        test_file.unlink()
        
        return True
    except Exception as e:
        print(f"✗ Document processor test failed: {e}")
        return False

def test_ner_extractor():
    """Test NER extractor"""
    print_separator("Testing NER Extractor")
    
    try:
        from utils.ner_extractor import LegalNERExtractor
        
        ner = LegalNERExtractor()
        entities = ner.extract_entities(SAMPLE_TEXT)
        
        print("✓ NER extraction completed")
        print(f"\nExtracted Entities:")
        for entity_type, items in entities.items():
            if items:
                print(f"  - {entity_type.title()}: {len(items)} found")
                if entity_type == 'parties' and items:
                    print(f"    Example: {items[0].get('name', 'N/A')}")
                elif entity_type == 'dates' and items:
                    print(f"    Example: {items[0].get('date', 'N/A')}")
                elif entity_type == 'monetary_values' and items:
                    print(f"    Example: {items[0].get('amount', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"✗ NER extractor test failed: {e}")
        return False

def test_document_classifier():
    """Test document classifier"""
    print_separator("Testing Document Classifier")
    
    try:
        from utils.doc_classifier import DocumentClassifier
        
        classifier = DocumentClassifier()
        result = classifier.classify_document(SAMPLE_TEXT, use_ai=False)
        
        print("✓ Document classification completed")
        print(f"  - Document Type: {result['document_type']}")
        print(f"  - Confidence: {result['confidence']}%")
        print(f"  - Method: {result['method']}")
        
        return True
    except Exception as e:
        print(f"✗ Document classifier test failed: {e}")
        return False

def test_clause_analyzer():
    """Test clause analyzer"""
    print_separator("Testing Clause Analyzer")
    
    try:
        from utils.clause_analyzer import ClauseAnalyzer
        
        analyzer = ClauseAnalyzer()
        clauses = analyzer.extract_clauses(SAMPLE_TEXT)
        
        print(f"✓ Clause extraction completed")
        print(f"  - Total clauses: {len(clauses)}")
        
        if clauses:
            print(f"\nSample Clause:")
            first_clause = clauses[0]
            print(f"  - Type: {first_clause.get('type', 'N/A')}")
            print(f"  - Number: {first_clause.get('number', first_clause.get('title', 'N/A'))}")
            content = first_clause.get('content', '')[:100]
            print(f"  - Preview: {content}...")
        
        return True
    except Exception as e:
        print(f"✗ Clause analyzer test failed: {e}")
        return False

def test_granite_client():
    """Test Granite client initialization"""
    print_separator("Testing Granite Client")
    
    try:
        from utils.granite_client import get_granite_client, GraniteConfig
        
        print("Initializing Granite client...")
        print("(This may take a few minutes on first run)")
        
        config = GraniteConfig(use_watsonx=False)  # Use HuggingFace
        client = get_granite_client(config)
        
        print("✓ Granite client initialized successfully")
        print(f"  - Using: {'IBM watsonx.ai' if config.use_watsonx else 'HuggingFace'}")
        
        # Optional: Test generation
        print("\nTesting text generation...")
        response = input("Do you want to test text generation? (y/n): ").lower()
        
        if response == 'y':
            test_prompt = "Simplify this: The party of the first part hereby agrees."
            print(f"\nTest prompt: {test_prompt}")
            print("Generating response...")
            
            result = client.generate(test_prompt)
            print(f"\nGenerated: {result[:200]}...")
        
        return True
    except Exception as e:
        print(f"✗ Granite client test failed: {e}")
        print("  Note: This is expected if you don't have sufficient RAM or GPU")
        return False

def run_full_demo():
    """Run complete demo with sample document"""
    print_separator("Running Full Demo")
    
    try:
        print("Processing sample NDA document...\n")
        
        # Import all components
        from utils.document_processor import DocumentProcessor
        from utils.ner_extractor import LegalNERExtractor
        from utils.doc_classifier import DocumentClassifier
        from utils.clause_analyzer import ClauseAnalyzer
        
        # 1. Process document
        print("1. Processing document...")
        test_file = Path("/tmp/demo_clausewise.txt")
        test_file.write_text(SAMPLE_TEXT)
        
        processor = DocumentProcessor()
        doc_data = processor.process_file(str(test_file))
        print(f"   ✓ Word count: {doc_data['metadata']['word_count']}")
        
        # 2. Classify
        print("\n2. Classifying document...")
        classifier = DocumentClassifier()
        classification = classifier.classify_document(doc_data['text'], use_ai=False)
        print(f"   ✓ Type: {classification['document_type']}")
        print(f"   ✓ Confidence: {classification['confidence']}%")
        
        # 3. Extract entities
        print("\n3. Extracting entities...")
        ner = LegalNERExtractor()
        entities = ner.extract_entities(doc_data['text'])
        summary = ner.get_summary()
        print(f"   ✓ Parties: {summary['parties']}")
        print(f"   ✓ Dates: {summary['dates']}")
        print(f"   ✓ Money: {summary['monetary_values']}")
        
        # 4. Extract clauses
        print("\n4. Extracting clauses...")
        analyzer = ClauseAnalyzer()
        clauses = analyzer.extract_clauses(doc_data['text'])
        print(f"   ✓ Clauses found: {len(clauses)}")
        
        # Clean up
        test_file.unlink()
        
        print_separator("Demo Complete!")
        print("✓ All components working correctly")
        print("\nYou can now run: streamlit run app.py")
        
        return True
    except Exception as e:
        print(f"✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main demo function"""
    print_separator("ClauseWise Component Test & Demo")
    print("This script will test all components of ClauseWise")
    print("to ensure everything is working correctly.\n")
    
    # Test imports first
    if not test_imports():
        print("\n❌ Import test failed. Please install requirements first.")
        print("   Run: pip install -r requirements.txt")
        sys.exit(1)
    
    print_separator()
    
    # Ask user what to test
    print("What would you like to test?\n")
    print("1. Quick Test (imports + basic functionality)")
    print("2. Full Test (all components)")
    print("3. Full Demo (complete workflow)")
    print("4. Test Individual Components")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        # Quick test
        print_separator("Quick Test")
        success = (
            test_document_processor() and
            test_ner_extractor()
        )
        if success:
            print_separator("Quick Test Passed!")
            print("✓ Basic components are working")
        else:
            print_separator("Quick Test Failed")
            print("✗ Some components need attention")
    
    elif choice == "2":
        # Full test
        print_separator("Full Component Test")
        results = {
            "Document Processor": test_document_processor(),
            "NER Extractor": test_ner_extractor(),
            "Document Classifier": test_document_classifier(),
            "Clause Analyzer": test_clause_analyzer(),
            "Granite Client": test_granite_client()
        }
        
        print_separator("Test Results Summary")
        for component, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {component}")
        
        if all(results.values()):
            print("\n✓ All tests passed!")
        else:
            print("\n⚠️  Some tests failed")
    
    elif choice == "3":
        # Full demo
        run_full_demo()
    
    elif choice == "4":
        # Individual components
        while True:
            print_separator("Individual Component Testing")
            print("1. Document Processor")
            print("2. NER Extractor")
            print("3. Document Classifier")
            print("4. Clause Analyzer")
            print("5. Granite Client")
            print("6. Back to main menu")
            
            sub_choice = input("\nSelect component (1-6): ").strip()
            
            if sub_choice == "1":
                test_document_processor()
            elif sub_choice == "2":
                test_ner_extractor()
            elif sub_choice == "3":
                test_document_classifier()
            elif sub_choice == "4":
                test_clause_analyzer()
            elif sub_choice == "5":
                test_granite_client()
            elif sub_choice == "6":
                break
            
            input("\nPress Enter to continue...")
    
    elif choice == "5":
        print("\nExiting. Thank you!")
        sys.exit(0)
    
    else:
        print("\n✗ Invalid choice")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("Testing complete!")
    print("To start ClauseWise, run: streamlit run app.py")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Testing cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)