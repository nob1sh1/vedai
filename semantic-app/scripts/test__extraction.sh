#!/bin/bash

# Test script to verify extraction from sample files
# Usage: ./test_extraction.sh sample_file.html

if [ $# -ne 1 ]; then
    echo "Usage: $0 <html_file>"
    exit 1
fi

HTML_FILE="$1"

if [ ! -f "$HTML_FILE" ]; then
    echo "File not found: $HTML_FILE"
    exit 1
fi

echo "Testing extraction from: $(basename "$HTML_FILE")"
echo "=================================="

# Extract main content
main_content=$(sed -n '/<H3 ALIGN="CENTER">Rig Veda Book.*Hymn/,/<HR>/p' "$HTML_FILE")
content=$(echo "$main_content" | sed '/<H3 ALIGN="CENTER">/d' | sed '/<HR>/d')

echo "Raw content (first 200 chars):"
echo "$content" | head -c 200
echo -e "\n\n"

# Extract Sanskrit
echo "SANSKRIT TEXT:"
echo "-------------"
sanskrit_section=$(echo "$content" | sed -n '1,/<P><\/P>/p' | sed '/<P><\/P>/d')
sanskrit_clean=$(echo "$sanskrit_section" | \
    sed 's/<BR[^>]*>/ /g' | \
    sed 's/<[^>]*>//g' | \
    sed 's/&nbsp;/ /g' | \
    sed 's/&amp;/\&/g' | \
    sed 's/&lt;/</g' | \
    sed 's/&gt;/>/g' | \
    tr '\n' ' ' | \
    sed 's/[[:space:]]\+/ /g' | \
    sed 's/^[[:space:]]*//' | \
    sed 's/[[:space:]]*$//')

echo "$sanskrit_clean"
echo -e "\n"

# Extract Romanized
echo "ROMANIZED TEXT:"
echo "--------------"
romanized_section=$(echo "$content" | sed -n '/<P><\/P>/,$p' | sed '1d')
romanized_clean=$(echo "$romanized_section" | \
    sed 's/<BR[^>]*>/ /g' | \
    sed 's/<[^>]*>//g' | \
    sed 's/&nbsp;/ /g' | \
    sed 's/&amp;/\&/g' | \
    sed 's/&lt;/</g' | \
    sed 's/&gt;/>/g' | \
    tr '\n' ' ' | \
    sed 's/[[:space:]]\+/ /g' | \
    sed 's/^[[:space:]]*//' | \
    sed 's/[[:space:]]*$//')

echo "$romanized_clean"
echo -e "\n"

# Count verses
verse_count=$(echo "$sanskrit_clean" | grep -o '||' | wc -l)
echo "Verse count: $verse_count"

# Test filename parsing
filename=$(basename "$HTML_FILE")
if [[ $filename =~ rv_([0-9]+)_([0-9]+)\.html ]]; then
    book="${BASH_REMATCH[1]}"
    hymn="${BASH_REMATCH[2]}"
    echo "Extracted - Book: $book, Hymn: $hymn"
    
    # Show URL format
    book_padded=$(printf "%02d" "$book")
    hymn_padded=$(printf "%03d" "$hymn")
    url="https://sacred-texts.com/hin/rvsan/rv${book_padded}${hymn_padded}.htm"
    echo "Generated URL: $url"
else
    echo "Could not parse filename: $filename"
fi