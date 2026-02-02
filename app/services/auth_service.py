from fastapi import HTTPException
from app.repository.firestore_repository import FirestoreRepository
from app.utils import jwt, auth, validated
from app.schemas.auth.authSchema import UserRegister, UserLogin
from app.models.user import User

class AuthService:
    def __init__(self, repository: FirestoreRepository, jwt: jwt.Jwt, auth: auth.Auth, validated: validated.Validadores):
        self.repository = repository
        self.jwt = jwt
        self.auth = auth
        self.validated = validated
        
    async def register_user(self, new_user_data: UserRegister):
        user_existing = await self.repository.find_one_by_field("users", "email", new_user_data.email)
        if user_existing:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        if not self.validated.password(new_user_data.password):
            raise HTTPException(
                status_code=400, 
                detail="A senha tem que ter 8 caracteres, pelo menos um caractere maiúsculo, um minúsculo, um número e um especial!"
            )
    
        hashed_password = self.auth.hash_senha(new_user_data.password)
        new_user = User(
            email=new_user_data.email,
            password=hashed_password,
            name=new_user_data.name,
            created_at=new_user_data.created_at,
            is_active=new_user_data.is_active
        )
        return await self.repository.save("users", new_user.model_dump())

    
    async def authenticate_user(self, login_data: UserLogin):
       user = await self.repository.find_one_by_field("users", "email", login_data.email)
       if not user or not self.auth.verificar_senha(login_data.password, user["password"]):
           raise HTTPException(status_code=401, detail="Credenciais inválidas")
       print("User authenticated:", user, flush=True)
       return user


    async def create_token(self, user_id: int, nivel: str):
        user = await self.repository.find_by_id("users", str(user_id))
        if not user or not user.get("is_active"):
            raise HTTPException(status_code=401, detail="Usuário inexistente ou inativo")
        
        access_token = self.jwt.create_access_token(data={"sub": str(user_id), "nivel": nivel})
        refresh_token = self.jwt.create_refresh_token(data={"sub": str(user_id), "nivel": nivel})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }