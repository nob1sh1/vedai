#!/bin/bash

# Script to extract Sanskrit and romanized text from Rig Veda HTML files
# Usage: ./extract_rigveda_text.sh input_directory output_file.json

# Check if correct number of arguments provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <input_directory> <output_file.json>"
    echo "Example: $0 data/rigveda_corpus/raw_html rigveda_extracted.json"
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_FILE="$2"

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Input directory '$INPUT_DIR' does not exist"
    exit 1
fi

# Function to extract text content from HTML and clean it
extract_text_content() {
    local html_file="$1"
    local extract_type="$2"  # "sanskrit" or "romanized"
    
    # Extract the main content between H3 heading and the first HR
    main_content=$(sed -n '/<H3 ALIGN="CENTER">Rig Veda Book.*Hymn/,/<HR>/p' "$html_file")
    
    # Remove the H3 heading line and HR line
    content=$(echo "$main_content" | sed '/<H3 ALIGN="CENTER">/d' | sed '/<HR>/d')
    
    if [ "$extract_type" = "sanskrit" ]; then
        # Extract Sanskrit text (Devanagari script) - appears before <P></P>
        sanskrit_section=$(echo "$content" | sed -n '1,/<P><\/P>/p' | sed '/<P><\/P>/d')
        
        # Clean up the Sanskrit text
        echo "$sanskrit_section" | \
        sed 's/<BR[^>]*>/ /g' | \
        sed 's/<[^>]*>//g' | \
        sed 's/&nbsp;/ /g' | \
        sed 's/&amp;/\&/g' | \
        sed 's/&lt;/</g' | \
        sed 's/&gt;/>/g' | \
        tr '\n' ' ' | \
        sed 's/[[:space:]]\+/ /g' | \
        sed 's/^[[:space:]]*//' | \
        sed 's/[[:space:]]*$//'
        
    else
        # Extract romanized text (after <P></P>)
        romanized_section=$(echo "$content" | sed -n '/<P><\/P>/,$p' | sed '1d')
        
        # Clean up the romanized text
        echo "$romanized_section" | \
        sed 's/<BR[^>]*>/ /g' | \
        sed 's/<[^>]*>//g' | \
        sed 's/&nbsp;/ /g' | \
        sed 's/&amp;/\&/g' | \
        sed 's/&lt;/</g' | \
        sed 's/&gt;/>/g' | \
        tr '\n' ' ' | \
        sed 's/[[:space:]]\+/ /g' | \
        sed 's/^[[:space:]]*//' | \
        sed 's/[[:space:]]*$//'
    fi
}

# Function to count verses in the text
count_verses() {
    local text="$1"
    # Count occurrences of "||" which typically mark verse endings in Vedic texts
    echo "$text" | grep -o '||' | wc -l
}

# Function to extract book and hymn numbers from filename
extract_book_hymn() {
    local filename="$1"
    # Handle underscore format: rv_X_Y.html
    if [[ $filename =~ rv_([0-9]+)_([0-9]+)\.html ]]; then
        # Pattern: rv_1_2.html or rv_10_15.html
        book="${BASH_REMATCH[1]}"
        hymn="${BASH_REMATCH[2]}"
        echo "$book,$hymn"
    else
        echo "0,0"
    fi
}

# Initialize output JSON
echo "[" > "$OUTPUT_FILE"
first_entry=true

# Process HTML files
for html_file in "$INPUT_DIR"/*.html; do
    if [ -f "$html_file" ]; then
        filename=$(basename "$html_file")
        echo "Processing: $filename"
        
        # Extract book and hymn numbers
        book_hymn=$(extract_book_hymn "$filename")
        book=$(echo "$book_hymn" | cut -d',' -f1)
        hymn=$(echo "$book_hymn" | cut -d',' -f2)
        
        # Skip if we couldn't parse the filename
        if [ "$book" = "0" ] && [ "$hymn" = "0" ]; then
            echo "Warning: Could not parse book/hymn from filename: $filename"
            continue
        fi
        
        # Extract Sanskrit and romanized text
        sanskrit_text=$(extract_text_content "$html_file" "sanskrit")
        romanized_text=$(extract_text_content "$html_file" "romanized")
        
        # Count verses
        verse_count=$(count_verses "$sanskrit_text")
        
        # Generate reference
        reference="RV $book.$hymn"
        
        # Generate URL (based on the pattern seen in the project knowledge)
        # Format: rv01002.htm (2 digits for book, 3 digits for hymn)
        book_padded=$(printf "%02d" "$book")
        hymn_padded=$(printf "%03d" "$hymn")
        
        url="https://sacred-texts.com/hin/rvsan/rv${book_padded}${hymn_padded}.htm"
        
        # Add comma before entry if not first
        if [ "$first_entry" = false ]; then
            echo "," >> "$OUTPUT_FILE"
        fi
        first_entry=false
        
        # Escape quotes in text content for JSON
        sanskrit_escaped=$(echo "$sanskrit_text" | sed 's/"/\\"/g')
        romanized_escaped=$(echo "$romanized_text" | sed 's/"/\\"/g')
        
        # Write JSON entry
        {
            echo "{"
            echo "    \"book\": $book,"
            echo "    \"hymn\": $hymn,"
            echo "    \"reference\": \"$reference\","
            echo "    \"url\": \"$url\","
            echo "    \"sanskrit\": \"$sanskrit_escaped\","
            echo "    \"romanized\": \"$romanized_escaped\","
            echo "    \"verses\": $verse_count,"
            echo "    \"downloaded_at\": \"$(date -u +%Y-%m-%dT%H:%M:%S+00:00)\","
            echo "    \"status\": \"complete\""
            echo "}"
        } >> "$OUTPUT_FILE"
    fi
done

# Close JSON array
echo "" >> "$OUTPUT_FILE"
echo "]" >> "$OUTPUT_FILE"

echo "Extraction complete. Output saved to: $OUTPUT_FILE"
echo "Total files processed: $(grep -c '"book":' "$OUTPUT_FILE")"