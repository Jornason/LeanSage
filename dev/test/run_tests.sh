#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# LeanSage Regression Test Runner
#
# Usage:
#   bash run_tests.sh                    # full suite against localhost:9019
#   bash run_tests.sh --smoke            # smoke tests only (~10s, no AI)
#   bash run_tests.sh --no-ai            # skip tests that call the AI model
#   bash run_tests.sh --target PROD      # run against production server
#   bash run_tests.sh --target LOCAL     # run against localhost (default)
#   bash run_tests.sh --target http://... # custom URL
#   bash run_tests.sh --mark search      # only search tests
#   bash run_tests.sh --parallel         # run with 4 workers (pytest-xdist)
#   bash run_tests.sh --smoke --target PROD  # smoke against production
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Defaults ──────────────────────────────────────────────────────────────────
TARGET_URL=""
MARKS=""
EXTRA_ARGS=()
SMOKE_ONLY=false
NO_AI=false
PARALLEL=false

# ── Argument parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --smoke)
      SMOKE_ONLY=true; shift;;
    --no-ai)
      NO_AI=true; shift;;
    --parallel)
      PARALLEL=true; shift;;
    --target)
      case "$2" in
        PROD|prod)      TARGET_URL="http://47.242.43.35:9019";;
        LOCAL|local)    TARGET_URL="http://localhost:9019";;
        *)              TARGET_URL="$2";;
      esac
      shift 2;;
    --mark)
      MARKS="$2"; shift 2;;
    -k)
      EXTRA_ARGS+=("-k" "$2"); shift 2;;
    *)
      EXTRA_ARGS+=("$1"); shift;;
  esac
done

# ── Resolve target URL ────────────────────────────────────────────────────────
if [[ -n "$TARGET_URL" ]]; then
  export BASE_URL="$TARGET_URL"
elif [[ -z "${BASE_URL:-}" ]]; then
  export BASE_URL="http://localhost:9019"
fi

echo ""
echo "══════════════════════════════════════════════════════"
echo "  LeanSage Regression Tests"
echo "  Target : $BASE_URL"
echo "══════════════════════════════════════════════════════"

# ── Check Python env ──────────────────────────────────────────────────────────
if ! python3 -c "import httpx, pytest" 2>/dev/null; then
  echo ""
  echo "[setup] Installing test dependencies..."
  pip install -q -r requirements.txt
fi

# ── Build pytest arguments ────────────────────────────────────────────────────
PYTEST_ARGS=("-v" "--tb=short" "--color=yes")

if $SMOKE_ONLY; then
  PYTEST_ARGS+=("-m" "smoke")
  echo "  Mode   : smoke only (fast, no AI)"
elif $NO_AI; then
  PYTEST_ARGS+=("-m" "not ai and not slow")
  echo "  Mode   : full (AI tests skipped)"
elif [[ -n "$MARKS" ]]; then
  PYTEST_ARGS+=("-m" "$MARKS")
  echo "  Mode   : mark=$MARKS"
else
  echo "  Mode   : full regression"
fi

if $PARALLEL; then
  PYTEST_ARGS+=("-n" "4")
  echo "  Workers: 4 (parallel)"
fi

PYTEST_ARGS+=("${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}")

echo "══════════════════════════════════════════════════════"
echo ""

# ── Run ───────────────────────────────────────────────────────────────────────
python3 -m pytest "${PYTEST_ARGS[@]}"
EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
  echo "  ✅  All tests passed."
else
  echo "  ❌  Some tests failed (exit $EXIT_CODE)."
fi
echo ""
exit $EXIT_CODE
