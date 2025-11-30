from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from src.config import settings
from src.database.database import get_db
from src.database.models import User

security = HTTPBearer(auto_error=False)

def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if not credentials or not credentials.scheme.lower() == "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다. (Bearer Token 없음)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

def get_current_user_id(
    token: str = Depends(get_token),
    db: Session = Depends(get_db) 
) -> int:
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        login_id = payload.get("loginId")
        
        if login_id is None:
            raise HTTPException(status_code=401, detail="토큰에 로그인 ID 정보가 없습니다.")
        
        user = db.query(User).filter(User.login_id == login_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="해당 로그인 ID를 가진 사용자가 DB에 없습니다.")
            
        return user.id
        
    except JWTError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었거나 유효하지 않습니다.")
    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=500, detail="인증 처리 중 서버 오류가 발생했습니다.")