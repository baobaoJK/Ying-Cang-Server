from flask import jsonify

class ResponseResult:
    def __init__(self, data=None, message="", status=200):
        self.data = data
        self.status = status
        self.message = message

    def to_dict(self):
        return {
            "data": self.data,
            "status": self.status,
            "message": self.message
        }

    def to_response(self):
        """返回 Flask Response"""
        return jsonify(self.to_dict()), self.status


class ResponseFactory:
    """工厂类，生成不同类型的返回结果"""

    @staticmethod
    def success(data=None, message="success", status=200):
        return ResponseResult(data, message, status)

    @staticmethod
    def error(message="error", status=400, data=None):
        return ResponseResult(data, message, status)

    @staticmethod
    def warning(message="warning", status=300, data=None):
        return ResponseResult(data, message, status)

    @staticmethod
    def info(message="info", status=200, data=None):
        return ResponseResult(data, message, status)
