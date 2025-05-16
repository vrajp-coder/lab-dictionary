# urls.py
from django.urls import path
from .views import (
    index_view,
    get_medication_data_view,
    get_lab_data_view,
    get_flowsheet_data_view,
    get_procedure_data_view,
    get_icd10cpt_data_view,
    submit_data_view,
    generate_csv_view,
    new_session_view
)

urlpatterns = [
    path('', index_view, name='index'),

    # Tab #1 (Medications)
    path('get_medication_data/', get_medication_data_view, name='get_medication_data'),

    # Tab #2 (Labs)
    path('get_lab_data/', get_lab_data_view, name='get_lab_data'),
    path('get_flowsheet_data/', get_flowsheet_data_view, name='get_flowsheet_data'),

    # Tab #3 (Procedures)
    path('get_procedure_data/', get_procedure_data_view, name='get_procedure_data'),
    path('get_icd10cpt_data/',  get_icd10cpt_data_view, name='get_icd10cpt_data'),

    # Tab #4 (Data Submission)
    path("submit_data/", submit_data_view, name="submit_data"),

    # Shared
    path('generate_csv/', generate_csv_view, name='generate_csv'),
    path('new_session/', new_session_view, name='new_session'),
]