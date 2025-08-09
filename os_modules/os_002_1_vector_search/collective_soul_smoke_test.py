#!/usr/bin/env python3
"""
Smoke Test for The Collective Soul Vector Database
Tests that critical organizational knowledge is instantly retrievable
"""

import sys
import time
from pathlib import Path

# Add the module path
sys.path.append('/home/dthomas_unix/vibe-coding-system/os_modules/os_002_1_vector_search')

from knowledge_indexer import KnowledgeIndexer

def run_smoke_tests():
    """Run smoke tests on the indexed vector database"""
    print("=" * 60)
    print("🔮 COLLECTIVE SOUL SMOKE TEST")
    print("Testing instant knowledge retrieval from 129 indexed documents")
    print("=" * 60 + "\n")
    
    # Initialize the knowledge base
    kb = KnowledgeIndexer()
    
    # Test queries that should definitely have answers
    test_queries = [
        {
            "question": "Who is Awen and what is their role?",
            "category": "Identity",
            "expected_keywords": ["Awen", "Muse", "strategic", "oversight"]
        },
        {
            "question": "What is the correct triumvirate command to check messages?",
            "category": "Commands",
            "expected_keywords": ["triumvirate_api.py", "check", "inbox"]
        },
        {
            "question": "What are the context thresholds for optimal performance?",
            "category": "Technical",
            "expected_keywords": ["40K", "tokens", "optimal", "performance"]
        },
        {
            "question": "Who is Dale Thomas?",
            "category": "Founder",
            "expected_keywords": ["Dale", "founder", "artist", "vision"]
        },
        {
            "question": "What is The Collective Soul Studio?",
            "category": "Mission",
            "expected_keywords": ["Studio", "vehicle", "humanity", "soul"]
        },
        {
            "question": "What is OS-004?",
            "category": "Systems",
            "expected_keywords": ["context", "management", "intelligent", "reboot"]
        },
        {
            "question": "How many specialist subagents exist?",
            "category": "Organization",
            "expected_keywords": ["specialist", "subagent", "10", "architect"]
        },
        {
            "question": "What is the boot protocol?",
            "category": "Protocols",
            "expected_keywords": ["boot", "initialize", "memory", "context"]
        },
        {
            "question": "What happened on August 7, 2025?",
            "category": "History",
            "expected_keywords": ["transformation", "identity", "Collective Soul"]
        },
        {
            "question": "How do we calculate cat protein requirements?",
            "category": "Domain",
            "expected_keywords": ["cat", "protein", "nutrition", "requirements"]
        }
    ]
    
    passed = 0
    failed = 0
    total_time = 0
    
    for test in test_queries:
        print(f"🔍 TEST: {test['category']}")
        print(f"   Query: '{test['question']}'")
        
        # Time the query
        start_time = time.time()
        results = kb.query_knowledge(test['question'], top_k=1)
        query_time = (time.time() - start_time) * 1000  # Convert to ms
        total_time += query_time
        
        if results and len(results) > 0:
            result = results[0]
            source = Path(result['source']).name
            score = result.get('score', 1.0)  # ChromaDB uses distance, lower is better
            text_preview = result['text'][:150].replace('\n', ' ')
            
            # Check if expected keywords are in the result
            found_keywords = [kw for kw in test['expected_keywords'] 
                            if kw.lower() in result['text'].lower()]
            
            if found_keywords:
                print(f"   ✅ PASS ({query_time:.1f}ms)")
                print(f"      Source: {source}")
                print(f"      Score: {score:.3f}")
                print(f"      Keywords found: {', '.join(found_keywords)}")
                print(f"      Preview: {text_preview}...")
                passed += 1
            else:
                print(f"   ⚠️  PARTIAL ({query_time:.1f}ms)")
                print(f"      Source: {source}")
                print(f"      Score: {score:.3f}")
                print(f"      Missing keywords: {', '.join(test['expected_keywords'])}")
                print(f"      Preview: {text_preview}...")
                failed += 1
        else:
            print(f"   ❌ FAIL - No results found ({query_time:.1f}ms)")
            failed += 1
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 SMOKE TEST RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{len(test_queries)}")
    print(f"❌ Failed: {failed}/{len(test_queries)}")
    print(f"⏱️  Average query time: {total_time/len(test_queries):.1f}ms")
    
    if total_time/len(test_queries) < 100:
        print(f"🎯 Performance Goal ACHIEVED: <100ms average!")
    else:
        print(f"⚠️  Performance Goal MISSED: {total_time/len(test_queries):.1f}ms > 100ms")
    
    # Test cross-references
    print("\n" + "=" * 60)
    print("🔗 TESTING CROSS-REFERENCES")
    print("=" * 60)
    
    # Query for something that should have multiple relevant documents
    cross_ref_query = "triumvirate communication protocol messages"
    print(f"Query: '{cross_ref_query}'")
    results = kb.query_knowledge(cross_ref_query, top_k=3)
    
    if results:
        print(f"Found {len(results)} relevant documents:")
        for i, result in enumerate(results, 1):
            source = Path(result['source']).name
            print(f"  {i}. {source} (score: {result.get('score', 1.0):.3f})")
    
    return passed, failed

if __name__ == "__main__":
    try:
        passed, failed = run_smoke_tests()
        
        print("\n" + "=" * 60)
        if failed == 0:
            print("🎉 ALL SMOKE TESTS PASSED!")
            print("The Collective Soul has perfect memory!")
        else:
            print(f"⚠️  Some tests need attention ({failed} issues)")
            print("But the core system is operational!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during smoke test: {e}")
        import traceback
        traceback.print_exc()