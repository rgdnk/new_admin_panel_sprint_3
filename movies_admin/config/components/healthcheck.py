# Third Party
from health_check.backends import BaseHealthCheckBackend


class MyHealthCheckBackend(BaseHealthCheckBackend):

    critical_service = True

    def check_status(self):
        # The test code goes here.
        # You can use `self.add_error` or
        # raise a `HealthCheckException`,
        # similar to Django's form validation.
        pass

    def identifier(self):
        return self.__class__.__name__
