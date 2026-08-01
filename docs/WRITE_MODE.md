# Kodex Write Mode Contract

## Estado actual

Kodex ya tiene control plane:

```txt
snapshot → virtualize → orchestrate → branch → ship → diagnose → resume
```

Write mode debe usar ese control plane, no saltárselo.

## Contrato mínimo

Una escritura real debe seguir este flujo:

```txt
1. snapshot
2. clean preview
3. create/check task branch
4. compile spec
5. build context
6. call provider
7. validate write plan
8. create checkpoint
9. apply files
10. run checks
11. inspect diff
12. repair loop if needed
13. stop at ready_for_commit
```

## Nunca automático

Kodex no debe hacer automáticamente:

- push
- merge
- borrar archivos sensibles
- editar `.env`
- tocar `.git`
- publicar releases
- abrir PR sin aprobación

## Resultado esperado

El resultado de write mode debe verse así:

```json
{
  "status": "ready_for_commit",
  "branch": "kodex/implement-mvp",
  "written": ["agent/new_module.py", "tests/test_new_module.py"],
  "checks_ok": true,
  "diff_safe": true,
  "next_commands": [
    "git add ...",
    "git commit -m \"kodex: implement mvp\"",
    "git push -u origin kodex/implement-mvp"
  ]
}
```
