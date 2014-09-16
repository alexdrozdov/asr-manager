clean:
	find -type f -name *.pyc -exec rm {} + 
	find . -type f -exec chmod -x {} \;
	chmod +x ./loader.py
