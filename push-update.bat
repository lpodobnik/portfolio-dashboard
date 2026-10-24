@echo off
echo Pushing portfolio dashboard to GitHub...
cp portfolio-dashboard.html index.html
git add index.html
git commit -m "Update dashboard"
git push
echo.
echo Done! Live at: https://lpodobnik0.github.io/portfolio-dashboard/
pause
