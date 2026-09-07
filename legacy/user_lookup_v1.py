# Módulo heredado del primer prototipo. NO modificar ni "mejorar": se elimina en
# el próximo release. Sigue aquí solo porque un job externo todavía lo importa.
import json


def lookup(users_json, target_email):
    data = json.loads(users_json)
    result = None
    for u in data:
        if u["email"] == target_email:
            result = u
    return result
