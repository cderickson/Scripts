:: Converts jupyter notebook to script, runs script, then deletes.
:: Pulls data starting from user-input start date, cleans and transforms data, inserts/updates to Azure DB.
cd C:\Users\chris\Documents\GitHub\Jupyter-Notebooks
jupyter nbconvert --to script 2022-12-30-mtgo-vintage-metagame-etl-azure-db.ipynb
python 2022-12-30-mtgo-vintage-metagame-etl-azure-db.py
del 2022-12-30-mtgo-vintage-metagame-etl-azure-db.py

:: Pulls tables from Azure DB, saves as .csv, moves files to Google Drive folder location.
:: If any data cells start with a '-', it will not work as expected
sqlcmd -s, -S sundodger.database.windows.net -d sundodgerdb -U chriserickson -P Erickson10 -W -Q "set nocount on; select * from sundodgerdb.dbo.vintage_events" | findstr /v /c:"-" /b > "vintage-events.csv"
sqlcmd -s, -S sundodger.database.windows.net -d sundodgerdb -U chriserickson -P Erickson10 -W -Q "set nocount on; select * from sundodgerdb.dbo.vintage_results" | findstr /v /c:"-" /b > "vintage-results.csv"

move /Y "vintage-events.csv" "G:\My Drive\Datasets\MTG Vintage\"
move /Y "vintage-results.csv" "G:\My Drive\Datasets\MTG Vintage\"