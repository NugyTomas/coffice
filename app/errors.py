from flask import current_app, jsonify, request
from werkzeug.exceptions import HTTPException, InternalServerError

SOMETHING_WENT_WRONG_ERROR = 'Something went wrong.'
REQUEST_TOO_LARGE_ERROR = "The upload is too large. Please use smaller photos."

FRIENDLY_MESSAGES = {
    413: REQUEST_TOO_LARGE_ERROR,
}


def wants_json():
    return request.path.startswith("/api/")


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_exception(error):
        if not wants_json():
            return error

        message = FRIENDLY_MESSAGES.get(error.code, error.description)

        return jsonify({"success": False, "errors": {"request": message}}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(_error):
        current_app.logger.exception("Unhandled exception")

        if not wants_json():
            return InternalServerError()
        return jsonify({
            "success": False,
            "errors": {"server": SOMETHING_WENT_WRONG_ERROR}
        }), 500
