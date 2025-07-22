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
```

### Output Interpretation
- **🟢 HIGH CONFIDENCE**: Strong algorithmic decision
- **🟡 MEDIUM/LOW CONFIDENCE**: Manual review recommended
- **🔴 MATCH FOUND**: Potential adverse media hit requiring investigation

## Testing & Evaluation

### Running Evaluations
```bash
# Run synthetic test suite
python evaluation/evaluator.py
```

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