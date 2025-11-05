from django.urls import path
from . import views

urlpatterns = [
    # Primary endpoints
    path("exam/", views.get_exam_flashcard, name="get_exam_flashcard"),
    path("exam/add/", views.add_exam_flashcards, name="add_exam_flashcards"),
    path("test/<str:subject>/", views.get_test_questions),
    path("note/<str:content>/", views.get_note_questions, name='get_note_questions'),
    path("notes/<str:topic_id>/", views.get_notes_by_topic, name='get_notes_by_topic'),

    # Backwards-compatible aliases (some clients expect the 'flashcard(s)' path)
    path("exam/flashcard/", views.get_exam_flashcard, name="get_exam_flashcard_alias"),
    path("exam/flashcards/add/", views.add_exam_flashcards, name="add_exam_flashcards_alias"),
]
