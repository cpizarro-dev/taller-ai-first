---
name: prepara-pr
description: This skill should be used when the user asks to "prepara el PR", "prepara-pr", "abre el PR", "abre el pull request", "crea el PR de esta rama", or wants to open a GitHub pull request for the current branch after quality checks pass.
version: 0.1.0
---

# Prepara PR

Abre el pull request de la rama actual en GitHub, pero solo si pasa una
serie de controles de calidad y una revisión de código automática.

## Flujo

1. **Correr los gates.** Ejecutar `gates.sh` (ubicado en la carpeta de
   este skill, `.claude/skills/prepara-pr/gates.sh`); el script se
   posiciona solo en la raíz del repo sin importar desde dónde se lo
   invoque. Corre, en este orden, y siempre completa los cuatro aunque
   alguno falle:
   1. `ruff check` sobre `src/` y `tests/` (vía `uvx ruff`).
   2. `bandit` sobre `src/`, filtrando severidad media/alta (vía `uvx
      bandit`).
   3. `pytest` (vía `uv run pytest`).
   4. Verificación de que todos los commits de la rama actual contra
      `main` (sin contar merges) siguen el formato Conventional Commits
      (`tipo(scope opcional)!: descripción`, con `tipo` en `feat`,
      `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`,
      `ci`, `chore`, `revert`).

   El script devuelve código de salida `1` si **cualquier** gate falló,
   `0` si los cuatro pasaron.

2. **Si algún gate falló:** mostrar al usuario la salida relevante del
   gate (o gates) que fallaron y detenerse. **No** pedir la revisión al
   subagente ni abrir el PR.

3. **Si los cuatro gates pasaron:** pedir la revisión al subagente
   `revisor-pr` sobre los commits de la rama actual contra `main` (el
   mismo rango `main..HEAD` usado en el gate 4).
   - Si el veredicto del subagente es de **rechazo**: reportar al
     usuario los hallazgos y el veredicto, y **no** abrir el PR.
   - Si el veredicto es de **aprobación**: continuar al paso 4.

4. **Abrir el PR con `gh`.** Con la rama actual ya empujada al remoto
   (hacer `git push -u origin <rama-actual>` si todavía no tiene
   upstream), correr `gh pr create` contra la rama base `main`,
   generando el título y cuerpo del PR a partir de los commits de la
   rama (por ejemplo con `--fill` o redactando un resumen breve).
   Reportar al usuario la URL del PR creado.

## Notas

- Los controles nunca deben saltearse ni relajarse aunque el usuario
  no lo pida explícitamente cada vez: son la condición para llegar al
  paso 3 y al paso 4.
- `uvx` descarga `ruff`/`bandit` en un entorno aislado la primera vez
  que se usan; no hace falta agregarlos a las dependencias del
  proyecto.
- Antes de correr `gh pr create` o `git push`, confirmar con el
  usuario si hay dudas sobre a qué remoto/rama base apunta (por
  defecto: `origin`/`main`), ya que empujar y abrir un PR son acciones
  visibles para otros.
