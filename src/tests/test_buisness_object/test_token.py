import pytest
import datetime

from business_object.token import Token 

@pytest.mark.parametrize(
    "param, erreur_message",
    [
        (
            ("a", "gpVU0x1IzZbP0ScIopiGLlZO5EzhtaAM", datetime.datetime(2025, 10, 10, 14, 30)),
            "L'identifiant de l'utilisateur 'id_user' doit être un entier."
        ),
        (
            (10, 123456, datetime.datetime(2025, 10, 10, 14, 30)),
            "Le jeton d'authentification 'jeton' doit être une chaine de caractères."
        ),
        (
            (1, "gpVU0x1IzZbP0ScIopiGLlZO5EzhtaAM", datetime.date(2025, 10, 10)),
            "La date d'expiration du jeton 'date_expiration' doit être une date au format datetime."
        ),
    ],
)
def test_token_init_echec(param, erreur_message):
    """Test de création d'un token invalide."""
    with pytest.raises(ValueError, match=erreur_message):
        Token(*param)

def test_token_init_valide():
    """Test de création d'un token valide."""
    token = Token(1, "gpVU0x1IzZbP0ScIopiGLlZO5EzhtaAM", datetime.datetime(2025, 10, 10, 14, 30))
    assert token.id_user == 1
    assert token.jeton == "gpVU0x1IzZbP0ScIopiGLlZO5EzhtaAM"
    assert token.date_expiration == datetime.datetime(2025, 10, 10, 14, 30)
