
import voluptuous as v


validar_user = v.Schema({
    v.Required('username'): str,
    v.Required('password'): v.All(str, v.Length(min=8)),
    'apellido': str,
    'nombre': str,
    'email': str,
})
