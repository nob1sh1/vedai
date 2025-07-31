#!/bin/bash

# Rig Veda Corpus Reprocessor
# Fixes the rigveda_complete_corpus.json by properly extracting Sanskrit and romanized text
# from the already downloaded HTML files

set -e  # Exit on any error

# Configuration
RAW_DIR="data/rigveda_corpus/raw_html"
OUTPUT_FILE="data/rigveda_complete_corpus_fixed.json"
BACKUP_FILE="data/rigveda_complete_corpus_backup.json"
LOG_FILE="data/rigveda_reprocess.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Initialize log
echo "=== RIG VEDA REPROCESSING SESSION: $(date) ===" > "$LOG_FILE"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

echo -e "${PURPLE}"
echo "🔧 ========================================== 🔧"
echo "     RIG VEDA CORPUS REPROCESSOR"
echo "     Fixing extraction from existing HTML files"
echo "🔧 ========================================== 🔧"
echo -e "${NC}"

# Check if raw HTML directory exists
if [ ! -d "$RAW_DIR" ]; then
    echo -e "${RED}❌ Error: Raw HTML directory not found at $RAW_DIR${NC}"
    echo "Please ensure the original download script was run first."
    exit 1
fi

# Backup original corpus file if it exists
if [ -f "data/rigveda_complete_corpus.json" ]; then
    cp "data/rigveda_complete_corpus.json" "$BACKUP_FILE"
    log "Backed up original corpus to $BACKUP_FILE"
fi

# Rig Veda structure: [book] = number_of_hymns
declare -A BOOK_HYMNS=(
    [1]=191 [2]=43 [3]=62 [4]=58 [5]=87
    [6]=75 [7]=104 [8]=103 [9]=114 [10]=191
)

# Calculate total hymns
total_hymns=0
for book in {1..10}; do
    total_hymns=$((total_hymns + BOOK_HYMNS[$book]))
done

log "Starting reprocessing of $total_hymns HTML files"

# Progress bar function
show_progress() {
    local current=$1
    local total=$2
    local book=$3
    local hymn=$4
    local percent=$((current * 100 / total))
    local filled=$((percent / 2))
    local empty=$((50 - filled))
    
    printf "\r${WHITE}Book $book.%03d ${BLUE}[" $hymn
    printf "%*s" $filled | tr ' ' '='
    printf "%*s" $empty | tr ' ' '-'
    printf "] ${YELLOW}%d%% ${GREEN}(%d/%d)${NC}" $percent $current $total
}

# Function to extract Sanskrit and romanization from HTML
extract_hymn_content() {
    local html_file=$1
    local book=$2
    local hymn=$3
    
    if [ ! -f "$html_file" ]; then
        echo "null"
        return
    fi
    
    # Extract content between the H3 header and the first <P><HR> separator
    local content=$(sed -n "/<H3 ALIGN=\"CENTER\">Rig Veda Book $book Hymn $hymn<\/H3>/,/<P><HR>/p" "$html_file")
    
    # Extract Sanskrit text (Devanagari) - lines that contain Devanagari characters followed by <BR>
    local sanskrit_lines=$(echo "$content" | grep -E '[अ-ॿ].*<BR>' | sed 's/<BR>//g' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
    local sanskrit=$(echo "$sanskrit_lines" | tr '\n' ' ' | sed 's/  */ /g' | sed 's/^ *//' | sed 's/ *$//')
    
    # Extract romanized lines - lines that come after Sanskrit and contain Latin with diacriticals
    # Look for lines with romanized characters followed by <BR>
    local romanized_lines=$(echo "$content" | grep -E '[a-zA-Zāīūṛḷēōṃḥńśṣṭḍṇṅñṇḻḥ].*<BR>' | grep -v '[अ-ॿ]' | sed 's/<BR>//g' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
    local romanized=$(echo "$romanized_lines" | tr '\n' ' ' | sed 's/  */ /g' | sed 's/^ *//' | sed 's/ *$//')
    
    # Count verses by counting || markers in Sanskrit text
    local verse_count=$(echo "$sanskrit" | grep -o '||' | wc -l)
    
    # If we got empty results, try alternative extraction method
    if [ -z "$sanskrit" ] || [ -z "$romanized" ]; then
        # Alternative: extract everything between H3 and <P></P>, then separate
        local all_content=$(sed -n "/<H3 ALIGN=\"CENTER\">Rig Veda Book $book Hymn $hymn<\/H3>/,/<P><\/P>/p" "$html_file")
        
        # Try to extract Sanskrit (any line with Devanagari)
        if [ -z "$sanskrit" ]; then
            sanskrit=$(echo "$all_content" | grep -E '[अ-ॿ]' | sed 's/<[^>]*>//g' | tr '\n' ' ' | sed 's/  */ /g' | sed 's/^ *//' | sed 's/ *$//')
        fi
        
        # Try to extract romanized (lines with Latin characters but no Devanagari)
        if [ -z "$romanized" ]; then
            romanized=$(echo "$all_content" | grep -E '[a-zA-Zāīūṛḷēōṃḥńśṣṭḍṇṅñṇḻḥ]' | grep -v '[अ-ॿ]' | grep -v '<' | grep -v 'Next:' | grep -v 'Previous' | head -20 | tr '\n' ' ' | sed 's/  */ /g' | sed 's/^ *//' | sed 's/ *$//')
        fi
        
        # Recount verses
        verse_count=$(echo "$sanskrit" | grep -o '||' | wc -l)
    fi
    
    # Clean up extracted text
    sanskrit=$(echo "$sanskrit" | sed 's/||/ || /g' | sed 's/|/ | /g' | sed 's/  */ /g')
    romanized=$(echo "$romanized" | sed 's/||/ || /g' | sed 's/|/ | /g' | sed 's/  */ /g')
    
    # Determine status
    local status="complete"
    if [ -z "$sanskrit" ] && [ -z "$romanized" ]; then
        status="failed"
    elif [ -z "$sanskrit" ] || [ -z "$romanized" ]; then
        status="partial"
    fi
    
    # Create JSON object with proper escaping
    cat << EOF
{
    "book": $book,
    "hymn": $hymn,
    "reference": "RV $book.$hymn",
    "url": "https://sacred-texts.com/hin/rvsan/rv$(printf "%02d%03d" $book $hymn).htm",
    "sanskrit": "$(echo "$sanskrit" | sed 's/"/\\"/g' | sed "s/'/\\'/g")",
    "romanized": "$(echo "$romanized" | sed 's/"/\\"/g' | sed "s/'/\\'/g")",
    "verses": $verse_count,
    "downloaded_at": "$(date -Iseconds)",
    "status": "$status"
}
EOF
}

# Main reprocessing
echo -e "${GREEN}🚀 Starting reprocessing...${NC}"
echo ""

# Initialize JSON output
echo "[" > "$OUTPUT_FILE"

current_count=0
successful_extractions=0
partial_extractions=0
failed_extractions=0
first_entry=true

# Process all books and hymns
for book in {1..10}; do
    hymn_count=${BOOK_HYMNS[$book]}
    log "Reprocessing Book $book ($hymn_count hymns)"
    
    for hymn in $(seq 1 $hymn_count); do
        current_count=$((current_count + 1))
        show_progress $current_count $total_hymns $book $hymn
        
        # Add comma separator (except for first entry)
        if [ "$first_entry" = false ]; then
            echo "," >> "$OUTPUT_FILE"
        fi
        first_entry=false
        
        # Process HTML file
        html_file="$RAW_DIR/rv_${book}_${hymn}.html"
        entry_json=$(extract_hymn_content "$html_file" $book $hymn)
        
        # Count extraction results
        status=$(echo "$entry_json" | grep '"status"' | sed 's/.*"status": "\([^"]*\)".*/\1/')
        case "$status" in
            "complete") successful_extractions=$((successful_extractions + 1)) ;;
            "partial") partial_extractions=$((partial_extractions + 1)) ;;
            *) failed_extractions=$((failed_extractions + 1)) ;;
        esac
        
        # Add to corpus
        echo "$entry_json" >> "$OUTPUT_FILE"
    done
    
    echo ""  # New line after progress bar
    log "Completed Book $book reprocessing"
done

# Close JSON array
echo "]" >> "$OUTPUT_FILE"

# Final statistics
echo ""
echo -e "${GREEN}✅ ========================================== ✅${NC}"
echo -e "${GREEN}         REPROCESSING COMPLETE!${NC}"
echo -e "${GREEN}✅ ========================================== ✅${NC}"
echo ""
echo -e "${WHITE}📊 EXTRACTION STATISTICS:${NC}"
echo -e "   🎯 Total hymns processed: ${CYAN}$total_hymns${NC}"
echo -e "   ✅ Complete extractions: ${GREEN}$successful_extractions${NC}"
echo -e "   ⚠️  Partial extractions: ${YELLOW}$partial_extractions${NC}"
echo -e "   ❌ Failed extractions: ${RED}$failed_extractions${NC}"
echo -e "   📈 Success rate: ${YELLOW}$(((successful_extractions + partial_extractions) * 100 / total_hymns))%${NC}"
echo ""
echo -e "${WHITE}📁 OUTPUT FILES:${NC}"
echo -e "   📋 Fixed corpus: ${BLUE}$OUTPUT_FILE${NC}"
echo -e "   💾 Backup of original: ${BLUE}$BACKUP_FILE${NC}"
echo -e "   📜 Processing log: ${BLUE}$LOG_FILE${NC}"
echo ""

# Validate JSON structure
if command -v python3 &> /dev/null; then
    python3 << EOF
import json
import sys

try:
    with open('$OUTPUT_FILE', 'r', encoding='utf-8') as f:
        corpus = json.load(f)
    
    print("${WHITE}📈 CORPUS VALIDATION:${NC}")
    print(f"   ✅ Valid JSON structure: ${GREEN}Yes${NC}")
    print(f"   📚 Total entries: ${CYAN}{len(corpus)}${NC}")
    
    # Count by status
    complete = sum(1 for entry in corpus if entry.get('status') == 'complete')
    partial = sum(1 for entry in corpus if entry.get('status') == 'partial')
    failed = sum(1 for entry in corpus if entry.get('status') == 'failed')
    
    print(f"   ✅ Complete entries: ${GREEN}{complete}${NC}")
    print(f"   ⚠️  Partial entries: ${YELLOW}{partial}${NC}")
    print(f"   ❌ Failed entries: ${RED}{failed}${NC}")
    
    # Sample some entries with content
    entries_with_content = [e for e in corpus if e.get('sanskrit') and len(e['sanskrit'].strip()) > 0]
    if entries_with_content:
        sample = entries_with_content[0]
        print(f"   📝 Sample extraction (RV {sample['book']}.{sample['hymn']}):")
        print(f"      Sanskrit: {sample['sanskrit'][:100]}...")
        print(f"      Romanized: {sample['romanized'][:100]}...")
        print(f"      Verses: {sample['verses']}")
    
    # Calculate total verses
    total_verses = sum(entry.get('verses', 0) for entry in corpus)
    print(f"   📝 Total verses extracted: ${CYAN}{total_verses}${NC}")
    
    # File size
    import os
    file_size = os.path.getsize('$OUTPUT_FILE') / (1024 * 1024)
    print(f"   💾 File size: ${CYAN}{file_size:.2f} MB${NC}")
    
except json.JSONDecodeError as e:
    print(f"${RED}❌ JSON validation failed: {e}${NC}")
    sys.exit(1)
except Exception as e:
    print(f"${RED}❌ Validation error: {e}${NC}")
    sys.exit(1)
EOF
else
    echo -e "${YELLOW}⚠️  Python3 not available - skipping JSON validation${NC}"
fi

echo ""
echo -e "${PURPLE}🕉️  FIXED CORPUS READY FOR USE! 🕉️${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo -e "1. Review the extraction quality in $OUTPUT_FILE"
echo -e "2. Compare with original file (backup at $BACKUP_FILE)"
echo -e "3. Load the fixed corpus into your Wisdom AI system"
echo ""
echo -e "${YELLOW}Test the corpus:${NC}"
echo -e "   python3 -c \"import json; c=json.load(open('$OUTPUT_FILE')); print(f'Loaded {len(c)} hymns, {sum(e.get(\\\"verses\\\",0) for e in c)} verses')\""
echo ""

log "Reprocessing completed successfully"
log "Fixed corpus saved to: $OUTPUT_FILE"
log "Complete extractions: $successful_extractions"
log "Partial extractions: $partial_extractions"
log "Failed extractions: $failed_extractions"

echo -e "${GREEN}🙏 Ancient wisdom, now properly extracted! 🙏${NC}"