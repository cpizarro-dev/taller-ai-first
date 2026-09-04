#!/usr/bin/env bash
# commit-conventional.sh - PreToolUse hook sobre Bash: bloquea `git commit`
# cuyo mensaje no siga Conventional Commits
# (tipo(scope opcional)!: descripción).
#
# Recibe el hook input JSON por stdin (tool_input.command trae el comando
# bash a ejecutar). Si no es un `git commit`, o si no se puede extraer el
# mensaje (p. ej. abre el editor interactivo), lo deja pasar sin opinar.

set -uo pipefail

input="$(cat)"
command="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"

[ -z "$command" ] && exit 0

# Solo nos interesan invocaciones de `git commit` (no `git commit-graph`, etc).
if ! printf '%s' "$command" | grep -qE '(^|[;&|]|\s)git[[:space:]]+commit([[:space:]]|$)'; then
    exit 0
fi

# --amend --no-edit reutiliza el mensaje ya existente (ya validado antes).
if printf '%s' "$command" | grep -qE -- '--no-edit\b'; then
    exit 0
fi

message=""

# 1. Heredoc: -m "$(cat <<'EOF' ... EOF)" (estilo usado por Claude Code).
if printf '%s' "$command" | grep -q 'cat <<'; then
    message="$(printf '%s' "$command" | awk '
        /cat <<.*EOF/ { in_heredoc=1; next }
        in_heredoc && /^EOF$/ { in_heredoc=0; next }
        in_heredoc && subject == "" && NF > 0 { subject = $0 }
        END { print subject }
    ')"
fi

# 2. -m "..." / --message "..." (comillas dobles).
if [ -z "$message" ]; then
    message="$(printf '%s' "$command" | grep -oE -- '(-m|--message)[= ]?"[^"]*"' | head -n1 \
        | sed -E 's/^(-m|--message)[= ]?"//; s/"$//')"
fi

# 3. -m '...' / --message '...' (comillas simples).
if [ -z "$message" ]; then
    message="$(printf '%s' "$command" | grep -oE -- "(-m|--message)[= ]?'[^']*'" | head -n1 \
        | sed -E "s/^(-m|--message)[= ]?'//; s/'\$//")"
fi

# Sin -m/--message/heredoc detectable (p. ej. abre editor interactivo): no
# podemos validar el mensaje, no bloqueamos.
[ -z "$message" ] && exit 0

subject="$(printf '%s' "$message" | head -n1)"

pattern='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-zA-Z0-9_./-]+\))?!?: .+'

if printf '%s' "$subject" | grep -qE "$pattern"; then
    exit 0
fi

reason="Commit bloqueado: el mensaje \"${subject}\" no sigue Conventional Commits. Formato esperado: tipo(scope opcional)!: descripción — con tipo en feat, fix, docs, style, refactor, perf, test, build, ci, chore o revert."

echo "$reason" >&2

jq -n --arg reason "$reason" '{
    hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: $reason
    }
}'

exit 0
