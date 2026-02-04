# Prompt para Módulo Security & Authentication

## 📋 Contexto del Proyecto
Estás desarrollando el **Módulo de Seguridad y Autenticación** para un sistema de copiloto con IA gubernamental. Este módulo es CRÍTICO ya que maneja datos sensibles del gobierno y debe cumplir con estándares de seguridad y normativas de protección de datos.

## 🎯 Objetivo del Módulo
Crear un sistema de seguridad robusto que:
1. Autentique usuarios con múltiples métodos (SSO, OAuth, SAML)
2. Implemente control de acceso basado en roles (RBAC)
3. Audite todas las operaciones críticas
4. Encripte datos sensibles en tránsito y reposo
5. Prevenga ataques comunes (SQL injection, XSS, CSRF)
6. Gestione secretos y API keys de forma segura
7. Implemente rate limiting y protección DDoS

## 📁 Estructura de Archivos a Generar

```
modules/security/
├── __init__.py
├── config.py                   # Configuración de seguridad
├── auth.py                     # Autenticación
├── rbac.py                     # Control de acceso (RBAC)
├── encryption.py               # Encriptación de datos
├── audit_logger.py             # Auditoría de acciones
├── rate_limiter.py             # Rate limiting
├── secrets_manager.py          # Gestión de secretos
├── input_validator.py          # Validación de inputs
├── session_manager.py          # Gestión de sesiones
└── utils/
    ├── __init__.py
    ├── password_utils.py
    ├── token_utils.py
    └── security_utils.py
```

## 🔧 Especificaciones Técnicas

### 1. auth.py

**Propósito**: Autenticación de usuarios con múltiples métodos.

**Funcionalidades requeridas**:
```python
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import bcrypt
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    """Modelo de usuario."""
    id: str
    email: EmailStr
    username: str
    full_name: str
    roles: List[str]
    organization: str
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class AuthenticationManager:
    """
    Gestiona autenticación de usuarios.
    """
    
    def __init__(self, 
                 secret_key: str,
                 token_expiry_hours: int = 24):
        """
        Args:
            secret_key: Clave secreta para JWT
            token_expiry_hours: Expiración de tokens en horas
        """
        self.secret_key = secret_key
        self.token_expiry = timedelta(hours=token_expiry_hours)
        self.algorithm = "HS256"
    
    def authenticate_user(self, 
                         username: str, 
                         password: str) -> Optional[User]:
        """
        Autentica usuario con credenciales.
        
        Args:
            username: Username o email
            password: Password en texto plano
            
        Returns:
            User object si autenticación exitosa, None si falla
        """
        # 1. Buscar usuario en BD
        user_data = self._get_user_from_db(username)
        if not user_data:
            return None
        
        # 2. Verificar password
        if not self._verify_password(password, user_data['password_hash']):
            return None
        
        # 3. Verificar cuenta activa
        if not user_data['is_active']:
            raise AuthenticationError("Cuenta desactivada")
        
        # 4. Actualizar último login
        self._update_last_login(user_data['id'])
        
        # 5. Retornar usuario
        return User(**user_data)
    
    def authenticate_with_sso(self, 
                             sso_token: str,
                             provider: str = "oauth2") -> Optional[User]:
        """
        Autentica usuario con SSO (OAuth2, SAML).
        
        Args:
            sso_token: Token del proveedor SSO
            provider: 'oauth2', 'saml', 'ldap'
        """
        if provider == "oauth2":
            return self._authenticate_oauth2(sso_token)
        elif provider == "saml":
            return self._authenticate_saml(sso_token)
        elif provider == "ldap":
            return self._authenticate_ldap(sso_token)
        else:
            raise ValueError(f"Proveedor no soportado: {provider}")
    
    def create_access_token(self, user: User) -> str:
        """
        Crea JWT access token.
        
        Returns:
            Token JWT como string
        """
        payload = {
            'user_id': user.id,
            'email': user.email,
            'roles': user.roles,
            'exp': datetime.utcnow() + self.token_expiry,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def create_refresh_token(self, user: User) -> str:
        """
        Crea refresh token de larga duración.
        """
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=30),
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verifica y decodifica JWT token.
        
        Returns:
            Payload del token
            
        Raises:
            JWTError si token inválido o expirado
        """
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expirado")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Token inválido")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Genera nuevo access token desde refresh token.
        """
        payload = self.verify_token(refresh_token)
        
        if payload.get('type') != 'refresh':
            raise AuthenticationError("No es un refresh token")
        
        user = self._get_user_from_db(payload['user_id'])
        return self.create_access_token(User(**user))
    
    def logout(self, token: str):
        """
        Cierra sesión invalidando token.
        Requiere blacklist de tokens.
        """
        self._add_token_to_blacklist(token)
    
    def change_password(self, 
                       user_id: str,
                       old_password: str,
                       new_password: str) -> bool:
        """
        Cambia password de usuario.
        """
        # 1. Verificar password actual
        user_data = self._get_user_from_db(user_id)
        if not self._verify_password(old_password, user_data['password_hash']):
            raise AuthenticationError("Password actual incorrecto")
        
        # 2. Validar nuevo password
        self._validate_password_strength(new_password)
        
        # 3. Hash y guardar
        new_hash = self._hash_password(new_password)
        self._update_password(user_id, new_hash)
        
        return True
    
    def reset_password_request(self, email: str):
        """
        Inicia proceso de reset de password.
        Envía email con token de reset.
        """
        user = self._get_user_by_email(email)
        if not user:
            # No revelar si email existe (seguridad)
            return
        
        # Generar token de reset
        reset_token = self._generate_reset_token(user['id'])
        
        # Enviar email
        self._send_reset_email(email, reset_token)
    
    def reset_password(self, reset_token: str, new_password: str) -> bool:
        """
        Completa reset de password con token.
        """
        # Verificar token
        user_id = self._verify_reset_token(reset_token)
        
        # Validar nuevo password
        self._validate_password_strength(new_password)
        
        # Actualizar password
        new_hash = self._hash_password(new_password)
        self._update_password(user_id, new_hash)
        
        # Invalidar token
        self._invalidate_reset_token(reset_token)
        
        return True
    
    # Métodos auxiliares
    def _hash_password(self, password: str) -> str:
        """Hash password con bcrypt."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def _verify_password(self, password: str, hash: str) -> bool:
        """Verifica password contra hash."""
        return bcrypt.checkpw(password.encode(), hash.encode())
    
    def _validate_password_strength(self, password: str):
        """
        Valida fortaleza de password.
        Requisitos:
        - Mínimo 12 caracteres
        - Al menos 1 mayúscula
        - Al menos 1 minúscula
        - Al menos 1 número
        - Al menos 1 carácter especial
        """
        if len(password) < 12:
            raise ValidationError("Password debe tener mínimo 12 caracteres")
        
        if not any(c.isupper() for c in password):
            raise ValidationError("Password debe tener al menos 1 mayúscula")
        
        if not any(c.islower() for c in password):
            raise ValidationError("Password debe tener al menos 1 minúscula")
        
        if not any(c.isdigit() for c in password):
            raise ValidationError("Password debe tener al menos 1 número")
        
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special for c in password):
            raise ValidationError("Password debe tener al menos 1 carácter especial")

class AuthenticationError(Exception):
    """Error de autenticación."""
    pass

class ValidationError(Exception):
    """Error de validación."""
    pass
```

**Dependencias**:
- PyJWT
- bcrypt
- pydantic

---

### 2. rbac.py

**Propósito**: Control de acceso basado en roles (RBAC).

**Funcionalidades requeridas**:
```python
from typing import List, Dict, Set
from enum import Enum

class Permission(str, Enum):
    """Permisos del sistema."""
    # Documentos
    READ_DOCUMENTS = "read:documents"
    WRITE_DOCUMENTS = "write:documents"
    DELETE_DOCUMENTS = "delete:documents"
    
    # Datos
    READ_DATA = "read:data"
    WRITE_DATA = "write:data"
    EXPORT_DATA = "export:data"
    
    # Mapas
    VIEW_MAPS = "view:maps"
    EDIT_MAPS = "edit:maps"
    
    # SQL
    EXECUTE_SQL = "execute:sql"
    
    # Admin
    MANAGE_USERS = "manage:users"
    VIEW_AUDIT = "view:audit"
    SYSTEM_CONFIG = "system:config"

class Role(BaseModel):
    """Modelo de rol."""
    name: str
    description: str
    permissions: List[Permission]

class RBACManager:
    """
    Gestiona control de acceso basado en roles.
    """
    
    def __init__(self):
        self.roles = self._initialize_roles()
    
    def _initialize_roles(self) -> Dict[str, Role]:
        """
        Define roles del sistema.
        """
        return {
            'admin': Role(
                name='admin',
                description='Administrador del sistema',
                permissions=list(Permission)  # Todos los permisos
            ),
            'analyst': Role(
                name='analyst',
                description='Analista de datos',
                permissions=[
                    Permission.READ_DOCUMENTS,
                    Permission.READ_DATA,
                    Permission.EXPORT_DATA,
                    Permission.VIEW_MAPS,
                    Permission.EXECUTE_SQL
                ]
            ),
            'planner': Role(
                name='planner',
                description='Planificador territorial',
                permissions=[
                    Permission.READ_DOCUMENTS,
                    Permission.READ_DATA,
                    Permission.VIEW_MAPS,
                    Permission.EDIT_MAPS
                ]
            ),
            'viewer': Role(
                name='viewer',
                description='Usuario de solo lectura',
                permissions=[
                    Permission.READ_DOCUMENTS,
                    Permission.READ_DATA,
                    Permission.VIEW_MAPS
                ]
            )
        }
    
    def check_permission(self, 
                        user: User, 
                        permission: Permission) -> bool:
        """
        Verifica si usuario tiene permiso.
        
        Args:
            user: Usuario a verificar
            permission: Permiso requerido
            
        Returns:
            True si tiene permiso, False si no
        """
        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role and permission in role.permissions:
                return True
        return False
    
    def require_permission(self, permission: Permission):
        """
        Decorador para requerir permiso en función.
        
        Usage:
            @rbac.require_permission(Permission.EXECUTE_SQL)
            def execute_query(user, sql):
                ...
        """
        def decorator(func):
            def wrapper(user: User, *args, **kwargs):
                if not self.check_permission(user, permission):
                    raise PermissionDeniedError(
                        f"Usuario no tiene permiso: {permission.value}"
                    )
                return func(user, *args, **kwargs)
            return wrapper
        return decorator
    
    def get_user_permissions(self, user: User) -> Set[Permission]:
        """
        Obtiene todos los permisos de un usuario.
        """
        permissions = set()
        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role:
                permissions.update(role.permissions)
        return permissions
    
    def assign_role(self, user_id: str, role_name: str):
        """
        Asigna rol a usuario.
        """
        if role_name not in self.roles:
            raise ValueError(f"Rol no existe: {role_name}")
        
        # Agregar rol en BD
        self._add_role_to_user(user_id, role_name)
    
    def remove_role(self, user_id: str, role_name: str):
        """
        Remueve rol de usuario.
        """
        self._remove_role_from_user(user_id, role_name)
    
    def create_custom_role(self, 
                          name: str,
                          description: str,
                          permissions: List[Permission]):
        """
        Crea rol personalizado.
        """
        role = Role(
            name=name,
            description=description,
            permissions=permissions
        )
        self.roles[name] = role
        self._save_role_to_db(role)

class PermissionDeniedError(Exception):
    """Error de permiso denegado."""
    pass
```

---

### 3. audit_logger.py

**Propósito**: Auditoría completa de operaciones.

**Funcionalidades requeridas**:
```python
from datetime import datetime
from typing import Dict, Any, Optional
import json
import logging

class AuditEvent(BaseModel):
    """Modelo de evento de auditoría."""
    id: str
    timestamp: datetime
    user_id: str
    user_email: str
    action: str
    resource: str
    resource_id: Optional[str]
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    success: bool
    error_message: Optional[str] = None

class AuditLogger:
    """
    Logger de auditoría para operaciones críticas.
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Configura logger."""
        logger = logging.getLogger('audit')
        logger.setLevel(logging.INFO)
        
        # File handler
        handler = logging.FileHandler('logs/audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def log_event(self, event: AuditEvent):
        """
        Registra evento de auditoría.
        """
        # 1. Log a archivo
        self.logger.info(json.dumps(event.dict()))
        
        # 2. Guardar en BD
        self._save_to_db(event)
        
        # 3. Si es crítico, alertar
        if self._is_critical_event(event):
            self._send_alert(event)
    
    def log_login(self, user: User, ip: str, success: bool):
        """Registra intento de login."""
        event = AuditEvent(
            id=self._generate_id(),
            timestamp=datetime.utcnow(),
            user_id=user.id if user else "unknown",
            user_email=user.email if user else "unknown",
            action="login",
            resource="auth",
            resource_id=None,
            details={},
            ip_address=ip,
            user_agent="",
            success=success
        )
        self.log_event(event)
    
    def log_data_access(self, 
                       user: User,
                       resource: str,
                       resource_id: str,
                       action: str = "read"):
        """Registra acceso a datos."""
        event = AuditEvent(
            id=self._generate_id(),
            timestamp=datetime.utcnow(),
            user_id=user.id,
            user_email=user.email,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details={},
            ip_address="",
            user_agent="",
            success=True
        )
        self.log_event(event)
    
    def log_query_execution(self,
                           user: User,
                           query_type: str,
                           query: str,
                           success: bool,
                           error: str = None):
        """Registra ejecución de queries."""
        event = AuditEvent(
            id=self._generate_id(),
            timestamp=datetime.utcnow(),
            user_id=user.id,
            user_email=user.email,
            action="execute_query",
            resource=query_type,
            resource_id=None,
            details={'query': query[:500]},  # Limitar tamaño
            ip_address="",
            user_agent="",
            success=success,
            error_message=error
        )
        self.log_event(event)
    
    def get_audit_trail(self,
                       user_id: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       action: Optional[str] = None) -> List[AuditEvent]:
        """
        Recupera trail de auditoría con filtros.
        """
        # Construir query con filtros
        query = "SELECT * FROM audit_log WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        if action:
            query += " AND action = ?"
            params.append(action)
        
        # Ejecutar y retornar
        results = self._execute_query(query, params)
        return [AuditEvent(**r) for r in results]
    
    def _is_critical_event(self, event: AuditEvent) -> bool:
        """Determina si evento es crítico."""
        critical_actions = [
            'delete', 'drop', 'truncate', 
            'admin_action', 'permission_change'
        ]
        return event.action in critical_actions or not event.success
    
    def _send_alert(self, event: AuditEvent):
        """Envía alerta de evento crítico."""
        # Implementar notificación (email, Slack, etc.)
        pass
```

---

### 4. rate_limiter.py

**Propósito**: Rate limiting para prevenir abuso.

**Funcionalidades requeridas**:
```python
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple

class RateLimiter:
    """
    Rate limiter para prevenir abuso de APIs.
    """
    
    def __init__(self, redis_client=None):
        """
        Args:
            redis_client: Cliente Redis (opcional, usa memoria si None)
        """
        self.redis = redis_client
        self.memory_store: Dict[str, list] = defaultdict(list)
    
    def check_rate_limit(self,
                        identifier: str,
                        max_requests: int = 100,
                        window_seconds: int = 60) -> Tuple[bool, Dict]:
        """
        Verifica rate limit.
        
        Args:
            identifier: ID único (user_id, IP, etc.)
            max_requests: Máximo de requests en ventana
            window_seconds: Ventana de tiempo en segundos
            
        Returns:
            (allowed, info) donde info contiene:
            - remaining: requests restantes
            - reset_time: cuándo se resetea
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        
        if self.redis:
            return self._check_redis(identifier, max_requests, window_seconds, now)
        else:
            return self._check_memory(identifier, max_requests, window_start, now)
    
    def _check_memory(self, identifier, max_requests, window_start, now):
        """Implementación en memoria."""
        # Limpiar requests antiguos
        self.memory_store[identifier] = [
            ts for ts in self.memory_store[identifier]
            if ts > window_start
        ]
        
        # Agregar request actual
        self.memory_store[identifier].append(now)
        
        # Verificar límite
        count = len(self.memory_store[identifier])
        allowed = count <= max_requests
        
        return allowed, {
            'remaining': max(0, max_requests - count),
            'reset_time': window_start + timedelta(seconds=60)
        }
    
    def _check_redis(self, identifier, max_requests, window_seconds, now):
        """Implementación con Redis."""
        key = f"rate_limit:{identifier}"
        
        # Usar sliding window con Redis
        pipe = self.redis.pipeline()
        pipe.zadd(key, {str(now): now.timestamp()})
        pipe.zremrangebyscore(key, '-inf', (now - timedelta(seconds=window_seconds)).timestamp())
        pipe.zcard(key)
        pipe.expire(key, window_seconds)
        
        _, _, count, _ = pipe.execute()
        
        allowed = count <= max_requests
        
        return allowed, {
            'remaining': max(0, max_requests - count),
            'reset_time': now + timedelta(seconds=window_seconds)
        }
    
    def rate_limit_decorator(self, max_requests=100, window_seconds=60):
        """
        Decorador para aplicar rate limiting a funciones.
        
        Usage:
            @rate_limiter.rate_limit_decorator(max_requests=10, window_seconds=60)
            def api_endpoint(user_id):
                ...
        """
        def decorator(func):
            def wrapper(identifier, *args, **kwargs):
                allowed, info = self.check_rate_limit(
                    identifier, max_requests, window_seconds
                )
                
                if not allowed:
                    raise RateLimitExceeded(
                        f"Rate limit excedido. Reset en {info['reset_time']}"
                    )
                
                return func(identifier, *args, **kwargs)
            return wrapper
        return decorator

class RateLimitExceeded(Exception):
    """Excepción de rate limit excedido."""
    pass
```

---

## 📝 Instrucciones de Implementación

### Paso 1: Instalación
```bash
pip install PyJWT bcrypt cryptography redis pydantic
```

### Paso 2: Configuración
```python
# modules/security/config.py
class SecurityConfig(BaseModel):
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = "HS256"
    token_expiry_hours: int = 24
    password_min_length: int = 12
    max_login_attempts: int = 5
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    enable_mfa: bool = False
```

### Paso 3: Middleware de Seguridad
```python
# modules/security/middleware.py
class SecurityMiddleware:
    """Middleware de seguridad para FastAPI/Streamlit."""
    
    def __init__(self, auth_manager, rbac_manager, rate_limiter):
        self.auth = auth_manager
        self.rbac = rbac_manager
        self.rate_limiter = rate_limiter
    
    async def __call__(self, request, call_next):
        # 1. Rate limiting
        ip = request.client.host
        allowed, _ = self.rate_limiter.check_rate_limit(ip)
        if not allowed:
            return Response("Rate limit exceeded", status_code=429)
        
        # 2. Autenticación
        token = request.headers.get("Authorization")
        if token:
            user = self.auth.verify_token(token.replace("Bearer ", ""))
            request.state.user = user
        
        # 3. Continuar
        response = await call_next(request)
        
        return response
```

---

## ✅ Criterios de Aceptación

- ✅ Autenticación robusta con JWT
- ✅ RBAC implementado correctamente
- ✅ Auditoría completa de operaciones
- ✅ Rate limiting efectivo
- ✅ Passwords seguros (bcrypt + validación)
- ✅ Prevención de ataques comunes
- ✅ Cumplimiento normativo

---

## 🔒 Checklist de Seguridad

- [ ] Passwords hasheados con bcrypt
- [ ] JWT con expiración
- [ ] HTTPS en producción
- [ ] SQL injection prevención
- [ ] XSS prevención
- [ ] CSRF tokens
- [ ] Rate limiting
- [ ] Auditoría de acciones
- [ ] Encriptación de datos sensibles
- [ ] Gestión segura de secretos
- [ ] Validación de inputs
- [ ] Manejo seguro de errores (no exponer info)

---

**¿Listo?** Copia este prompt en Cursor para generar el módulo de seguridad completo.

**⚠️ IMPORTANTE**: Este módulo maneja seguridad crítica. Asegúrate de:
1. Revisar código generado cuidadosamente
2. Realizar pentesting antes de producción
3. Seguir OWASP Top 10
4. Cumplir normativas locales de protección de datos
