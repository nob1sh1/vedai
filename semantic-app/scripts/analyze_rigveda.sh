#!/bin/bash

# Rigveda Corpus Analysis Script
# Analyzes rigveda_complete_corpus.json and rigveda_extracted.json files
# Counts total books, hymns per book, and verifies content presence

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Files to analyze
COMPLETE_CORPUS="data/rigveda_complete_corpus.json"
EXTRACTED_FILE="rigveda_extracted.json"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Rigveda Corpus Analysis Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# Function to check if jq is installed
check_jq() {
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}Error: jq is not installed. Please install jq first.${NC}"
        echo "On Ubuntu/Debian: sudo apt-get install jq"
        echo "On macOS: brew install jq"
        exit 1
    fi
}

# Function to check if file exists
check_file() {
    local file=$1
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}Error: File '$file' not found in current directory.${NC}"
        return 1
    fi
    echo -e "${GREEN}✓${NC} Found: $file"
    return 0
}

# Function to validate JSON format
validate_json() {
    local file=$1
    if ! jq empty "$file" 2>/dev/null; then
        echo -e "${RED}Error: '$file' is not valid JSON.${NC}"
        return 1
    fi
    echo -e "${GREEN}✓${NC} Valid JSON: $file"
    return 0
}

# Function to analyze complete corpus
analyze_complete_corpus() {
    echo -e "\n${YELLOW}=== Analyzing Complete Corpus ===${NC}"
    
    # Count total entries
    local total_entries=$(jq 'length' "$COMPLETE_CORPUS")
    echo "Total entries in complete corpus: $total_entries"
    
    # Count books and hymns per book
    echo -e "\n${BLUE}Books and Hymns per Book:${NC}"
    jq -r '
        group_by(.book) | 
        map({
            book: .[0].book, 
            hymn_count: length,
            hymn_range: "\(map(.hymn) | min)-\(map(.hymn) | max)"
        }) | 
        .[] | 
        "Book \(.book): \(.hymn_count) hymns (range: \(.hymn_range))"
    ' "$COMPLETE_CORPUS"
    
    # Summary statistics
    echo -e "\n${BLUE}Summary Statistics:${NC}"
    local total_books=$(jq '[.[].book] | unique | length' "$COMPLETE_CORPUS")
    local total_hymns=$(jq 'length' "$COMPLETE_CORPUS")
    echo "Total Books: $total_books"
    echo "Total Hymns: $total_hymns"
    
    # Check status distribution
    echo -e "\n${BLUE}Status Distribution:${NC}"
    jq -r 'group_by(.status) | map({status: .[0].status, count: length}) | .[] | "\(.status): \(.count)"' "$COMPLETE_CORPUS"
    
    # Check for entries with content
    echo -e "\n${BLUE}Content Analysis:${NC}"
    local with_sanskrit=$(jq '[.[] | select(.sanskrit != "")] | length' "$COMPLETE_CORPUS")
    local with_romanized=$(jq '[.[] | select(.romanized != "")] | length' "$COMPLETE_CORPUS")
    local with_verses=$(jq '[.[] | select(.verses > 0)] | length' "$COMPLETE_CORPUS")
    
    echo "Entries with Sanskrit content: $with_sanskrit"
    echo "Entries with Romanized content: $with_romanized"
    echo "Entries with verse count > 0: $with_verses"
    
    # Check for empty content
    local empty_sanskrit=$(jq '[.[] | select(.sanskrit == "")] | length' "$COMPLETE_CORPUS")
    local empty_romanized=$(jq '[.[] | select(.romanized == "")] | length' "$COMPLETE_CORPUS")
    local zero_verses=$(jq '[.[] | select(.verses == 0)] | length' "$COMPLETE_CORPUS")
    
    if [[ $empty_sanskrit -gt 0 || $empty_romanized -gt 0 || $zero_verses -gt 0 ]]; then
        echo -e "\n${YELLOW}⚠ Warning: Found entries with missing content:${NC}"
        echo "Empty Sanskrit fields: $empty_sanskrit"
        echo "Empty Romanized fields: $empty_romanized"
        echo "Zero verse counts: $zero_verses"
    fi
}

# Function to analyze extracted corpus
analyze_extracted_corpus() {
    echo -e "\n${YELLOW}=== Analyzing Extracted Corpus ===${NC}"
    
    # Check if file has expected structure
    local first_entry=$(jq '.[0]' "$EXTRACTED_FILE" 2>/dev/null)
    if [[ "$first_entry" == "null" ]]; then
        echo -e "${RED}Error: Extracted file appears to be empty or has unexpected structure.${NC}"
        return 1
    fi
    
    # Count total entries
    local total_entries=$(jq 'length' "$EXTRACTED_FILE")
    echo "Total entries in extracted corpus: $total_entries"
    
    # Check if it has the same structure as complete corpus
    local has_book=$(jq '.[0] | has("book")' "$EXTRACTED_FILE" 2>/dev/null)
    local has_hymn=$(jq '.[0] | has("hymn")' "$EXTRACTED_FILE" 2>/dev/null)
    local has_sanskrit=$(jq '.[0] | has("sanskrit")' "$EXTRACTED_FILE" 2>/dev/null)
    local has_romanized=$(jq '.[0] | has("romanized")' "$EXTRACTED_FILE" 2>/dev/null)
    
    echo -e "\n${BLUE}Structure Check:${NC}"
    echo "Has 'book' field: $has_book"
    echo "Has 'hymn' field: $has_hymn"
    echo "Has 'sanskrit' field: $has_sanskrit"
    echo "Has 'romanized' field: $has_romanized"
    
    if [[ "$has_book" == "true" && "$has_hymn" == "true" ]]; then
        # Count books and hymns per book
        echo -e "\n${BLUE}Books and Hymns per Book (Extracted):${NC}"
        jq -r '
            group_by(.book) | 
            map({
                book: .[0].book, 
                hymn_count: length,
                hymn_range: "\(map(.hymn) | min)-\(map(.hymn) | max)"
            }) | 
            .[] | 
            "Book \(.book): \(.hymn_count) hymns (range: \(.hymn_range))"
        ' "$EXTRACTED_FILE"
        
        # Summary statistics
        echo -e "\n${BLUE}Summary Statistics (Extracted):${NC}"
        local total_books=$(jq '[.[].book] | unique | length' "$EXTRACTED_FILE")
        local total_hymns=$(jq 'length' "$EXTRACTED_FILE")
        echo "Total Books: $total_books"
        echo "Total Hymns: $total_hymns"
    fi
    
    if [[ "$has_sanskrit" == "true" && "$has_romanized" == "true" ]]; then
        # Check content presence
        echo -e "\n${BLUE}Content Analysis (Extracted):${NC}"
        local with_sanskrit=$(jq '[.[] | select(.sanskrit != "" and .sanskrit != null)] | length' "$EXTRACTED_FILE")
        local with_romanized=$(jq '[.[] | select(.romanized != "" and .romanized != null)] | length' "$EXTRACTED_FILE")
        
        echo "Entries with Sanskrit content: $with_sanskrit"
        echo "Entries with Romanized content: $with_romanized"
        
        # Calculate percentages
        if [[ $total_entries -gt 0 ]]; then
            local sanskrit_percent=$(echo "scale=2; $with_sanskrit * 100 / $total_entries" | bc -l 2>/dev/null || echo "N/A")
            local romanized_percent=$(echo "scale=2; $with_romanized * 100 / $total_entries" | bc -l 2>/dev/null || echo "N/A")
            echo "Sanskrit coverage: ${sanskrit_percent}%"
            echo "Romanized coverage: ${romanized_percent}%"
        fi
    fi
}

# Function to compare both files
compare_files() {
    echo -e "\n${YELLOW}=== Cross-File Comparison ===${NC}"
    
    local complete_total=$(jq 'length' "$COMPLETE_CORPUS")
    local extracted_total=$(jq 'length' "$EXTRACTED_FILE")
    
    echo "Complete corpus entries: $complete_total"
    echo "Extracted corpus entries: $extracted_total"
    
    if [[ $extracted_total -eq $complete_total ]]; then
        echo -e "${GREEN}✓${NC} Entry counts match!"
    elif [[ $extracted_total -lt $complete_total ]]; then
        echo -e "${YELLOW}⚠${NC} Extracted corpus has fewer entries (missing: $((complete_total - extracted_total)))"
    else
        echo -e "${YELLOW}⚠${NC} Extracted corpus has more entries (extra: $((extracted_total - complete_total)))"
    fi
    
    # Check if both have book/hymn structure
    local complete_has_book=$(jq '.[0] | has("book")' "$COMPLETE_CORPUS" 2>/dev/null)
    local extracted_has_book=$(jq '.[0] | has("book")' "$EXTRACTED_FILE" 2>/dev/null)
    
    if [[ "$complete_has_book" == "true" && "$extracted_has_book" == "true" ]]; then
        # Find missing entries by comparing book/hymn combinations
        echo -e "\n${BLUE}Finding missing or extra entries...${NC}"
        
        # Create temporary files for comparison
        jq -r '.[] | "\(.book).\(.hymn)"' "$COMPLETE_CORPUS" | sort > /tmp/complete_refs.txt
        jq -r '.[] | "\(.book).\(.hymn)"' "$EXTRACTED_FILE" | sort > /tmp/extracted_refs.txt
        
        # Find differences
        local missing_count=$(comm -23 /tmp/complete_refs.txt /tmp/extracted_refs.txt | wc -l)
        local extra_count=$(comm -13 /tmp/complete_refs.txt /tmp/extracted_refs.txt | wc -l)
        
        if [[ $missing_count -eq 0 && $extra_count -eq 0 ]]; then
            echo -e "${GREEN}✓${NC} All hymn references match between files!"
        else
            if [[ $missing_count -gt 0 ]]; then
                echo -e "${YELLOW}Missing from extracted file ($missing_count entries):${NC}"
                comm -23 /tmp/complete_refs.txt /tmp/extracted_refs.txt | head -10
                [[ $missing_count -gt 10 ]] && echo "... and $((missing_count - 10)) more"
            fi
            
            if [[ $extra_count -gt 0 ]]; then
                echo -e "${YELLOW}Extra in extracted file ($extra_count entries):${NC}"
                comm -13 /tmp/complete_refs.txt /tmp/extracted_refs.txt | head -10
                [[ $extra_count -gt 10 ]] && echo "... and $((extra_count - 10)) more"
            fi
        fi
        
        # Clean up temp files
        rm -f /tmp/complete_refs.txt /tmp/extracted_refs.txt
    fi
}

# Function to generate summary report
generate_summary() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}             SUMMARY REPORT${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    local complete_total=$(jq 'length' "$COMPLETE_CORPUS")
    local complete_books=$(jq '[.[].book] | unique | length' "$COMPLETE_CORPUS")
    local complete_sanskrit=$(jq '[.[] | select(.sanskrit != "")] | length' "$COMPLETE_CORPUS")
    local complete_romanized=$(jq '[.[] | select(.romanized != "")] | length' "$COMPLETE_CORPUS")
    
    echo "Complete Corpus:"
    echo "  - Books: $complete_books"
    echo "  - Total Hymns: $complete_total"
    echo "  - With Sanskrit: $complete_sanskrit"
    echo "  - With Romanized: $complete_romanized"
    
    if [[ -f "$EXTRACTED_FILE" ]]; then
        local extracted_total=$(jq 'length' "$EXTRACTED_FILE")
        local extracted_books=$(jq '[.[].book] | unique | length' "$EXTRACTED_FILE" 2>/dev/null || echo "N/A")
        local extracted_sanskrit=$(jq '[.[] | select(.sanskrit != "" and .sanskrit != null)] | length' "$EXTRACTED_FILE" 2>/dev/null || echo "N/A")
        local extracted_romanized=$(jq '[.[] | select(.romanized != "" and .romanized != null)] | length' "$EXTRACTED_FILE" 2>/dev/null || echo "N/A")
        
        echo ""
        echo "Extracted Corpus:"
        echo "  - Books: $extracted_books"
        echo "  - Total Hymns: $extracted_total"
        echo "  - With Sanskrit: $extracted_sanskrit"
        echo "  - With Romanized: $extracted_romanized"
    fi
    
    echo -e "\n${GREEN}Analysis complete!${NC}"
}

# Main execution
main() {
    echo "Checking prerequisites..."
    check_jq
    
    echo -e "\nChecking files..."
    if ! check_file "$COMPLETE_CORPUS"; then
        exit 1
    fi
    
    if ! validate_json "$COMPLETE_CORPUS"; then
        exit 1
    fi
    
    # Analyze complete corpus
    analyze_complete_corpus
    
    # Check if extracted file exists and analyze it
    if check_file "$EXTRACTED_FILE" 2>/dev/null; then
        if validate_json "$EXTRACTED_FILE"; then
            analyze_extracted_corpus
            compare_files
        else
            echo -e "${YELLOW}Skipping extracted file analysis due to JSON validation error.${NC}"
        fi
    else
        echo -e "\n${YELLOW}Note: rigveda_extracted.json not found. Skipping extracted corpus analysis.${NC}"
    fi
    
    # Generate summary
    generate_summary
}

# Run the script
main "$@"