@echo off
echo.
echo ========================================
echo  CartoonizeMe - Fix Git Secret History
echo ========================================
echo.

echo [Step 1] Installing git-filter-repo...
pip install git-filter-repo
echo.

echo [Step 2] Removing .env from ALL old commits...
git filter-repo --path .env --invert-paths --force
echo.

echo [Step 3] Writing replacements file to scrub old payment.py...
echo regex:sk_test_[A-Za-z0-9]+==>RAZORPAY_ONLY > _replacements.txt
git filter-repo --replace-text _replacements.txt --force
del _replacements.txt
echo.

echo [Step 4] Re-adding remote (filter-repo removes it)...
git remote add origin https://github.com/Prathmeshkangane/Caartoonize-me.git
echo.

echo [Step 5] Force-pushing clean history...
git push --force origin main
echo.

echo ========================================
echo  Done! Check above for SUCCESS or errors
echo ========================================
pause