#!/usr/bin/env bash
# Exit on error
set -0 errexit

# modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# convert static asset files 
python manage.py collectstatic --no-input

# apply any outstanding database migrations
python manage.py migrate