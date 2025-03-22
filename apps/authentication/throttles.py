from rest_framework.throttling import AnonRateThrottle


class RegisterThrottle(AnonRateThrottle):
    # Custom limit for registration
    rate = "10/minute"

class HighLimitAnonRateThrottle(AnonRateThrottle):
    # Custom throttle with high limit (for login, logout, token refresh)
    rate = "20/minute"
