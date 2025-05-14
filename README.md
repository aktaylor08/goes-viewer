Work in progress, but can run with these commands: 
```
docker run -it -p6379:6379 redis:latest --save "" --appendonly no
 uvicorn server-red:app
 ./tile.py r
./scheduler.py
```
then navigate to test.html
