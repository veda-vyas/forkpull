# forkpull

## Run using python script
`pip install -r requirements.txt`
`python forkpull.py https://github.com/<username>/<repository>.git`

## Run using executable
`pip install -r requirements.txt` & `pyinstaller --onefile forkpull.py` to generate executable
Executable will be located under `dist/` directory 
`forkpull.exe https://github.com/<username>/<repository>.git`

## Run using helper script
Helper script will be located under `dist/` directory. 
1) You need to generate executable before running helper script.
2) You need to have repos.txt too.
`python forkpull_helper.py`
