from flask import current_app, jsonify, request
from werkzeug.exceptions import HTTPException, InternalServerError

SOMETHING_WENT_WRONG_ERROR = 'Something went wrong.'


def wants_json():
    return request.path.startswith("/api/")


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_exception(error):
        if not wants_json():
            return error

        return jsonify({"success": False, "errors": {"request": error.description}}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(_error):
        current_app.logger.exception("Unhandled exception")

        if not wants_json():
            return InternalServerError()
        return jsonify({
            "success": False,
            "errors": {"server": SOMETHING_WENT_WRONG_ERROR}
        }), 500
