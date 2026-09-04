#!/usr/bin/env bash
# gates.sh - Controles de calidad previos a abrir un PR.
#
# Corre los 4 controles, mostrando la salida de cada uno, y siempre
# los ejecuta todos (no corta en el primer fallo) para que se vea el
# panorama completo. Termina con código 1 si alguno falló, 0 si todos
# pasaron.

set -uo pipefail

repo_root="$(git rev-parse --show-toplevel)" || exit 1
cd "$repo_root" || exit 1

fail=0

run_gate() {
    local name="$1"
    shift
    echo "== ${name} =="
    if "$@"; then
        echo "-- ${name}: OK --"
    else
        echo "-- ${name}: FALLÓ --"
        fail=1
    fi
    echo
}

# 1. ruff check sobre src/ y tests/, sin hallazgos.
run_gate "ruff check" uvx ruff check src/ tests/

# 2. bandit sobre src/, sin hallazgos de severidad media o alta.
run_gate "bandit" uvx bandit -r src/ --severity-level medium

# 3. pytest en verde.
run_gate "pytest" uv run pytest

# 4. Todos los commits de la rama contra main en formato Conventional Commits.
#    Se excluyen los merge commits (no los escribe una persona con ese formato).
branch="$(git rev-parse --abbrev-ref HEAD)"
echo "== Conventional Commits (main..${branch}) =="

pattern='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-zA-Z0-9_./-]+\))?!?: .+'
commits_fail=0
found_commits=0

while IFS= read -r line; do
    [ -z "$line" ] && continue
    found_commits=1
    hash="${line%% *}"
    subject="${line#* }"
    if [[ "$subject" =~ $pattern ]]; then
        echo "OK    $hash $subject"
    else
        echo "MAL   $hash $subject"
        commits_fail=1
    fi
done < <(git log --no-merges --format='%h %s' "main..${branch}")

if [ "$found_commits" -eq 0 ]; then
    echo "(sin commits nuevos contra main)"
fi

if [ "$commits_fail" -ne 0 ]; then
    echo "-- Conventional Commits: FALLÓ --"
    fail=1
else
    echo "-- Conventional Commits: OK --"
fi
echo

exit "$fail"
