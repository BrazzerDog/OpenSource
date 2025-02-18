from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

def check_admin_access(current_user = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user 