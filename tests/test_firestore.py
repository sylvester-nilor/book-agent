#!/usr/bin/env python3
"""
Test script to check Firestore connectivity and data.
"""

import os
import asyncio
from google.cloud import firestore_v1 as firestore

def test_firestore():
    """Test Firestore connectivity and check for conversation data."""
    project_id = os.getenv("GCP_PROJECT", "robot-rnd-nilor-gcp")
    
    print(f"Testing Firestore for project: {project_id}")
    
    try:
        # Initialize Firestore client
        db = firestore.Client(project=project_id)
        
        # Check if we can access the conversations collection
        collection_name = "book_agent_conversations"
        collection_ref = db.collection(collection_name)
        
        print(f"Checking collection: {collection_name}")
        
        # Try to get documents
        docs = collection_ref.limit(5).stream()
        doc_count = 0
        
        for doc in docs:
            doc_count += 1
            print(f"Document ID: {doc.id}")
            print(f"Data: {doc.to_dict()}")
            print("-" * 50)
        
        if doc_count == 0:
            print("No documents found in the collection.")
            
        print(f"Total documents found: {doc_count}")
        
    except Exception as e:
        print(f"Error accessing Firestore: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_firestore()
