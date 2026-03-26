from rest_framework_simplejwt.tokens import RefreshToken

from apps.auth_module.models import UserSession


class AuthService:
    def issue_tokens(self, user, request) -> dict:
        refresh = RefreshToken.for_user(user)
        UserSession.objects.create(
            user=user,
            refresh_token_jti=str(refresh["jti"]),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
            ip_address=self._get_client_ip(request),
        )
        return {"access": str(refresh.access_token), "refresh": str(refresh)}

    def revoke_session(self, refresh_token: str) -> None:
        token = RefreshToken(refresh_token)
        jti = str(token["jti"])
        UserSession.objects.filter(refresh_token_jti=jti).update(is_active=False)
        token.blacklist()

    def _get_client_ip(self, request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
