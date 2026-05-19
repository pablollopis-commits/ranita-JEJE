
echo "🚀 Subiendo cambios a GitHub..."
git add .
git commit -m "Auto-commit: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main
echo "✅ Cambios subidos exitosamente"

git remote add origin https://github.com/pablollopis-commits/ranita-JEJE.git
git branch -M main
git push -u origin main

pablollopis-commits
