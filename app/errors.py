from flask import current_app, jsonify, request
from werkzeug.exceptions import HTTPException, InternalServerError

REQUEST_TOO_LARGE_ERROR = 'Request is too large.'
SOMETHING_WENT_WRONG_ERROR = 'Something went wrong.'


def wants_json():
    return request.path.startswith("/api/")


def register_error_handlers(app):
    @app.errorhandler(413)
    def request_too_large(error):
        if not wants_json():
            return error
        return jsonify({"success": False, "errors": {"request": REQUEST_TOO_LARGE_ERROR}}), 413

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        if isinstance(error, HTTPException):
            return error

        current_app.logger.exception("Unhandled exception")

        if not wants_json():
            return InternalServerError()
        return jsonify({
            "success": False,
            "errors": {"server": SOMETHING_WENT_WRONG_ERROR}
        }), 500
