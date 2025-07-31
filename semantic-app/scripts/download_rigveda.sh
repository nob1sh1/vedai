#!/bin/bash

# Complete Rig Veda Corpus Downloader
# Downloads all 1,028 hymns from sacred-texts.com in Sanskrit + Romanization
# Creates a structured corpus for the Wisdom AI system

set -e  # Exit on any error

# Configuration
BASE_URL="https://sacred-texts.com/hin/rvsan"
OUTPUT_DIR="data/rigveda_corpus"
RAW_DIR="$OUTPUT_DIR/raw_html"
PROCESSED_FILE="data/rigveda_complete_corpus.json" 
LOG_FILE="data/rigveda_download.log"
DELAY_SECONDS=1  # Respectful delay between requests
MAX_RETRIES=3

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Create directories
mkdir -p "$RAW_DIR"
mkdir -p "data"

# Initialize log
echo "=== RIG VEDA DOWNLOAD SESSION: $(date) ===" > "$LOG_FILE"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

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

echo -e "${PURPLE}"
echo "🕉️  ========================================== 🕉️"
echo "   COMPLETE RIG VEDA CORPUS DOWNLOADER"
echo "   Sanskrit + Romanization from sacred-texts.com"
echo "🕉️  ========================================== 🕉️"
echo -e "${NC}"
echo ""
echo -e "${CYAN}📚 Target: Complete Rig Veda (10 books, ~1,028 hymns)${NC}"
echo -e "${CYAN}🌐 Source: sacred-texts.com${NC}"
echo -e "${CYAN}📁 Output: $OUTPUT_DIR${NC}"
echo -e "${CYAN}⏱️  Delay: $DELAY_SECONDS seconds between requests${NC}"
echo ""

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

log "Starting download of $total_hymns hymns across 10 books"

# Function to download and parse a single hymn
download_hymn() {
    local book=$1
    local hymn=$2
    local url="$BASE_URL/rv$(printf "%02d%03d" $book $hymn).htm"
    local html_file="$RAW_DIR/rv_${book}_${hymn}.html"
    local retry_count=0
    
    # Download with retries
    while [ $retry_count -lt $MAX_RETRIES ]; do
        if curl -s -L --max-time 30 --user-agent "Mozilla/5.0 (compatible; RigVedaBot/1.0)" \
               "$url" -o "$html_file" 2>/dev/null; then
            
            # Verify we got valid content
            if [ -s "$html_file" ] && grep -q "Rig Veda Book $book Hymn $hymn" "$html_file" 2>/dev/null; then
                return 0  # Success
            fi
        fi
        
        retry_count=$((retry_count + 1))
        [ $retry_count -lt $MAX_RETRIES ] && sleep $((retry_count * 2))
    done
    
    # Clean up failed download
    [ -f "$html_file" ] && rm "$html_file"
    return 1  # Failed
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
    
    # Extract the main content between the title and "Next:" link
    local content=$(sed -n "/Rig Veda Book $book Hymn $hymn/,/Next:/p" "$html_file")
    
    # Extract Sanskrit (Devanagari text)
    local sanskrit=$(echo "$content" | grep -o '[अ-ॿ][^|]*' | head -20 | tr '\n' ' ' | sed 's/|//g' | sed 's/  */ /g' | xargs)
    
    # Extract romanization (lines with Latin characters and diacriticals)
    local romanized=$(echo "$content" | grep -E '[a-zA-Zāīūṛḷēōṃḥńśṣṭḍṇ]' | \
                     grep -v '<' | grep -v 'Previous' | grep -v 'Next' | \
                     head -10 | tr '\n' ' ' | sed 's/  */ /g' | xargs)
    
    # Clean up the extracted text
    sanskrit=$(echo "$sanskrit" | sed 's/||/ || /g' | sed 's/|/ | /g')
    romanized=$(echo "$romanized" | sed 's/||/ || /g' | sed 's/|/ | /g')
    
    # Create JSON object
    cat << EOF
{
    "book": $book,
    "hymn": $hymn,
    "reference": "RV $book.$hymn",
    "url": "$BASE_URL/rv$(printf "%02d%03d" $book $hymn).htm",
    "sanskrit": "$(echo "$sanskrit" | sed 's/"/\\"/g')",
    "romanized": "$(echo "$romanized" | sed 's/"/\\"/g')",
    "verses": $(echo "$sanskrit" | grep -o '||' | wc -l),
    "downloaded_at": "$(date -Iseconds)",
    "status": "complete"
}
EOF
}

# Function to create a placeholder for failed downloads
create_placeholder() {
    local book=$1
    local hymn=$2
    
    cat << EOF
{
    "book": $book,
    "hymn": $hymn,
    "reference": "RV $book.$hymn",
    "url": "$BASE_URL/rv$(printf "%02d%03d" $book $hymn).htm",
    "sanskrit": "",
    "romanized": "",
    "verses": 0,
    "downloaded_at": "$(date -Iseconds)",
    "status": "failed",
    "error": "Download failed after $MAX_RETRIES attempts"
}
EOF
}

# Main download process
echo -e "${GREEN}🚀 Starting download process...${NC}"
echo ""

# Initialize JSON output
echo "[" > "$PROCESSED_FILE"

current_count=0
successful_downloads=0
failed_downloads=0
first_entry=true

# Download all books and hymns
for book in {1..10}; do
    hymn_count=${BOOK_HYMNS[$book]}
    log "Processing Book $book ($hymn_count hymns)"
    
    for hymn in $(seq 1 $hymn_count); do
        current_count=$((current_count + 1))
        show_progress $current_count $total_hymns $book $hymn
        
        # Add comma separator (except for first entry)
        if [ "$first_entry" = false ]; then
            echo "," >> "$PROCESSED_FILE"
        fi
        first_entry=false
        
        # Download and process hymn
        if download_hymn $book $hymn; then
            # Extract content and add to corpus
            html_file="$RAW_DIR/rv_${book}_${hymn}.html"
            extract_hymn_content "$html_file" $book $hymn >> "$PROCESSED_FILE"
            successful_downloads=$((successful_downloads + 1))
        else
            # Add placeholder for failed download
            create_placeholder $book $hymn >> "$PROCESSED_FILE"
            failed_downloads=$((failed_downloads + 1))
            log "Failed to download RV $book.$hymn after $MAX_RETRIES attempts"
        fi
        
        # Respectful delay
        sleep $DELAY_SECONDS
    done
    
    echo ""  # New line after progress bar
    log "Completed Book $book: $((hymn_count - failed_downloads)) hymns downloaded successfully"
done

# Close JSON array
echo "]" >> "$PROCESSED_FILE"

# Final statistics and summary
echo ""
echo -e "${GREEN}✅ ========================================== ✅${NC}"
echo -e "${GREEN}           DOWNLOAD COMPLETE!${NC}"
echo -e "${GREEN}✅ ========================================== ✅${NC}"
echo ""
echo -e "${WHITE}📊 FINAL STATISTICS:${NC}"
echo -e "   🎯 Total hymns targeted: ${CYAN}$total_hymns${NC}"
echo -e "   ✅ Successful downloads: ${GREEN}$successful_downloads${NC}"
echo -e "   ❌ Failed downloads: ${RED}$failed_downloads${NC}"
echo -e "   📈 Success rate: ${YELLOW}$((successful_downloads * 100 / total_hymns))%${NC}"
echo ""
echo -e "${WHITE}📁 OUTPUT FILES:${NC}"
echo -e "   📋 Main corpus: ${BLUE}$PROCESSED_FILE${NC}"
echo -e "   📂 Raw HTML files: ${BLUE}$RAW_DIR${NC}"
echo -e "   📜 Download log: ${BLUE}$LOG_FILE${NC}"
echo ""

# Create corpus statistics
python3 << EOF
import json
import sys

try:
    with open('$PROCESSED_FILE', 'r', encoding='utf-8') as f:
        corpus = json.load(f)
    
    print("${WHITE}📈 CORPUS ANALYSIS:${NC}")
    print(f"   📚 Total entries: ${CYAN}{len(corpus)}${NC}")
    
    # Count verses
    total_verses = sum(entry.get('verses', 0) for entry in corpus if entry.get('status') == 'complete')
    print(f"   📝 Total verses: ${CYAN}{total_verses}${NC}")
    
    # Count by book
    book_stats = {}
    for entry in corpus:
        book = entry['book']
        if book not in book_stats:
            book_stats[book] = {'hymns': 0, 'verses': 0}
        book_stats[book]['hymns'] += 1
        book_stats[book]['verses'] += entry.get('verses', 0)
    
    print(f"   📖 Book breakdown:")
    for book in sorted(book_stats.keys()):
        stats = book_stats[book]
        print(f"      Book {book}: {stats['hymns']} hymns, {stats['verses']} verses")
    
    # Calculate file size
    import os
    file_size = os.path.getsize('$PROCESSED_FILE') / (1024 * 1024)
    print(f"   💾 Corpus file size: ${CYAN}{file_size:.2f} MB${NC}")
    
except Exception as e:
    print(f"Error analyzing corpus: {e}")
EOF

echo ""
echo -e "${PURPLE}🕉️  CORPUS READY FOR WISDOM AI! 🕉️${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo -e "1. Load this corpus into your Wisdom AI system"
echo -e "2. Process the Sanskrit text with your semantic analyzer"
echo -e "3. Create embeddings from the romanized text"
echo -e "4. Build knowledge graphs from the hymn relationships"
echo ""
echo -e "${YELLOW}Example usage:${NC}"
echo -e "   python3 -c \"import json; corpus=json.load(open('$PROCESSED_FILE')); print(f'Loaded {len(corpus)} hymns')\""
echo ""

log "Download session completed successfully"
log "Corpus saved to: $PROCESSED_FILE"
log "Total entries: $((successful_downloads + failed_downloads))"
log "Success rate: $((successful_downloads * 100 / total_hymns))%"

echo -e "${GREEN}🙏 May this ancient wisdom serve all beings! 🙏${NC}"