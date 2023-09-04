from flask import render_template, Blueprint, request, redirect, flash, url_for
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json
from bson import json_util
from collections import OrderedDict
from hadrumet_platform import get_database
from pprint import pprint

bp_admin = Blueprint('admin', __name__)

# Database and Google API Configurations
db = get_database()
db_lgfs = db.lgf
db_lgf_leads = db.lgf_lead
SERVICE_ACCOUNT_FILE = 'google-api-keys.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)


@bp_admin.route('/admin/submit_lgf', methods = ["GET", "POST"])
def submit_lgf():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        google_form_url = request.form.get("google_form_url")
        responses_url = request.form.get("responses_url")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        field_id = request.form.get("field_id")
        range = request.form.get("range")
        visible_questions = request.form.get("visible_questions")

        if name and responses_url and range and field_id and visible_questions:
            if _submit_lgf(lgf_description=description, lgf_name=name, id_field=field_id, start_date=start_date, end_date=end_date, range=range, responses_url=responses_url, google_form_url=google_form_url, visible_questions=visible_questions):
                flash("LGF Added Successfully!", "success")
            else:
                flash("LGF already exists.", "danger")
            return redirect(url_for("admin.submit_lgf"))

    return render_template("admin_submit_lgf.html", title="LGF Submission")

@bp_admin.route('/admin/add_lgf_leads', methods = ["GET", "POST"])
def add_lgf_leads():
    if request.method == "POST":
        name = request.form.get("name")
        responses_url = request.form.get("responses_url")
        range = request.form.get("range")
        start_row = int(request.form.get("start_row"))

        if name and responses_url and range and start_row:
            update_leads_starting_from_row_n(responses_url, range, name, start_row)
            flash("LGF Leads Updated Successfully!", "success")
            return redirect(url_for("admin.add_lgf_leads"))

    res = db_lgfs.find({})
    options = list(element["name"] for element in res)

    return render_template("admin_add_lgf_leads.html", title="LGF Leads Update", options=options)

@bp_admin.route('/admin/update_lgf', methods = ["GET", "POST"])
def update_lgf():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        google_form_url = request.form.get("google_form_url")
        responses_url = request.form.get("responses_url")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        field_id = request.form.get("field_id")
        range = request.form.get("range")
        visible_questions = request.form.get("visible_questions")

        if name and responses_url and range and field_id and visible_questions:
            _update_lgf(lgf_description=description, lgf_name=name, id_field=field_id, start_date=start_date, end_date=end_date, range=range, responses_url=responses_url, google_form_url=google_form_url, visible_questions=visible_questions)
            flash("LGF Updated Successfully!", "success")
            return redirect(url_for("admin.update_lgf"))

    res = db_lgfs.find({})
    options = list(element["name"] for element in res)

    return render_template("admin_update_lgf.html", title="LGF Update", options=options)

@bp_admin.route('/admin/delete_lgf', methods = ["GET", "POST"])
def delete_lgf():
    if request.method == "POST":
        name = request.form.get("name")
        drop_leads = request.form.get("drop_leads")

        if name:
            result = db_lgfs.delete_one({"name": name})
            if result.deleted_count == 1:
                flash("LGF Deleted Successfully!", "success")
            else:
                flash("Couldn't delete the LGF.", "danger")

            if drop_leads == "on":
                result = db_lgf_leads.delete_many({"lgf_name": name})
                if result.deleted_count:
                    flash("LGF Leads Deleted Successfully!", "success")
                else:
                    flash("Couldn't delete the LGF Leads.", "danger")
            else:
                flash("LGF Leads not deleted.", "danger")
            return redirect(url_for("admin.delete_lgf"))

    res = db_lgfs.find({})
    options = list(element["name"] for element in res)

    return render_template("admin_delete_lgf.html", title="LGF Delete", options=options)

@bp_admin.route('/config/lgf_preview_data')
def lgf_preview_data():
    responses_url = request.args.get("responses_url")
    range = request.args.get("range")
    SPREADSHEET_ID = responses_url.split("https://docs.google.com/spreadsheets/d/")[1].split("/")[0]
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=range).execute()

    return json.dumps({"result": result["values"]})

@bp_admin.route('/config/get_lgf_details')
def get_lgf_details():
    name = request.args.get("name")
    lgf = db_lgfs.find_one({"name": name})
    return json.loads(json_util.dumps(lgf))

def _submit_leads(lgf_name, questions, answers):
    lgf_leads = []
    for answer in answers:
        _lgf_lead = OrderedDict({"lgf_name": lgf_name})
        lgf_questions = {}
        for q, a in zip(questions, answer):
            lgf_questions[q] = a
        _lgf_lead.update({"lgf_questions": lgf_questions})
        _lgf_lead.update({"dispatched_to": ""})
        _lgf_lead.update({"dispatched_at": ""})
        _lgf_lead.update({"dispatched_by": ""})
        _lgf_lead.update({"current_manager": ""})
        _lgf_lead.update({"current_department": ""})
        _lgf_lead.update({"current_status": ""})
        _lgf_lead.update({"crm": []})
        _lgf_lead.update({"expa_id": ""})
        _lgf_lead.update({"customer_flow": []})
        _lgf_lead.update({"transitioned_state": False})

        lgf_leads.append(_lgf_lead)

    _leads = []
    _leads.append(lgf_leads)
    pprint(_leads)
    _leads = json.loads(json.dumps(_leads))[0]

    return _leads

def _submit_lgf(range:str, lgf_name:str, lgf_description:str, google_form_url:str, visible_questions:str,
               responses_url:str, id_field:str, start_date=None, end_date=None):

    SPREADSHEET_ID = responses_url.split("https://docs.google.com/spreadsheets/d/")[1].split("/")[0]

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=range).execute()

    questions = result['values'][0]
    answers = result['values'][1:]

    lgf = {"name": lgf_name, "description": lgf_description, "google_form_url": google_form_url, "responses_url": responses_url, "id_field": id_field, "last_range_inserted": range, "start_date": start_date, "end_date": end_date, "visible_questions":visible_questions}

    filter_query = {"name": lgf_name}
    update_query = {"$set": lgf}
    db_lgfs.update_one(filter_query, update_query, upsert=True)

    _leads = _submit_leads(lgf_name, questions, answers)

    if not db_lgf_leads.find_one({"lgf_name": lgf_name}):
        inset_leads(_leads)
        return True
    else:
        return False

def _update_lgf(range:str, lgf_name:str, lgf_description:str, google_form_url:str, visible_questions:str,
               responses_url:str, id_field:str, start_date=None, end_date=None):

    lgf = {"name": lgf_name, "description": lgf_description, "google_form_url": google_form_url, "responses_url": responses_url, "id_field": id_field, "last_range_inserted": range, "start_date": start_date, "end_date": end_date, "visible_questions": visible_questions}

    filter_query = {"name": lgf_name}
    update_query = {"$set": lgf}

    db_lgfs.update_one(filter_query, update_query, upsert=True)

def update_leads_starting_from_row_n(responses_url: str, range:str, lgf_name:str, start_row: int):
    SPREADSHEET_ID = responses_url.split("https://docs.google.com/spreadsheets/d/")[1].split("/")[0]

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=range).execute()

    questions = result['values'][0]
    answers = result['values'][start_row-1:]

    _leads = _submit_leads(lgf_name, questions, answers)

    lgf = {"last_range_inserted": range}

    filter_query = {"name": lgf_name}
    update_query = {"$set": lgf}
    db_lgfs.update_one(filter_query, update_query, upsert=True)

    inset_leads(_leads)

def inset_leads(leads):
    db_lgf_leads.insert_many(leads)
