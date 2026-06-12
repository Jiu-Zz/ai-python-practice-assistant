class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "资源不存在") -> None:
        super().__init__(message, status_code=404)


class AuthError(AppError):
    def __init__(self, message: str = "认证失败") -> None:
        super().__init__(message, status_code=401)


class PermissionDeniedError(AppError):
    def __init__(self, message: str = "无权限执行该操作") -> None:
        super().__init__(message, status_code=403)
