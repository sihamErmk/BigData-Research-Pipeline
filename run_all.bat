@echo off
echo ============================================================
echo MASSIVE DATA COLLECTION - ALL SPIDERS
echo ============================================================
echo.
echo This will scrape data from:
echo   - Google Scholar (25 keywords x 20 articles = 500)
echo   - arXiv (30 keywords x 50 articles = 1,500)
echo   - IEEE (may be blocked by Cloudflare)
echo   - ACM (may be blocked by Cloudflare)
echo   - ScienceDirect (may be blocked)
echo.
echo Expected total: ~2,000 articles
echo.
pause
echo.
echo Starting collection...
echo.

python run_all_spiders.py

echo.
echo ============================================================
echo DATA COLLECTION COMPLETE!
echo ============================================================
echo.
echo Check your data in MongoDB:
echo   mongosh
echo   use research_db
echo   db.articles.countDocuments()
echo.
pause
