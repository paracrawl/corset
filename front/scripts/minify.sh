#!/bin/bash
currentdir=$(pwd)

cd /opt/dp/front
source venv/bin/activate

cd app/static/

# Compile custom Bootstrap css
>&2 echo "Compiling custom bootstrap..."
sass --style compressed scss/custom.scss > css/bootstrap.min.css

# Minify css
for file in $(find css \( -name "*.*" ! -iname "*.min*" \) -type f -printf "%T@ %p\n" | sort -nr | cut -d\  -f2-)
do
    filename=$(echo $file | sed 's/\.[^.]*$//')
    cat $file | npx minify --css > $filename.min.css
done

# Minify js
for file in $(find js \( -name "*.*" ! -iname "*.min*" \) -type f -printf "%T@ %p\n" | sort -nr | cut -d\  -f2-)
do
    filename=$(echo $file | sed 's/\.[^.]*$//')
    cat $file | npx minify --js > $filename.min.js
done

cd "$currentdir" || exit