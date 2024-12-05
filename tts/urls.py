from django.urls import path
from . import views

urlpatterns = [
    path('', views.tts_home, name='tts_home'),  # Homepage
    path('process-file/', views.process_file, name='process_file'),  # File processing
    path('process-text/', views.process_text, name='process_text'),  # Text processing
    path('save-user-details/', views.save_user_details, name='save_user_details'),  # User details submission
    path('get-visitor-count/', views.get_visitor_count, name='get_visitor_count'),  # Visitor count
]
