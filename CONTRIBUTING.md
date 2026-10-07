# Contribuir a Salva Systems

Este repositorio contiene presentación y documentación pública. Cambios al producto o infraestructura real se coordinan en su contexto de desarrollo correspondiente.

## Cambios aceptables

- Correcciones verificables de contenido, enlaces y terminología.
- Documentación que distingue estado actual, alcance conceptual y propuestas.
- Recursos genéricos y ejemplos ficticios autorizados para publicación.

No adjuntar secretos, datos de clientes, mensajes privados, registros de planta o código de implementaciones privadas. Para un problema sensible, contactar al responsable por los canales de negocio existentes antes de publicar detalles.

## Flujo

1. Crear una rama desde `main` actualizado: `docs/tema`, `fix/tema` o `ci/tema`.
2. Mantener un cambio coherente por PR. Commits: `docs:`, `fix:`, `ci:` o `chore:` seguidos de su propósito real.
3. Revisar enlaces, estado del producto y ausencia de información privada.
4. Abrir un PR con propósito, cambios, impacto y validación. Esperar que CI termine y atender fallos antes de fusionar.
5. Usar un merge normal. No reescribir historial ni modificar protecciones para facilitar el merge.

No hay aplicación instalable en este repositorio. La validación de documentación requiere Python 3.10+ y el checker público de [Salva Systems](https://github.com/LehiSalvador/SalvaSystems/tree/main/tools). Copiar `check_docs.py` junto con su licencia; ejecutar desde la raíz de este repositorio:

```sh
python /ruta/al/check_docs.py --root .
git diff --check
```

El workflow fija un commit del checker para hacer reproducible la versión usada. Una actualización de ese commit requiere un PR y validación. El checker no comprueba URLs remotas, destinos de fragmentos ni comportamiento del producto; revisar esos aspectos manualmente.

## Publicación

Cambios de documentación se publican al fusionarse en `main`. Una release requiere un entregable versionado real, notas de alcance y validación; documentación rutinaria no necesita tags ni releases.

[Contexto del producto](docs/overview.md) · [Presentación](README.md)
