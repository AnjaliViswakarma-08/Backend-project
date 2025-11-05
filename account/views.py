# account/views.py
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from account.mongo import collections, exam_collection, note_collection, notes_collection
from bson.objectid import ObjectId
import json
from account.utils.summarization_utils import summarize_text
from account.utils.pointwise_utils import convert_to_pointwise

# Helper to convert ObjectId to string
def _serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# Get all exam flashcards
def get_exam_flashcard(request):
    docs = list(exam_collection.find({}))
    docs = [_serialize_doc(d) for d in docs]
    return JsonResponse(docs, safe=False)


# Backwards-compatible alias: some code expects the plural name
def get_exam_flashcards(request):
    #print("Request hit!", request.method, request.path)
    return get_exam_flashcard(request)

# Add a new flashcard
def add_exam_flashcards(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")
    payload = json.loads(request.body)
    doc = {"question": payload.get("question"), "answer": payload.get("answer")}
    res = exam_collection.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    return JsonResponse(doc, status=201)

# ------------------- New test routes -------------------

def get_test_questions(request, subject):
    if subject not in collections:
        return JsonResponse({"error": "Invalid subject name"}, status=400)
    
    col = collections[subject]
    docs = list(col.find({}))
    docs = [_serialize_doc(d) for d in docs]
    return JsonResponse(docs, safe=False)

#------------------- New note routes -------------------

def get_note_questions(request, content):
    """
    Get notes with summarization and pointwise conversion.
    Endpoint: /api/note/<content>/
    Example: /api/note/notedsa/
    """
    if content not in note_collection:
        return JsonResponse({"error": "Invalid subject name"}, status=400)
    
    col = note_collection[content]
    docs = list(col.find({}))
    
    if not docs:
        return JsonResponse({
            "success": True,
            "subject": content,
            "notes": [],
            "summary": "No notes found for summarization.",
            "pointwise": [],
            "total_notes": 0
        })
    
    # Serialize documents
    docs = [_serialize_doc(d) for d in docs]
    
    # Combine all text from notes for processing
    all_text = " ".join([
        doc.get("notes", "") or doc.get("content", "") or doc.get("text", "") 
        for doc in docs 
        if doc.get("notes") or doc.get("content") or doc.get("text")
    ])
    
    # Generate summary and pointwise breakdown
    if all_text.strip():
        summary = summarize_text(all_text)
        pointwise = convert_to_pointwise(summary)
    else:
        summary = "No text content found in notes."
        pointwise = []
    
    # Return complete response with notes, summary, and pointwise
    return JsonResponse({
        "success": True,
        "subject": content,
        "notes": docs,
        "summary": summary,
        "pointwise": pointwise,
        "total_notes": len(docs)
    })



def get_notes_by_topic(request, topic_id):
    """
    Fetch notes for a given topic_id from dynamic MongoDB collections.
    Endpoint: /api/notes/<topic_id>/
    Topic mapping: 1->noteos, 2->notecn, 3->notedsa, 4->notetoc, 5->notecoa
    Returns notes from the appropriate collection.
    """
    # Map topic_id to collection name
    topic_mapping = {
        "1": "noteos",
        "2": "notecn",
        "3": "notedsa",
        "4": "notetoc",
        "5": "notecoa"
    }
    
    # Validate topic_id
    if topic_id not in topic_mapping:
        return JsonResponse({
            "success": False,
            "error": "Invalid topic_id",
            "valid_topics": list(topic_mapping.keys())
        }, status=400)
    
    try:
        # Get the collection name from mapping
        collection_name = topic_mapping[topic_id]
        collection = note_collection.get(collection_name)
        
        if collection is None:
            return JsonResponse({
                "success": False,
                "error": f"Collection {collection_name} not found"
            }, status=500)
        
        # Fetch all documents from the collection
        docs = list(collection.find({}))
        
        # Extract and flatten notes data
        notes_list = []
        for doc in docs:
            # The structure is: {_id: ..., '0': {content: '...'}, '1': {...}, ...}
            # We need to extract the content from nested objects
            for key in doc.keys():
                if key != '_id':
                    note_data = doc[key]
                    if isinstance(note_data, dict) and 'content' in note_data:
                        notes_list.append({
                            "content": note_data['content']
                        })
                    elif isinstance(note_data, dict):
                        # If it's a dict but no 'content' key, include as is
                        notes_list.append(note_data)
                    elif isinstance(note_data, str):
                        # If it's a string, wrap it
                        notes_list.append({"content": note_data})
        
        return JsonResponse({
            "success": True,
            "topic_id": topic_id,
            "collection": collection_name,
            "notes": notes_list,
            "count": len(notes_list)
        })
    
    except Exception as e:
        import traceback
        return JsonResponse({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "topic_id": topic_id
        }, status=500)


