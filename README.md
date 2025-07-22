# Adverse Media Name Matching Tool

A command-line tool for matching individual names against news articles in regulated financial contexts. The system determines whether a news article refers to a specific person for KYC/AML adverse media screening.

## Architecture & Design Decisions

### Core Components

- **Name Variants Generator** (`name_variants.py`): Generates nicknames, initials, and cultural variations using HumanName parser + LLM
- **Article Parser** (`article_parser.py`): Extracts person names using spaCy NER, regex patterns, and LLM fallback
- **Matcher** (`matcher.py`): Hybrid fuzzy matching (fuzzywuzzy) with LLM disambiguation for edge cases
- **CLI Interface** (`run.py`): Production-ready command-line tool with comprehensive output

### Key Design Decisions

**1. Hybrid Matching Approach**
- Primary: Fuzzy string matching for speed and reliability
- Fallback: LLM for complex cases (cultural variations, ambiguous matches)
- Rationale: Balances performance with accuracy for edge cases

**2. Conservative Bias for Regulatory Context**
- False negatives more costly than false positives in compliance
- Uncertain matches default to manual review recommendations
- Detailed explanations for all decisions

**3. Multi-Method Name Extraction**
- spaCy NER for accuracy, regex for coverage, LLM for robustness
- Handles various text qualities and formats
- Graceful degradation if components unavailable

**4. Tiered Confidence System**
- High confidence (>85): Auto-accept/reject
- Medium confidence (70-85): LLM disambiguation  
- Low confidence (<70): Manual review
- Provides clear risk assessment for analysts

## Installation & Setup

```bash
# Clone repository
git clone <repo-url>
cd adverse-media-matcher

# Install dependencies
pip install -r requirements.txt

# Install spaCy model (optional but recommended)
python -m spacy download en_core_web_sm

# Set up OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > .env
```

### Requirements
```
nameparser>=1.1.3
fuzzywuzzy>=0.18.0
python-levenshtein>=0.12.2
spacy>=3.4.0
langchain-openai>=0.1.0
python-dotenv>=1.0.0
```

## Usage

### Basic Command Line Usage
```bash
# Simple name matching
python run.py --name "John Smith" --filepath article.txt

# Verbose output with analysis details  
python run.py -n "Mary Johnson" -f article.txt --verbose

# JSON output for automation
python run.py --name "Alex Brown" --filepath article.txt --output json

# Save detailed report
python run.py --name "Sarah Wilson" --filepath article.txt --save-report analysis_report.txt

# These are the three examples I ran with the available data in this repo:
python run.py --name "Johnny Christopher Depp II" --filepath tests/test_data/sample_article_3.txt --save-report tests/test_reports/report_sample_article_3.txt
python run.py --name "Jannik Sinner" --filepath tests/test_data/sample_article_2.txt --save-report tests/test_reports/report_sample_article_2.txt
python run.py --name "Chloe Kelly" --filepath tests/test_data/sample_article_1.txt --save-report tests/test_reports/sample_article_1.txt 
```



### Output Interpretation
- **🟢 HIGH CONFIDENCE**: Strong algorithmic decision
- **🟡 MEDIUM/LOW CONFIDENCE**: Manual review recommended
- **🔴 MATCH FOUND**: Potential adverse media hit requiring investigation

## Testing & Evaluation

### Running Evaluations
```bash
# Run synthetic test suite
python -m tests.evaluator
```

This is the expected output:
============================================================
NAME MATCHING SYSTEM EVALUATION RESULTS
============================================================
Overall Accuracy: 85.71%
Precision: 85.71%
Recall: 100.00%
F1 Score: 92.31%

Confusion Matrix:
True Positives: 6
False Positives: 1
False Negatives: 0
True Negatives: 0

Results by Case Type:
  exact_match: 1/1 (100.00%)
  nickname: 1/1 (100.00%)
  initials: 1/1 (100.00%)
  middle_as_first: 1/1 (100.00%)
  false_positive: 0/1 (0.00%)
  hyphenated: 1/1 (100.00%)
  cultural_variation: 1/1 (100.00%)

Detailed Results:
✓ Case 1 (exact_match): 'John Smith' -> Expected: True, Predicted: True (Method: fuzzy_high_confidence)
✓ Case 2 (nickname): 'William Johnson' -> Expected: True, Predicted: True (Method: fuzzy_high_confidence)
✓ Case 3 (initials): 'Mary Elizabeth Anderson' -> Expected: True, Predicted: True (Method: fuzzy_high_confidence)
✓ Case 4 (middle_as_first): 'James Robert Wilson' -> Expected: True, Predicted: True (Method: fuzzy_high_confidence)
✗ Case 5 (false_positive): 'Michael Brown' -> Expected: False, Predicted: True (Method: fuzzy_high_confidence)
    Explanation: High confidence match (score: 88.6) between variant 'michael brown' and article name 'michelle brown'
    Article names found: ['michelle brown']
✓ Case 6 (hyphenated): 'Sarah Johnson-Smith' -> Expected: True, Predicted: True (Method: fuzzy_high_confidence)
✓ Case 7 (cultural_variation): 'José María González' -> Expected: True, Predicted: True (Method: fuzzy_high_confidence)

### Evaluation Framework
The system includes a comprehensive evaluation suite (`evaluation/evaluator.py`) testing:

- **Exact matches**: Direct name appearances
- **Nickname variations**: William/Bill, James/Jim
- **Initial usage**: Mary Elizabeth Anderson → M.E. Anderson  
- **Cultural variations**: José María González → Jose Gonzalez
- **False positives**: Michael Brown vs Michelle Brown
- **Complex cases**: Hyphenated names, middle-name-as-first

### Metrics Tracked
- **Precision/Recall/F1**: Standard classification metrics
- **Case-type breakdown**: Performance by scenario type
- **False negative rate**: Critical for regulatory compliance
- **Confidence calibration**: Alignment of confidence scores with accuracy

### Test Data Strategy
1. **Synthetic test cases**: Controlled scenarios covering edge cases
2. **Real article sampling**: Wikipedia articles with known entity mentions
3. **Manual curation**: Difficult cases identified during development
4. **Cultural diversity**: Names from different linguistic backgrounds

## Performance Considerations

**Speed Optimizations:**
- Fuzzy matching as primary filter (sub-second response)
- LLM calls only for uncertain cases (~20% of queries)
- Caching for nickname generation
- Configurable thresholds for speed/accuracy trade-offs

**Robustness Features:**
- Graceful degradation when components fail
- Input validation and sanitization
- Comprehensive error handling
- Unicode normalization for international names

## Regulatory Compliance Features

- **Audit trail**: All decisions logged with timestamps
- **Explainable AI**: Clear reasoning for every match decision
- **Conservative defaults**: Uncertain cases flag for manual review
- **Confidence scoring**: Risk-based triage for analyst workflows
- **Structured output**: JSON format for downstream integration

## Limitations & Future Improvements

**Current Limitations:**
- English-centric (though handles some cultural variations)
- Requires OpenAI API key for full functionality
- Limited context understanding beyond name matching


**Planned Enhancements:**
- Multi-language support with translation
- Contextual matching (age, occupation, location)
- Integration with additional LLM providers
- Real-time confidence calibration based on feedback
- Automated external enrichment: Plan for web-based attribute enrichment using trusted sources (Wikipedia, search APIs, LinkedIn, etc.) to disambiguate unclear matches. This would include a query generator, API retrieval layer, NER-based attribute extraction, and comparison module. Enrichment would be triggered for medium- or low-confidence matches and would be logged with full traceability.

### Enrichment Strategy (Part 2 Plan)

In some cases, key details such as middle names, date of birth, or occupation may be missing from the article but are crucial for disambiguation. To handle this, we propose an automated enrichment pipeline that performs web-based research to retrieve additional context. The strategy includes:

1. **Trigger Conditions**
   - Medium or low confidence matches
   - Lack of disambiguating metadata in article
   - Presence of known profile attributes (DOB, occupation)

2. **Data Sources**
   - Wikipedia/Wikidata APIs
   - Google/Bing Search APIs
   - LinkedIn (via APIs)
   - Public people directories and news aggregators

3. **Enrichment Modules**
   - **Query Generator**: Builds search queries from profile info
   - **API/Data Fetcher**: Collects relevant content using search and knowledge APIs
   - **Attribute Extractor**: Extracts DOB, occupation, affiliations, etc. using NER or LLMs
   - **Comparator**: Matches extracted attributes to input profile to assess match likelihood

4. **Explainability**
   - All enrichment attempts logged with sources and decision reasoning
   - Used to upgrade or downgrade match confidence with clear justifications

5. **Fallback**
   - If enrichment fails or yields ambiguous data, case is flagged for manual review with enrichment log attached

This enrichment plan is designed to integrate with the existing confidence tiering system and further reduce false positives while maintaining high regulatory compliance standards.

## Project Structure
```
adverse-media-matcher/
├── matcher/
│   ├── name_variants.py      # Name variation generation
│   ├── article_parser.py     # Name extraction from articles
│   └── matcher.py           # Core matching logic
├── evaluation/
│   └── evaluator.py         # Comprehensive test framework
├── tests/
│   └── test_data/           # Sample articles for testing
├── run.py                   # Main CLI interface
├── requirements.txt         # Dependencies
└── README.md               # This file
```

---

*This tool prioritizes regulatory compliance and explainability while maintaining practical performance for production KYC/AML workflows.*
