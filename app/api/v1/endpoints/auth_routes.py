from fastapi import APIRouter, Depends, HTTPException
from app.schemas.auth.authSchema import UserRegister, UserLogin, Token, RefreshRequest
from app.services.auth_service import AuthService
from app.core.deps import get_auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=Token, summary="Registrar um novo usuário",
description="""
Cria um novo usuário com os dados fornecidos.

Retorna um token de autenticação após o cadastro.
""",
responses={
    200: {"description": "Usuário registrado com sucesso"},
    400: {"description": "Dados inválidos ou usuário já existe"},
},
status_code=201,
)
async def register(user: UserRegister, service: AuthService = Depends(get_auth_service)):
    db_user = await service.register_user(user)
    token = await service.create_token(db_user.get("id"), db_user.get("nivel"))
    return token

@router.post("/login", response_model=Token, summary="Login de usuário",
description="""
Autentica um usuário com email e senha.

Retorna um token de acesso e refresh token se as credenciais forem válidas.
""",
responses={
    200: {"description": "Login bem-sucedido"},
    401: {"description": "Credenciais inválidas"},
})
async def login(user: UserLogin, service: AuthService = Depends(get_auth_service)):
    db_user = await service.authenticate_user(user)
    token = await service.create_token(db_user.get("id"), db_user.get("nivel"))
    return token

@router.post("/refresh-token", response_model=Token, summary="Renovar o token de acesso",
description="""
Gera um novo token de acesso com base em um refresh token válido.

Use essa rota para manter a sessão do usuário ativa sem exigir novo login.
""",
responses={
    200: {"description": "Token renovado com sucesso"},
    401: {"description": "Token inválido ou expirado"},
})
async def refresh_token(token: RefreshRequest, service: AuthService = Depends(get_auth_service)):
    payload = service.jwt.verify_token(token.refresh_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    user_id = payload.get("sub")
    nivel = payload.get("nivel")
    return await service.create_token(user_id, nivel)