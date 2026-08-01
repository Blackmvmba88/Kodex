# Kodex Write Activation Bundle

Este paquete prepara a Kodex para avanzar hacia escritura real con frenos.

No reemplaza tu repo. Es una capa de activación y política para que el modo escritura
sea explícito, revisable y reversible.

## Objetivo

Pasar de:

```txt
app-build preview
```

a:

```txt
provider → generation → write plan → approval → safe apply → tests → repair loop
```

## Filosofía

Kodex puede escribir sólo cuando:

- el repo está limpio
- está en rama segura
- el write plan fue validado
- no toca rutas prohibidas
- no escribe secretos
- los cambios caben dentro del límite configurado
- hay checkpoint antes de aplicar
- se detiene antes de commit/push

## Archivos

- `configs/kodex_write_policy.json`: política de escritura segura
- `docs/WRITE_MODE.md`: contrato operativo
- `scripts/verify_write_activation.sh`: verificación local básica
- `examples/SPEC.md`: ejemplo de spec de app
- `examples/AGENTS.md`: reglas para el agente
- `examples/README_APP.md`: ejemplo de README de producto
- `roadmap/NEXT_BRAIN_STEPS.md`: próximos pasos técnicos
- `patches/WRITE_MODE_IMPLEMENTATION_PLAN.md`: plan para implementar write mode en Kodex

## Uso sugerido

Copia el contenido que quieras al repo o descomprímelo dentro de una rama nueva:

```bash
cd ~/Kodex
git checkout main
git pull
git checkout -b kodex/write-activation
unzip ~/Downloads/kodex_write_activation_bundle.zip -d .
bash scripts/verify_write_activation.sh
git status
```

Luego revisas y decides qué entra al repo.
