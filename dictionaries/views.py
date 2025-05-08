# views.py
import csv
import io
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

def index_view(request):
    # Renders the base.html, which includes tab1, tab2, tab3
    return render(request, "dictionaries/base.html")


@csrf_exempt
def upload_medication_view(request):
    """
    Replaces the old upload_csv_view. For the first tab "Medications".
    Requires 7 columns (case-insensitive):
      medication_id, pharma_class, generic_name, drug_name_dose,
      drug_concept_id, frequency, percentage
    """
    if request.method != "POST":
        return JsonResponse({"error": "Must be POST"}, status=400)
    if "csvFile" not in request.FILES:
        return JsonResponse({"error": "No file uploaded."}, status=400)

    file = request.FILES["csvFile"]
    try:
        decoded = file.read().decode("utf-8", errors="replace")
        lines = decoded.splitlines()
        if not lines:
            return JsonResponse({"error": "CSV is empty."}, status=400)

        reader = csv.reader(lines, delimiter=",")
        rows = list(reader)
        if not rows:
            return JsonResponse({"error": "CSV is empty."}, status=400)

        header = [h.strip().lower() for h in rows[0]]
        required_cols = [
            "medication_id",
            "pharma_class",
            "generic_name",
            "drug_name_dose",
            "drug_concept_id",
            "frequency",
            "percentage"
        ]
        # Check presence
        for rc in required_cols:
            if rc not in header:
                return JsonResponse({"error": f"Missing required column '{rc}'"}, status=400)

        data_list = []
        for row in rows[1:]:
            row_dict = {}
            for colName in required_cols:
                idx = header.index(colName)
                val = row[idx].strip() if idx < len(row) else ""
                row_dict[colName] = val if val else "null"
            data_list.append(row_dict)

        request.session["csv_data"] = data_list  # same session key as before
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_medication_data_view(request):
    """
    For tab #1 ("Medications"). Returns what's in session["csv_data"].
    """
    if request.method != "GET":
        return JsonResponse({"error": "Must be GET"}, status=400)
    data_list = request.session.get("csv_data", [])
    full_result = []
    for i, row in enumerate(data_list):
        row_obj = {
            "rowIndex": i,
            "medication_id": row["medication_id"],
            "pharma_class": row["pharma_class"],
            "generic_name": row["generic_name"],
            "drug_name_dose": row["drug_name_dose"],
            "drug_concept_id": row["drug_concept_id"],
            "frequency": row["frequency"],
            "percentage": row["percentage"]
        }
        full_result.append(row_obj)
    return JsonResponse({"rows": full_result})


@csrf_exempt
def upload_lab_view(request):
    """
    For tab #2 ("Labs"), left side => user uploads a CSV with columns:
      lab_id + (concept_name, concept_id, frequency, percentage,
                source_value, domain_id, vocabulary_id,
                concept_code, concept_class_id)
    We'll store them in session["lab_data"].
    If the file is missing any of these 10 columns (case-insensitive),
    we return an error.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Must be POST"}, status=400)
    if "csvFile" not in request.FILES:
        return JsonResponse({"error": "No file uploaded."}, status=400)

    file = request.FILES["csvFile"]
    try:
        decoded = file.read().decode("utf-8", errors="replace")
        lines = decoded.splitlines()
        if not lines:
            return JsonResponse({"error": "CSV is empty."}, status=400)

        reader = csv.reader(lines)
        rows = list(reader)
        if not rows:
            return JsonResponse({"error": "CSV is empty."}, status=400)

        header = [h.strip().lower() for h in rows[0]]
        required_cols = [
            "lab_id",
            "concept_name",
            "concept_id",
            "frequency",
            "percentage",
            "source_value",
            "domain_id",
            "vocabulary_id",
            "concept_code",
            "concept_class_id"
        ]
        for rc in required_cols:
            if rc not in header:
                return JsonResponse({"error": f"Missing required column '{rc}'"}, status=400)

        data_list = []
        for row in rows[1:]:
            row_dict = {}
            for colName in required_cols:
                idx = header.index(colName)
                val = row[idx].strip() if idx < len(row) else ""
                row_dict[colName] = val if val else "null"
            data_list.append(row_dict)

        request.session["lab_data"] = data_list
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_lab_data_view(request):
    """Returns session["lab_data"] with rowIndex, or [] if none."""
    if request.method != "GET":
        return JsonResponse({"error": "Must be GET"}, status=400)
    data_list = request.session.get("lab_data", [])
    full_result = []
    for i, row in enumerate(data_list):
        row_obj = {
            "rowIndex": i,
            "lab_id": row["lab_id"],
            "concept_name": row["concept_name"],
            "concept_id": row["concept_id"],
            "frequency": row["frequency"],
            "percentage": row["percentage"],
            "source_value": row["source_value"],
            "domain_id": row["domain_id"],
            "vocabulary_id": row["vocabulary_id"],
            "concept_code": row["concept_code"],
            "concept_class_id": row["concept_class_id"]
        }
        full_result.append(row_obj)
    return JsonResponse({"rows": full_result})


@csrf_exempt
def upload_flowsheet_view(request):
    """
    For tab #2 ("Labs"), right side => user uploads a CSV with columns:
      flowsheet_id + (concept_name, concept_id, frequency, percentage,
                      source_value, domain_id, vocabulary_id,
                      concept_code, concept_class_id)
    We'll store them in session["flowsheet_data"].
    """
    if request.method != "POST":
        return JsonResponse({"error": "Must be POST"}, status=400)
    if "csvFile" not in request.FILES:
        return JsonResponse({"error": "No file uploaded."}, status=400)

    file = request.FILES["csvFile"]
    try:
        decoded = file.read().decode("utf-8", errors="replace")
        lines = decoded.splitlines()
        if not lines:
            return JsonResponse({"error": "CSV is empty."}, status=400)

        reader = csv.reader(lines)
        rows = list(reader)
        if not rows:
            return JsonResponse({"error": "CSV is empty."}, status=400)

        header = [h.strip().lower() for h in rows[0]]
        required_cols = [
            "flowsheet_id",
            "concept_name",
            "concept_id",
            "frequency",
            "percentage",
            "source_value",
            "domain_id",
            "vocabulary_id",
            "concept_code",
            "concept_class_id"
        ]
        for rc in required_cols:
            if rc not in header:
                return JsonResponse({"error": f"Missing required column '{rc}'"}, status=400)

        data_list = []
        for row in rows[1:]:
            row_dict = {}
            for colName in required_cols:
                idx = header.index(colName)
                val = row[idx].strip() if idx < len(row) else ""
                row_dict[colName] = val if val else "null"
            data_list.append(row_dict)

        request.session["flowsheet_data"] = data_list
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_flowsheet_data_view(request):
    """Returns session["flowsheet_data"] with rowIndex, or [] if none."""
    if request.method != "GET":
        return JsonResponse({"error": "Must be GET"}, status=400)
    data_list = request.session.get("flowsheet_data", [])
    full_result = []
    for i, row in enumerate(data_list):
        row_obj = {
            "rowIndex": i,
            "flowsheet_id": row["flowsheet_id"],
            "concept_name": row["concept_name"],
            "concept_id": row["concept_id"],
            "frequency": row["frequency"],
            "percentage": row["percentage"],
            "source_value": row["source_value"],
            "domain_id": row["domain_id"],
            "vocabulary_id": row["vocabulary_id"],
            "concept_code": row["concept_code"],
            "concept_class_id": row["concept_class_id"]
        }
        full_result.append(row_obj)
    return JsonResponse({"rows": full_result})


@csrf_exempt
def upload_procedure_view(request):
    """
    Left-hand CSV in Tab 3.
    Columns required (case-insensitive):
      procedure_id, concept_name, concept_id,
      order_code, order_description,
      frequency, percentage,
      domain_id, vocabulary_id, concept_code, concept_class_id
    """
    if request.method != "POST":
        return JsonResponse({"error": "Must be POST"}, status=400)
    if "csvFile" not in request.FILES:
        return JsonResponse({"error": "No file uploaded."}, status=400)

    file = request.FILES["csvFile"]
    try:
        decoded  = file.read().decode("utf-8", errors="replace")
        rows     = list(csv.reader(decoded.splitlines()))
        if not rows:
            return JsonResponse({"error": "CSV is empty."}, status=400)

        header = [h.strip().lower() for h in rows[0]]
        required = [
            "procedure_id", "concept_name", "concept_id",
            "order_code", "order_description",
            "frequency", "percentage",
            "domain_id", "vocabulary_id", "concept_code", "concept_class_id"
        ]
        for col in required:
            if col not in header:
                return JsonResponse({"error": f"Missing column '{col}'"}, status=400)

        data = []
        for r in rows[1:]:
            row = {}
            for col in required:
                idx = header.index(col)
                row[col] = r[idx].strip() if idx < len(r) and r[idx].strip() else "null"
            data.append(row)

        request.session["procedure_data"] = data
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_procedure_data_view(request):
    """Return session['procedure_data'] as rows with rowIndex (id column is hidden on the client)."""
    if request.method != "GET":
        return JsonResponse({"error": "Must be GET"}, status=400)
    rows = request.session.get("procedure_data", [])
    return JsonResponse({
        "rows": [
            {
                "rowIndex": i,
                "procedure_id"     : r["procedure_id"],        # hidden but needed for capture
                "concept_name"     : r["concept_name"],
                "concept_id"       : r["concept_id"],
                "order_code"       : r["order_code"],
                "order_description": r["order_description"],
                "frequency"        : r["frequency"],
                "percentage"       : r["percentage"],
                "domain_id"        : r["domain_id"],
                "vocabulary_id"    : r["vocabulary_id"],
                "concept_code"     : r["concept_code"],
                "concept_class_id" : r["concept_class_id"],
            }
            for i, r in enumerate(rows)
        ]
    })


@csrf_exempt
def upload_icd10cpt_view(request):
    """
    Right-hand CSV in Tab 3.
    Columns required (case-insensitive):
      procedure_id, concept_name, concept_id,
      code, procedure_code, procedure_description,
      frequency, percentage,
      domain_id, vocabulary_id, concept_code, concept_class_id
    """
    if request.method != "POST":
        return JsonResponse({"error": "Must be POST"}, status=400)
    if "csvFile" not in request.FILES:
        return JsonResponse({"error": "No file uploaded."}, status=400)

    file = request.FILES["csvFile"]
    try:
        decoded  = file.read().decode("utf-8", errors="replace")
        rows     = list(csv.reader(decoded.splitlines()))
        if not rows:
            return JsonResponse({"error": "CSV is empty."}, status=400)

        header = [h.strip().lower() for h in rows[0]]
        required = [
            "procedure_id", "concept_name", "concept_id",
            "code", "procedure_code", "procedure_description",
            "frequency", "percentage",
            "domain_id", "vocabulary_id", "concept_code", "concept_class_id"
        ]
        for col in required:
            if col not in header:
                return JsonResponse({"error": f"Missing column '{col}'"}, status=400)

        data = []
        for r in rows[1:]:
            row = {}
            for col in required:
                idx = header.index(col)
                row[col] = r[idx].strip() if idx < len(r) and r[idx].strip() else "null"
            data.append(row)

        request.session["icd10cpt_data"] = data
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_icd10cpt_data_view(request):
    """Return session['icd10cpt_data'] as rows with rowIndex (id column hidden on the client)."""
    if request.method != "GET":
        return JsonResponse({"error": "Must be GET"}, status=400)
    rows = request.session.get("icd10cpt_data", [])
    return JsonResponse({
        "rows": [
            {
                "rowIndex"         : i,
                "procedure_id"     : r["procedure_id"],        # hidden but needed for capture
                "concept_name"     : r["concept_name"],
                "concept_id"       : r["concept_id"],
                "code"             : r["code"],
                "procedure_code"   : r["procedure_code"],
                "procedure_description": r["procedure_description"],
                "frequency"        : r["frequency"],
                "percentage"       : r["percentage"],
                "domain_id"        : r["domain_id"],
                "vocabulary_id"    : r["vocabulary_id"],
                "concept_code"     : r["concept_code"],
                "concept_class_id" : r["concept_class_id"],
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
def new_session_view(request):
    """Clears session data for everything and returns {ok:true}."""
    if request.method != "POST":
        return JsonResponse({"error": "Must be POST"}, status=400)
    request.session.flush()
    return JsonResponse({"ok": True})
