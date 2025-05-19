# views.py
import csv
import io
import os, glob, pathlib
import json, datetime
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.conf import settings

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

_MED_CACHE,  _MED_MTIME  = None, 0      # drug_exposure_*.csv
_LAB_CACHE,  _LAB_MTIME  = None, 0      # measurement_*.csv
_FLOW_CACHE, _FLOW_MTIME = None, 0      # observation_*.csv
_PROC_CACHE, _PROC_MTIME = None, 0      # procedure_*.csv
_ICD_CACHE,  _ICD_MTIME  = None, 0      # icd10_cpt_*.csv

def index_view(request):
    # Renders the base.html, which includes tab1, tab2, tab3
    return render(request, "dictionaries/base.html")

def _load_med_data():
    """
    Load the newest drug_exposure_*.csv from dictionaries/data/.
    Caches the parsed list until the file timestamp changes.
    """
    global _MED_CACHE, _MED_MTIME

    pattern = BASE_DIR / "dictionaries" / "data" / "drug_exposure_*.csv"
    files = glob.glob(str(pattern))
    if not files:
        return []

    latest = max(files, key=os.path.getmtime)
    mtime  = os.path.getmtime(latest)

    if _MED_CACHE is not None and mtime == _MED_MTIME:
        return _MED_CACHE     # cached copy still fresh

    required = [
        "medication_id", "pharma_class", "generic_name",
        "drug_name_dose", "drug_concept_id", "frequency", "percentage"
    ]

    data = []
    with open(latest, newline="", encoding="utf-8", errors="replace") as fh:
        rdr = csv.DictReader(fh)
        # normalise header names to lower
        field_map = {h.lower(): h for h in rdr.fieldnames}
        for col in required:
            if col not in field_map:
                raise ValueError(f"{latest} missing column '{col}'")
        for row in rdr:
            rec = {col: (row[field_map[col]] or "null").strip() for col in required}
            data.append(rec)

    _MED_CACHE, _MED_MTIME = data, mtime
    return data

@csrf_exempt
def get_medication_data_view(request):
    if request.method != "GET":
        return JsonResponse({"error": "Must be GET"}, status=400)

    data_list = _load_med_data()
    result = [
        {
            "rowIndex"       : i,
            "medication_id"  : r["medication_id"],   # hidden on client
            "pharma_class"   : r["pharma_class"],
            "generic_name"   : r["generic_name"],
            "drug_name_dose" : r["drug_name_dose"],
            "drug_concept_id": r["drug_concept_id"],
            "frequency"      : r["frequency"],
            "percentage"     : r["percentage"],
        }
        for i, r in enumerate(data_list)
    ]
    return JsonResponse({"rows": result})

def _load_lab_data():
    """
    Load newest measurement_*.csv → list[dict].
    """
    global _LAB_CACHE, _LAB_MTIME
    pattern = BASE_DIR / "dictionaries" / "data" / "measurement_*.csv"
    files   = glob.glob(str(pattern))
    if not files: return []

    latest  = max(files, key=os.path.getmtime)
    mtime   = os.path.getmtime(latest)
    if _LAB_CACHE is not None and mtime == _LAB_MTIME:
        return _LAB_CACHE

    required = [
        "measurement_id",    # hidden on UI
        "concept_name",
        "frequency", "percentage",
        "unit_source_value"
    ]
    data = []
    with open(latest, newline="", encoding="utf-8", errors="replace") as fh:
        rdr = csv.DictReader(fh)
        fmap = {h.lower(): h for h in rdr.fieldnames}
        for col in required:
            if col not in fmap:
                raise ValueError(f"{latest} missing column '{col}'")
        for row in rdr:
            rec = {col: (row[fmap[col]] or "null").strip() for col in required}
            data.append(rec)

    _LAB_CACHE, _LAB_MTIME = data, mtime
    return data

@csrf_exempt
def get_lab_data_view(request):
    if request.method != "GET":
        return JsonResponse({"error": "Must be GET"}, status=400)

    rows = _load_lab_data()
    return JsonResponse({
        "rows": [
            {
                "rowIndex"        : i,
                "lab_id"          : r["measurement_id"],      # JS still expects lab_id
                "concept_name"    : r["concept_name"],
                "frequency"       : r["frequency"],
                "percentage"      : r["percentage"],
                "unit_source_value": r["unit_source_value"],
            }
            for i, r in enumerate(rows)
        ]
    })

def _load_flow_data():
    """
    Load newest observation_*.csv → list[dict].
    """
    global _FLOW_CACHE, _FLOW_MTIME
    pattern = BASE_DIR / "dictionaries" / "data" / "observation_*.csv"
    files   = glob.glob(str(pattern))
    if not files: return []

    latest  = max(files, key=os.path.getmtime)
    mtime   = os.path.getmtime(latest)
    if _FLOW_CACHE is not None and mtime == _FLOW_MTIME:
        return _FLOW_CACHE

    required = [
        "observation_id",    # hidden on UI
        "concept_name",
        "frequency", "percentage",
        "value_source_value"
    ]
    data = []
    with open(latest, newline="", encoding="utf-8", errors="replace") as fh:
        rdr = csv.DictReader(fh)
        fmap = {h.lower(): h for h in rdr.fieldnames}
        for col in required:
            if col not in fmap:
                raise ValueError(f"{latest} missing column '{col}'")
        for row in rdr:
            rec = {col: (row[fmap[col]] or "null").strip() for col in required}
            data.append(rec)

    _FLOW_CACHE, _FLOW_MTIME = data, mtime
    return data

@csrf_exempt
def get_flowsheet_data_view(request):
    if request.method != "GET":
        return JsonResponse({"error": "Must be GET"}, status=400)

    rows = _load_flow_data()
    return JsonResponse({
        "rows": [
            {
                "rowIndex"        : i,
                "flowsheet_id"    : r["observation_id"],      # keep same key for JS
                "concept_name"    : r["concept_name"],
                "frequency"       : r["frequency"],
                "percentage"      : r["percentage"],
                "value_source_value": r["value_source_value"],
            }
            for i, r in enumerate(rows)
        ]
    })

def _load_proc_data():
    """Return newest procedure_*.csv as list[dict]."""
    global _PROC_CACHE, _PROC_MTIME
    pattern = BASE_DIR / "dictionaries" / "data" / "procedure_*.csv"
    files   = glob.glob(str(pattern))
    if not files:
        return []
    latest  = max(files, key=os.path.getmtime)
    mtime   = os.path.getmtime(latest)
    if _PROC_CACHE is not None and mtime == _PROC_MTIME:
        return _PROC_CACHE

    required = [
        "procedure_id", "concept_name", "concept_id",
        "order_code", "order_description",
        "frequency", "percentage",
        "domain_id", "vocabulary_id", "concept_code", "concept_class_id"
    ]
    data = []
    with open(latest, newline="", encoding="utf-8", errors="replace") as fh:
        rdr  = csv.DictReader(fh)
        fmap = {h.lower(): h for h in rdr.fieldnames}
        for col in required:
            if col not in fmap:
                raise ValueError(f"{latest} missing column '{col}'")
        for row in rdr:
            rec = {col: (row[fmap[col]] or "null").strip() for col in required}
            data.append(rec)

    _PROC_CACHE, _PROC_MTIME = data, mtime
    return data

@csrf_exempt
def get_procedure_data_view(request):
    if request.method != "GET":
        return JsonResponse({"error": "Must be GET"}, status=400)

    rows = _load_proc_data()
    return JsonResponse({
        "rows": [
            {
                "rowIndex"        : i,
                "procedure_id"    : r["procedure_id"],      # hidden on client
                "concept_name"    : r["concept_name"],
                "concept_id"      : r["concept_id"],
                "order_code"      : r["order_code"],
                "order_description": r["order_description"],
                "frequency"       : r["frequency"],
                "percentage"      : r["percentage"],
                "domain_id"       : r["domain_id"],
                "vocabulary_id"   : r["vocabulary_id"],
                "concept_code"    : r["concept_code"],
                "concept_class_id": r["concept_class_id"],
            }
            for i, r in enumerate(rows)
        ]
    })

def _load_icd_data():
    """Return newest icd10_cpt_*.csv as list[dict]."""
    global _ICD_CACHE, _ICD_MTIME
    pattern = BASE_DIR / "dictionaries" / "data" / "icd10_cpt_*.csv"
    files   = glob.glob(str(pattern))
    if not files:
        return []
    latest  = max(files, key=os.path.getmtime)
    mtime   = os.path.getmtime(latest)
    if _ICD_CACHE is not None and mtime == _ICD_MTIME:
        return _ICD_CACHE

    required = [
        "procedure_id", "concept_name", "concept_id",
        "code", "procedure_code", "procedure_description",
        "frequency", "percentage",
        "domain_id", "vocabulary_id", "concept_code", "concept_class_id"
    ]
    data = []
    with open(latest, newline="", encoding="utf-8", errors="replace") as fh:
        rdr  = csv.DictReader(fh)
        fmap = {h.lower(): h for h in rdr.fieldnames}
        for col in required:
            if col not in fmap:
                raise ValueError(f"{latest} missing column '{col}'")
        for row in rdr:
            rec = {col: (row[fmap[col]] or "null").strip() for col in required}
            data.append(rec)

    _ICD_CACHE, _ICD_MTIME = data, mtime
    return data

@csrf_exempt
def get_icd10cpt_data_view(request):
    if request.method != "GET":
        return JsonResponse({"error": "Must be GET"}, status=400)

    rows = _load_icd_data()
    return JsonResponse({
        "rows": [
            {
                "rowIndex"             : i,
                "procedure_id"         : r["procedure_id"],  # hidden on client
                "concept_name"         : r["concept_name"],
                "concept_id"           : r["concept_id"],
                "code"                 : r["code"],
                "procedure_code"       : r["procedure_code"],
                "procedure_description": r["procedure_description"],
                "frequency"            : r["frequency"],
                "percentage"           : r["percentage"],
                "domain_id"            : r["domain_id"],
                "vocabulary_id"        : r["vocabulary_id"],
                "concept_code"         : r["concept_code"],
                "concept_class_id"     : r["concept_class_id"],
            }
            for i, r in enumerate(rows)
        ]
    })

@csrf_exempt
def generate_csv_view(request):
    """
    Build the CSV **in column-oriented form**.

    ┌────────────┬──────────┬──────────┐
    │  Col A     │  Col B   │  …       │   ← header row (colName values)
    ├────────────┼──────────┼──────────┤
    │ id_A_1     │ id_B_1   │ …        │
    │ id_A_2     │ id_B_2   │ …        │
    │ …          │ …        │ …        │
    └────────────┴──────────┴──────────┘

    Body JSON
    ----------
    {
      "columns": [
        { "colName": "...", "medicationIds" | "labIds" | "flowsheetIds": [...] },
        …
      ],
      "fileType": "med" | "lab" | "flowsheet",   // optional (defaults to "med")
      "fileName": "example.csv"                  // optional
    }
    """
    if request.method != "POST":
        return JsonResponse({"error": "Must be POST"}, status=400)

    import json
    body      = json.loads(request.body or "{}")
    columns   = body.get("columns", [])
    file_type = body.get("fileType", "med").lower()
    file_name = body.get("fileName", "output.csv")
    if not file_name.lower().endswith(".csv"):
        file_name += ".csv"

    # Helper: pick the correct ID list from each column object
    def get_ids(col_obj):
        if file_type == "lab":
            return col_obj.get("labIds", [])
        if file_type == "flowsheet":
            return col_obj.get("flowsheetIds", [])
        if file_type == "procedure":
            return col_obj.get("procedureIds", [])
        if file_type == "icd10cpt":
            return col_obj.get("icd10cptIds", [])
        return col_obj.get("medicationIds", [])      # default – medications

    # Assemble header and each column’s ID list
    headers   = [col.get("colName", "") for col in columns]
    id_lists  = [get_ids(col)            for col in columns]
    max_len   = max((len(lst) for lst in id_lists), default=0)

    # Write to an in-memory CSV buffer
    csv_buffer = io.StringIO()
    writer     = csv.writer(csv_buffer)

    writer.writerow(headers)                       # header row
    for r in range(max_len):                       # data rows
        row = [
            ids[r] if r < len(ids) else ""         # blank if this column ran short
            for ids in id_lists
        ]
        writer.writerow(row)

    response = HttpResponse(
        csv_buffer.getvalue(),
        content_type="text/csv"
    )
    response["Content-Disposition"] = f'attachment; filename="{file_name}"'
    return response

@csrf_exempt
def submit_data_view(request):
    """
    Expects JSON:
    {
      firstName: "...",
      lastName : "...",
      email    : "...",
      irb      : "...",
      previews : {           # optional - any combo present
        tab1: [ {colName, medicationIds:[...] }, ... ],
        tab2_lab : [ {colName, labIds:[...] }, ... ],
        tab2_flow: [ {colName, flowsheetIds:[...] }, ... ],
        tab3_proc: [ {colName, procedureIds:[...] }, ... ],
        tab3_icd : [ {colName, icd10cptIds:[...] }, ... ]
      }
    }
    Generates up to 5 CSVs via generate_csv_view() helper and emails them.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Must be POST"}, status=400)

    payload = json.loads(request.body or "{}")
    first = payload.get("firstName", "").strip()
    last  = payload.get("lastName", "").strip()
    user_email = payload.get("email", "").strip()
    irb  = payload.get("irb", "").strip()
    previews = payload.get("previews", {})

    if not (first and last and user_email and irb):
        return JsonResponse({"error": "Missing required fields"}, status=400)

    # --- Helper to call generate_csv_view internally -------------------------
    def build_csv(preview_list, ftype, prefix):
        """
        Return (bytes, filename) or None.
        """
        if not preview_list:
            return None
        body = {
            "columns": preview_list,
            "fileType": ftype,
            "fileName": f"{prefix}_{datetime.datetime.now():%Y%m%d_%H%M%S}.csv"
        }
        fake_req = HttpRequest()
        fake_req.method = "POST"
        fake_req._body  = json.dumps(body).encode()
        # minimal META so generate_csv_view doesn’t crash
        fake_req.META = {}
        resp = generate_csv_view(fake_req)
        return resp.content, body["fileName"]

    attachments = []
    mapping = [
        ("tab1",       "med",       "MED"),
        ("tab2_lab",   "lab",       "LAB"),
        ("tab2_flow",  "flowsheet", "FLOWSHEET"),
        ("tab3_proc",  "procedure", "PROCEDURE"),
        ("tab3_icd",   "icd10cpt",  "PROCEDURE_CPT"),
    ]
    for key, ftype, prefix in mapping:
        csv_bytes = build_csv(previews.get(key, []), ftype, prefix)
        if csv_bytes:
            attachments.append(csv_bytes)

    # -------------------- email to user -------------------------------------
    subj_user = "Confirmation: Data Request Received - CTRA Lab"
    msg_user  = (
        f"Dear {first} {last},\n\n"
        f"Thank you for submitting a data request to the CTRA Lab!\n"
        f"We have received your request with the following IRB number: {irb}.\n"
        f"Our team will reach out with a follow-up as soon as possible.\n\n"
        "Please do not reply - this inbox is not monitored regularly.\n"
        "If you have questions, contact bashar.kadhim@yale.edu.\n\n"
        "Sincerely,\nThe CTRA Team"
    )
    EmailMessage(
        subject=subj_user,
        body=msg_user,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user_email]
    ).send(fail_silently=False)

    # -------------------- email to team -------------------------------------
    subj_team = f"Data Request from IRB #: {irb}"
    msg_team  = (
        "A data request has been made by the user below:\n\n"
        f"Name : {first} {last}\n"
        f"Email: {user_email}\n"
        f"IRB #: {irb}\n"
    )
    email_team = EmailMessage(
        subject=subj_team,
        body=msg_team,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[
            "vraj.pandya@yale.edu",
            "bashar.kadhim@yale.edu"
            ]
    )
    for content, fname in attachments:
        email_team.attach(fname, content, "text/csv")
    email_team.send(fail_silently=False)

    return JsonResponse({"ok": True})

@csrf_exempt
def new_session_view(request):
    """Clears session data for everything and returns {ok:true}."""
    if request.method != "POST":
        return JsonResponse({"error": "Must be POST"}, status=400)
    request.session.flush()
    return JsonResponse({"ok": True})
