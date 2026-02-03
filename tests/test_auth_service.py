import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.services.auth_service import AuthService
from app.schemas.auth.authSchema import UserRegister, UserLogin


@pytest.mark.asyncio
async def test_authenticate_user_success():
    mock_repository = MagicMock()
    mock_repository.find_one_by_field = AsyncMock(return_value={
        "id": "user_1_abc",
        "password": "hashed_password",
        "email": "testuser@example.com",
    })

    mock_auth = MagicMock()
    mock_auth.verificar_senha = MagicMock(return_value=True)
    mock_jwt = MagicMock()
    mock_validated = MagicMock()

    service = AuthService(repository=mock_repository, auth=mock_auth, jwt=mock_jwt, validated=mock_validated)

    login_data = UserLogin(email="testuser@example.com", password="correct_password")


    user = await service.authenticate_user(login_data)

    assert user["id"] == "user_1_abc"
    mock_repository.find_one_by_field.assert_called_once_with("users", "email", "testuser@example.com")
    mock_auth.verificar_senha.assert_called_once_with("correct_password", "hashed_password")


@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials_raises_401():
    mock_repository = MagicMock()
    mock_repository.find_one_by_field = AsyncMock(return_value={
        "id": "user_1_abc",
        "password": "hashed_password",
        "email": "testuser@example.com"
    })
    mock_auth = MagicMock()
    mock_auth.verificar_senha = MagicMock(return_value=False)
    mock_jwt = MagicMock()
    mock_validated = MagicMock()

    service = AuthService(repository=mock_repository, auth=mock_auth, jwt=mock_jwt, validated=mock_validated)
    login_data = UserLogin(email="testuser@example.com", password="wrong_password")

    with pytest.raises(HTTPException) as exc_info:
        await service.authenticate_user(login_data)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Credenciais inválidas"


@pytest.mark.asyncio
async def test_authenticate_user_nonexistent_user_raises_401():
    mock_repository = MagicMock()
    mock_repository.find_one_by_field = AsyncMock(return_value=None)
    mock_auth = MagicMock()
    mock_jwt = MagicMock()
    mock_validated = MagicMock()

    service = AuthService(repository=mock_repository, auth=mock_auth, jwt=mock_jwt, validated=mock_validated)
    login_data = UserLogin(email="nonexistent@example.com", password="any_password")

    with pytest.raises(HTTPException) as exc_info:
        await service.authenticate_user(login_data)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Credenciais inválidas"


@pytest.mark.asyncio
async def test_register_user_email_already_exists_raises_400():
    mock_repository = MagicMock()
    mock_repository.find_one_by_field = AsyncMock(return_value={
        "id": "user_1_abc",
        "email": "existing@example.com"
    })

    mock_auth = MagicMock()
    mock_jwt = MagicMock()
    mock_validated = MagicMock()    
    
    service = AuthService(repository=mock_repository, auth=mock_auth, jwt=mock_jwt, validated=mock_validated)
    new_user_data = UserRegister(
        email="existing@example.com",
        password="ValidPass1!",
        name="Existing User",
        created_at="2023-01-01T00:00:00Z",
        is_active=True
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.register_user(new_user_data)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email já cadastrado"


@pytest.mark.asyncio
async def test_register_user_weak_password_raises_400():
    mock_repository = MagicMock()
    mock_repository.find_one_by_field = AsyncMock(return_value=None)

    mock_auth = MagicMock()
    mock_jwt = MagicMock()
    mock_validated = MagicMock()
    mock_validated.password = MagicMock(return_value=False)

    service = AuthService(repository=mock_repository, auth=mock_auth, jwt=mock_jwt, validated=mock_validated)
    new_user_data = UserRegister(
        email="existing@example.com",
        password="ValidPass",
        name="Existing User",
        created_at="2023-01-01T00:00:00Z",
        is_active=True
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.register_user(new_user_data)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "A senha tem que ter 8 caracteres, pelo menos um caractere maiúsculo, um minúsculo, um número e um especial!"


@pytest.mark.asyncio
async def test_register_user_success():
    mock_repository = MagicMock()
    mock_repository.find_one_by_field = AsyncMock(return_value=None)
    mock_repository.save = AsyncMock(return_value={
        "id": "new_user_123",
        "email": "email1@example.com",
        "password": "ValidPass1!",
        "name": "User",
        "created_at": "2023-01-01T00:00:00Z",
        "is_active": True
    })

    mock_auth = MagicMock()
    mock_auth.hash_senha = MagicMock(return_value="hashed_password")
    mock_jwt = MagicMock()
    mock_validated = MagicMock()
    mock_validated.password = MagicMock(return_value=True)

    service = AuthService(repository=mock_repository, auth=mock_auth, jwt=mock_jwt, validated=mock_validated)
    new_user_data = UserRegister(
        email="email1@example.com",
        password="ValidPass1!",
        name="User",
        created_at="2023-01-01T00:00:00Z"
    )

    user = await service.register_user(new_user_data)
    assert user["id"] == "new_user_123"
    mock_repository.find_one_by_field.assert_called_once_with("users", "email", "email1@example.com")


@pytest.mark.asyncio
async def test_create_token_inactive_user_raises_401():
    mock_repository = MagicMock()
    mock_repository.find_by_id = AsyncMock(return_value={
        "id": "user_1_abc",
        "is_active": False
    })

    mock_auth = MagicMock()
    mock_jwt = MagicMock()
    mock_validated = MagicMock()

    service = AuthService(repository=mock_repository, auth=mock_auth, jwt=mock_jwt, validated=mock_validated)

    with pytest.raises(HTTPException) as exc_info:
        await service.create_token(user_id=1, nivel="common")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Usuário inexistente ou inativo"


@pytest.mark.asyncio
async def test_create_token_success():  
    mock_repository = MagicMock()
    mock_repository.find_by_id = AsyncMock(return_value={
        "id": "user_1_abc",
        "is_active": True
    })

    mock_jwt = MagicMock()
    mock_jwt.create_access_token = MagicMock(return_value="access_token_123")
    mock_jwt.create_refresh_token = MagicMock(return_value="refresh_token_456")

    mock_auth = MagicMock()
    mock_validated = MagicMock()

    service = AuthService(repository=mock_repository, auth=mock_auth, jwt=mock_jwt, validated=mock_validated)

    tokens = await service.create_token(user_id=1, nivel="common")
    assert tokens["access_token"] == "access_token_123"
    assert tokens["refresh_token"] == "refresh_token_456"
    assert tokens["token_type"] == "bearer"
    mock_repository.find_by_id.assert_called_once_with("users", "1")
    mock_jwt.create_access_token.assert_called_once_with(data={"sub": "1", "nivel": "common"})
    mock_jwt.create_refresh_token.assert_called_once_with(data={"sub": "1", "nivel": "common"})