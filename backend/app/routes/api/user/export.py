import os

from flask import jsonify, send_file
from flask_security import auth_required, current_user

from app.routes.api.user import user_bp
from app.tasks.export import export_trekking_history, EXPORT_DIR


@user_bp.route("/export", methods=["POST"])
@auth_required()
def trigger_export():
    task = export_trekking_history.delay(current_user.id)
    return jsonify({
        "message": "Export job started. Use the task_id to check progress.",
        "task_id": task.id,
    }), 202


@user_bp.route("/export/<task_id>", methods=["GET"])
@auth_required()
def export_status(task_id):
    result = export_trekking_history.AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": result.status,  # PENDING | STARTED | SUCCESS | FAILURE
    }

    if result.state == "SUCCESS" and result.result:
        response["result"] = result.result
    elif result.state == "FAILURE":
        response["error"] = str(result.result)

    return jsonify(response), 200


@user_bp.route("/export/<task_id>/download", methods=["GET"])
@auth_required()
def download_export(task_id):
    result = export_trekking_history.AsyncResult(task_id)

    if result.state != "SUCCESS" or not result.result:
        return jsonify({"error": "Export is not ready yet or has failed."}), 400

    filename = result.result.get("filename")
    if not filename:
        return jsonify({"error": "No file produced by the export task."}), 400

    filepath = os.path.join(EXPORT_DIR, filename)
    if not os.path.isfile(filepath):
        return jsonify({"error": "Export file not found on server."}), 404

    return send_file(
        filepath,
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename,
    )
