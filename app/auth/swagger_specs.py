"""
Especificaciones Swagger para las rutas de autenticación
"""

LOGIN_SPEC = {
    "tags": ["Auth"],
    "summary": "Iniciar sesión de usuario",
    "description": "Autentica un usuario con email y contraseña, devuelve un token JWT",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "Email del usuario",
                        "example": "usuario@ejemplo.com"
                    },
                    "password": {
                        "type": "string",
                        "description": "Contraseña del usuario",
                        "example": "miContraseña123"
                    }
                },
                "required": ["email", "password"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Login exitoso",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "ID del usuario"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email del usuario"
                    },
                    "access_token": {
                        "type": "string",
                        "description": "Token JWT para autenticación"
                    }
                }
            }
        },
        "400": {
            "description": "Datos faltantes",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Missing email or password"
                    }
                }
            }
        },
        "401": {
            "description": "Contraseña incorrecta",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Incorrect password"
                    }
                }
            }
        },
        "404": {
            "description": "Email no encontrado",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Email not found"
                    }
                }
            }
        }
    }
}

REGISTER_SPEC = {
    "tags": ["Auth"],
    "summary": "Registrar nuevo usuario",
    "description": "Crea un nuevo usuario. El primer usuario registrado será automáticamente 'owner', los demás serán 'driver'",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Nombre del usuario",
                        "example": "Juan"
                    },
                    "surname": {
                        "type": "string",
                        "description": "Apellido del usuario",
                        "example": "Pérez"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "Email del usuario",
                        "example": "juan.perez@ejemplo.com"
                    },
                    "password": {
                        "type": "string",
                        "description": "Contraseña del usuario",
                        "example": "miContraseña123"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Número de teléfono (opcional)",
                        "example": "+1234567890"
                    }
                },
                "required": ["name", "surname", "email", "password"]
            }
        }
    ],
    "responses": {
        "201": {
            "description": "Usuario creado exitosamente",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "ID del usuario creado"
                    },
                    "name": {
                        "type": "string",
                        "description": "Nombre del usuario"
                    },
                    "surname": {
                        "type": "string",
                        "description": "Apellido del usuario"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email del usuario"
                    },
                    "rol": {
                        "type": "string",
                        "description": "Rol asignado (owner o driver)",
                        "enum": ["owner", "driver"]
                    },
                    "phone": {
                        "type": "string",
                        "description": "Número de teléfono"
                    },
                    "status": {
                        "type": "string",
                        "description": "Estado del usuario",
                        "example": "active"
                    }
                }
            }
        },
        "400": {
            "description": "Email ya existe",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Email already exists"
                    }
                }
            }
        },
        "500": {
            "description": "Error interno del servidor",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Error creating user"
                    },
                    "error": {
                        "type": "string",
                        "description": "Detalles del error"
                    }
                }
            }
        }
    }
}
