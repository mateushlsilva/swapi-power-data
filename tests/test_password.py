import pytest
from app.utils.validated import Validadores

@pytest.mark.parametrize("password, expected", [
    ("Password123!", True),
    ("pass", False),
    ("PASSWORD123!", False),
    ("P@ssw0rd", True),
    ("P@ss12", False),
])
def test_validated_password(password, expected):
    validador = Validadores()
    assert validador.password(password) == expected