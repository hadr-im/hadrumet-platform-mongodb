from flask import render_template, Blueprint, request, flash, redirect, url_for
from hadrumet_platform import get_database
from bson import ObjectId  # Import the ObjectId class
from datetime import datetime  # Import datetime for date handling

bp_leads = Blueprint('leads', __name__)
db = get_database()


@bp_leads.route("/lgf", methods=['GET', 'POST'])
def all_lgf():
    all_lgfs = list(db['lgf'].find())
    return render_template("lgf.html", title="LGF", lgfs=all_lgfs)



@bp_leads.route("/lgf/<string:lgf_id>/", methods=['GET', 'POST'])
def all_leads(lgf_id):
    if request.method == "POST":
        selected_ids = request.form.getlist('selected')  # Get a list of selected document IDs
        department = request.form.get('department')

        # Assuming your collection is named 'lgf_lead'

        collection = db['lgf_lead']
        try:
            for document_id in selected_ids:
                try:
                    document_id = ObjectId(document_id)
                    # Update fields in the document using the update_one method
                    collection.update_one(
                        {'_id': document_id},
                        {
                            "$set": {
                                'dispatched_to': department,  # Update dispatched_to field
                                'dispatched_at': datetime.now(),  # Update dispatched_at with the current date
                                # Assuming you have a way to get the logged-in member's name, update dispatched_by accordingly
                                'dispatched_by': 'Logged-In Member Name',
                                'current_status': 'Stranger'  # Update current_status field
                            }
                        }
                    )
                except Exception as e:
                    print(f"Error updating document: {str(e)}")
                    flash(f"Error updating document: {str(e)}", "danger")
            else:
                flash("Lead(s) dispatched successfully!", "success")
        except Exception as e:
            print(f"Error dispatching leads: {str(e)}")
            flash(f"Error dispatching leads: {str(e)}", "danger")

        # Redirect to the same page after processing the form
        return redirect(url_for('leads.all_leads', lgf_id=lgf_id))

    elif request.method == 'GET':
        try:
            lgf_name = db['lgf'].find_one({'_id': ObjectId(lgf_id)})['name']  # Get the name of the LGF
            leads = db['lgf_lead']
            undispatched_leads = list(leads.find({"dispatched_to": "", "lgf_name": lgf_name}))  #  Filter data by dispatched_to field being empty
            dispatched_leads = list(leads.find({"dispatched_to": {"$ne": ""}, "lgf_name": lgf_name}))  # Filter data by dispatched_to field not being empty
            unmanaged_leads = list(leads.find({"current_manager": "", "lgf_name": lgf_name, "dispatched_to": {"$ne": ""}}))  # Filter data by current_manager field being empty

            print(len(dispatched_leads))
            return render_template("leads.html", title="All Leads", undispatched_leads=undispatched_leads, unmanaged_leads=unmanaged_leads, dispatched_leads=dispatched_leads,  lgf_id=lgf_id)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            flash(f"An error occurred: {str(e)}", "danger")
            # Redirect to the same page after processing the form
            return redirect(url_for('leads.all_leads', lgf_id=lgf_id))


@bp_leads.route("/leads/<string:id>", methods=['GET', 'POST'])
def specific_lead(id):
    try:
        specific_lead = db['lgf_lead']
        # Assuming each document has a unique user ID field
        document = specific_lead.find_one({'_id': ObjectId(id)})
        print(document)
        if document:
            return render_template('leads.html', title="Specific Lead", data=[document])  # Wrap the document in a list
        else:
            return "User not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"


@bp_leads.route("/<string:id>/leads", methods=['GET', 'POST'])
def department_lead(id):
    departments = [
        'ogtit',
        'ogttmba',
        'ogv'
    ]
    department_leads = db['lgf_lead']
    if request.method == 'GET':
        members = list(db['member'].find({"department": id}))
        data = list(department_leads.find({"dispatched_to": id, "current_manager": ""}))  # Filter data by dispatched_to
        if id not in departments:
            return "Department not found."
        elif not data:
            return "No data found."
        elif id == 'ogtit':
            return render_template("ogx.html", title="OGT IT&ENG Leads", data=data, members=members, id=id)
        elif id == 'ogttmba':
            return render_template("ogx.html", title="OGT TMBA Leads", data=data, members=members, id=id)
        elif id == 'ogv':
            return render_template("ogx.html", title="OGV Leads", data=data, members=members, id=id)
    if request.method == 'POST':
        selected_ids = request.form.getlist('selected')
        manager_name = request.form.get('manager_name')
        collection = db['lgf_lead']
        try:
            for document_id in selected_ids:
                try:
                    document_id = ObjectId(document_id)
                    # Update fields in the document using the update_one method
                    collection.update_one(
                        {'_id': document_id},
                        {
                            "$set": {
                                'dispatched_by': 'Logged-In Member Name',
                                'current_manager': manager_name  # Update current_status field
                            }
                        }
                    )
                    members = list(db['member'].find({"department": id}))
                    data = list(department_leads.find({"dispatched_to": id, "current_manager": ""}))  # Filter data by dispatched_to
                    if not data:
                        return "No data found."
                    elif id == 'ogtit':
                        return render_template("ogx.html", title="OGT IT&ENG Leads", data=data, members=members, id=id)
                    elif id == 'ogttmba':
                        return render_template("ogx.html", title="OGT TMBA Leads", data=data, members=members, id=id)
                    elif id == 'ogv':
                        return render_template("ogx.html", title="OGV Leads", data=data, members=members, id=id)
                except Exception as e:
                    print(f"Error updating document: {str(e)}")
                    flash(f"Error updating document: {str(e)}", "danger")
            else:
                flash("Manager assigned successfully!", "success")
        except Exception as e:
            print(f"Error dispatching leads: {str(e)}")
            flash(f"Error dispatching leads: {str(e)}", "danger")

        return redirect(url_for('leads.department_lead', id=id))

    