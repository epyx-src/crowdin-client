coverage:
	coverage run --source=crowdin test
	coverage html
	open htmlcov/index.html
