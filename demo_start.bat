@echo off
echo Starting Aplus Platform End-to-End Verification...
echo.

echo [Step 1] Ingesting enriched 340B and TIC data...
python scripts/etl/load_raw_from_csv.py

echo [Step 2] Refreshing Performance Serving Layer...
python scripts/ops/refresh_demo_serving_layer.py

echo [Step 3] Running BD Discovery Opportunity Rank Verification...
python -m scripts.tests.test_bd_discovery_ranking

echo.
echo Verification Complete. Check logs for details.
pause
