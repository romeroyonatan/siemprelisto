import voluptuous as v


validar_persona = v.Schema({
    v.Required('nombre'): v.All(str, v.Length(min=1)),
    v.Required('apellido'): v.All(str, v.Length(min=1)),
})
