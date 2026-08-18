from django.contrib import admin
from django.urls import path
from documents.views import (
    DocumentListCreateView,
    QAHistoryListView,
    ask_question,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/documents/', DocumentListCreateView.as_view()),
    path('api/ask/', ask_question),
    path('api/history/', QAHistoryListView.as_view()),
]