#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
OUT="$(cd "$SRC/.." && pwd)/Final Docs List"
mkdir -p "$OUT"
cd "$SRC"

shopt -s nullglob
files=(0*.tex 1*.tex 2*.tex)
if [[ ${#files[@]} -eq 0 ]]; then
  echo "No hay archivos .tex numerados para compilar."
  exit 1
fi

ok=0
fail=0
for tex in "${files[@]}"; do
  base="${tex%.tex}"
  echo "============================================================"
  echo "Compilando $tex"
  echo "============================================================"
  pdflatex -interaction=nonstopmode "$tex" >/tmp/latex-"$base".log 2>&1 || true
  pdflatex -interaction=nonstopmode "$tex" >/tmp/latex-"$base".log 2>&1 || true
  if [[ -f "$base.pdf" ]]; then
    cp -f "$base.pdf" "$OUT/$base.pdf"
    echo "OK -> $OUT/$base.pdf"
    ok=$((ok+1))
  else
    echo "ERROR en $tex (ver /tmp/latex-$base.log)"
    tail -n 40 /tmp/latex-"$base".log || true
    fail=$((fail+1))
  fi
done

# limpia auxiliares en la fuente
rm -f ./*.aux ./*.log ./*.out ./*.toc ./*.synctex.gz

echo "============================================================"
echo "Terminados: $ok  |  Fallidos: $fail"
echo "PDF en: $OUT"
ls -la "$OUT"
