coverage:
	coverage run --source=crowdin setup.py test
	coverage html

showcov: coverage
	open htmlcov/index.html

test:
	python setup.py test
