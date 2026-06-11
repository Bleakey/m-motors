"""Protection CSRF via le pattern double-submit cookie.

Un jeton aleatoire est depose dans un cookie ET injecte dans chaque
formulaire (champ cache). A la soumission, on verifie que les deux
correspondent : un site tiers ne peut ni lire le cookie ni deviner le
jeton, il ne peut donc pas forger de requete valide.
"""
import secrets

from fastapi import Request, Form, HTTPException, status

CSRF_COOKIE_NAME = "csrf_token"


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


async def verify_csrf(request: Request, csrf_token: str = Form("")):
    """Dependance a brancher sur les routes POST/PUT/DELETE."""
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME, "")
    if not cookie_token or not secrets.compare_digest(cookie_token, csrf_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Jeton CSRF invalide ou manquant",
        )
