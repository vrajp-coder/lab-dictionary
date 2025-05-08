# urls.py
from django.urls import path
from .views import (
    index_view,
    upload_medication_view,
    get_medication_data_view,
    upload_lab_view,
    get_lab_data_view,
    upload_flowsheet_view,
    get_flowsheet_data_view,
    upload_procedure_view,
    get_procedure_data_view,
    upload_icd10cpt_view,
    get_icd10cpt_data_view,
    generate_csv_view,
    new_session_view
)

urlpatterns = [
    path('', index_view, name='index'),

    # Tab #1 (Medications)
    path('upload_medication/', upload_medication_view, name='upload_medication'),
    path('get_medication_data/', get_medication_data_view, name='get_medication_data'),

    # Tab #2 (Labs)
    path('upload_lab/', upload_lab_view, name='upload_lab'),
    path('get_lab_data/', get_lab_data_view, name='get_lab_data'),
    path('upload_flowsheet/', upload_flowsheet_view, name='upload_flowsheet'),
    path('get_flowsheet_data/', get_flowsheet_data_view, name='get_flowsheet_data'),

    # Tab #3 (Procedures)
    path('upload_procedure/',   upload_procedure_view, name='upload_procedure'),
    path('get_procedure_data/', get_procedure_data_view, name='get_procedure_data'),
    path('upload_icd10cpt/',    upload_icd10cpt_view,  name='upload_icd10cpt'),
    path('get_icd10cpt_data/',  get_icd10cpt_data_view, name='get_icd10cpt_data'),

    # Shared
    path('generate_csv/', generate_csv_view, name='generate_csv'),
    path('new_session/', new_session_view, name='new_session'),
]