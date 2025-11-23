"""
URL routing for API endpoints
"""

from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('process-document/', views.process_document, name='process_document'),
    path('process-all-documents/', views.process_all_documents, name='process_all_documents'),
    path('semantic-search/', views.semantic_search, name='semantic_search'),
    path('project-tasks/', views.get_project_tasks, name='get_project_tasks'),
    path('cost-items/', views.get_cost_items, name='get_cost_items'),
    path('chroma-stats/', views.get_chroma_stats, name='get_chroma_stats'),
    path('clear-databases/', views.clear_databases, name='clear_databases'),
]

