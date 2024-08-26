## Install ubuntu package, python, nvm, node, python env, node modules
```
bash install.sh
```
## Run (delete dist -> rebuild -> export key -> run)
```
rm -rf ./templates/dist
npm run-script build
mv dist/ templates/dist/
export AWS_ACCESS_KEY_ID={}
export AWS_SECRET_ACCESS_KEY={}
python app.py
```