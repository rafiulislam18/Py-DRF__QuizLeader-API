from rest_framework.throttling import UserRateThrottle


class AdminExemptUserRateThrottle(UserRateThrottle):
    # Global throttle exempting staff & superusers and  from rate limiting.
    def allow_request(self, request, view):
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return True  # Exempt staff & superusers
        return super().allow_request(request, view)
