
from app.utils.security import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM
import pytest
from datetime import timedelta
from jose import jwt, JWTError
from datetime import datetime, timedelta
import time 


def test_hash_password_creates_valid_hash():
    """Prueba que hash_password genera un hash y verify_password lo valida."""
    password = "mypassword123"
    hashed = hash_password(password)

    # Comprobamos que el hash no es la contraseña original
    assert password != hashed
    # Comprobamos que verify_password funciona con la contraseña correcta
    assert verify_password(password, hashed) is True

def test_verify_password_fails_with_wrong_password():
    """Prueba que verify_password devuelve False para una contraseña incorrecta."""
    password = "mypassword123"
    wrong_password = "wrongpassword"
    hashed = hash_password(password)

    # Comprobamos que verify_password falla con la contraseña incorrecta
    assert verify_password(wrong_password, hashed) is False

def test_verify_password_fails_with_different_hash():
    """Prueba que verify_password falla si el hash es diferente."""
    password = "mypassword123"
    hashed_correct = hash_password(password)
    # Simulamos un hash diferente (podría ser el hash de otra contraseña)
    hashed_incorrect = hash_password("anotherpassword")

    assert verify_password(password, hashed_incorrect) is False

def test_create_access_token_creates_valid_jwt():
    """Prueba que se crea un token JWT y contiene los datos esperados."""
    user_data = {"sub": "test@example.com", "user_id": "123", "company_id": "abc"}
    token = create_access_token(data=user_data)

    assert isinstance(token, str) # Debe ser un string

    # Decodificamos el token para verificar su contenido
    # Usamos las mismas claves y algoritmos que en la creación
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert payload["sub"] == user_data["sub"]
    assert payload["user_id"] == user_data["user_id"]
    assert payload["company_id"] == user_data["company_id"]
    assert "exp" in payload # Debe tener una fecha de expiración

def test_create_access_token_default_expiration():
    """Prueba que la expiración por defecto es aproximadamente 1 hora."""
    user_data = {"sub": "test@example.com"}
    token = create_access_token(data=user_data)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    expiration_time = datetime.utcfromtimestamp(payload["exp"])
    current_time = datetime.utcnow()
    time_difference = expiration_time - current_time

    # Comprobamos que la diferencia es cercana a 1 hora (damos margen de segundos)
    assert timedelta(minutes=59, seconds=50) < time_difference < timedelta(hours=1, seconds=10)

def test_create_access_token_custom_expiration():
    """Prueba que se respeta una expiración personalizada (ej: 30 minutos)."""
    user_data = {"sub": "test@example.com"}
    custom_delta = timedelta(minutes=30)
    token = create_access_token(data=user_data, expires_delta=custom_delta)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    expiration_time = datetime.utcfromtimestamp(payload["exp"])
    current_time = datetime.utcnow()
    time_difference = expiration_time - current_time

    # Comprobamos que la diferencia es cercana a 30 minutos
    assert timedelta(minutes=29, seconds=50) < time_difference < timedelta(minutes=30, seconds=10)

def test_decode_expired_token_raises_error():
    """Prueba que un token expirado lanza JWTError al decodificar."""
    # Creamos un token que expiró hace 1 segundo
    user_data = {"sub": "test@example.com"}
    expired_delta = timedelta(seconds=-1)
    token = create_access_token(data=user_data, expires_delta=expired_delta)

    # Esperamos un poco para asegurar que realmente está expirado
    time.sleep(1.1)

    with pytest.raises(JWTError):
         jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])