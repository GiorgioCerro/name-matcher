#!/usr/bin/env python3
"""
Adverse Media Name Matching Tool

A command-line tool for matching individual names against news articles
for regulatory compliance and adverse media screening.

Usage:
    python run.py --name "John Smith" --filepath article.txt
    python run.py -n "Mary Johnson" -f article.txt --verbose
    python run.py --name "Alex Brown" --filepath article.txt --output json
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any

# Import our matcher modules
try:
    from matcher.name_variants import generate_name_variants
    from matcher.article_parser import extract_person_names
    from matcher.matcher import match_name_against_article
except ImportError as e:
    print(f"Error importing matcher modules: {e}")
    print("Make sure the matcher package is in your Python path")
    sys.exit(1)


class NameMatchingCLI:
    """Command-line interface for the name matching system."""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description="Match individual names against news articles for adverse media screening",
            epilog="Example: python run.py --name 'John Smith' --filepath article.txt",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            "--name", "-n",
            required=True,
            help="Full name of the individual to search for (e.g., 'John Smith')"
        )
        
        parser.add_argument(
            "--filepath", "-f",
            required=True,
            help="Path to the text file containing the news article"
        )
        
        parser.add_argument(
            "--output", "-o",
            choices=["text", "json"],
            default="text",
            help="Output format: 'text' for human-readable or 'json' for machine-readable (default: text)"
        )
        
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Show detailed information including name variants and extracted names"
        )
        
        parser.add_argument(
            "--threshold",
            type=float,
            default=85.0,
            help="Fuzzy matching threshold (0-100, default: 85.0)"
        )
        
        parser.add_argument(
            "--save-report",
            help="Save detailed report to specified file path"
        )
        
        return parser
    
    def load_article(self, filepath: str) -> str:
        """Load and return article text from file."""
        try:
            path = Path(filepath)
            if not path.exists():
                raise FileNotFoundError(f"Article file not found: {filepath}")
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                raise ValueError("Article file is empty")
            
            return content
            
        except Exception as e:
            print(f"Error loading article: {e}")
            sys.exit(1)
    
    def format_confidence_indicator(self, confidence: str) -> str:
        """Return a visual indicator for confidence level."""
        indicators = {
            "high": "🟢",
            "medium": "🟡", 
            "low": "🔴"
        }
        return indicators.get(confidence.lower(), "❔")
    
    def format_text_output(self, name: str, result: Dict[Any, Any], 
                          variants: set, article_names: list, 
                          verbose: bool = False) -> str:
        """Format results as human-readable text."""
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("ADVERSE MEDIA NAME MATCHING RESULT")
        lines.append("=" * 70)
        
        # Basic info
        lines.append(f"Target Name: {name}")
        lines.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Match result with visual indicator
        match_status = "MATCH FOUND" if result["match"] else "NO MATCH"
        confidence = result.get("confidence", "unknown")
        confidence_icon = self.format_confidence_indicator(confidence)
        
        lines.append(f"Result: {match_status} {confidence_icon}")
        lines.append(f"Confidence: {confidence.upper()}")
        lines.append(f"Method: {result['method'].replace('_', ' ').title()}")
        
        if result.get("score") is not None:
            lines.append(f"Match Score: {result['score']:.1f}/100")
        
        lines.append("")
        
        # Matched details
        if result["match"] and result.get("matched_name"):
            lines.append("Match Details:")
            lines.append(f"  • Matched Name in Article: '{result['matched_name']}'")
            if result.get("matched_variant"):
                lines.append(f"  • Matched Name Variant: '{result['matched_variant']}'")
        
        # Explanation
        lines.append("Explanation:")
        lines.append(f"  {result.get('explanation', 'No explanation provided')}")
        lines.append("")
        
        # Verbose information
        if verbose:
            lines.append("Detailed Analysis:")
            lines.append("-" * 30)
            
            lines.append(f"Name Variants Generated ({len(variants)}):")
            for variant in sorted(variants):
                lines.append(f"  • {variant}")
            lines.append("")
            
            lines.append(f"Names Found in Article ({len(article_names)}):")
            if article_names:
                for name in article_names:
                    lines.append(f"  • {name}")
            else:
                lines.append("  • No names detected")
            lines.append("")
            
            # Additional scores if available
            if result.get("detailed_scores"):
                lines.append("Detailed Fuzzy Match Scores:")
                for score_type, score in result["detailed_scores"].items():
                    lines.append(f"  • {score_type.replace('_', ' ').title()}: {score}")
                lines.append("")
        
        # Risk assessment for regulatory context
        lines.append("Risk Assessment:")
        if result["match"]:
            if confidence == "high":
                lines.append("  🔴 HIGH RISK - Strong indication this article refers to the target individual")
            elif confidence == "medium":
                lines.append("  🟡 MEDIUM RISK - Possible match, recommend manual review")
            else:
                lines.append("  🟡 MEDIUM RISK - Uncertain match, manual review required")
        else:
            if confidence == "high":
                lines.append("  🟢 LOW RISK - Article likely does not refer to target individual")
            else:
                lines.append("  🟡 MEDIUM RISK - Uncertain, consider manual review")
        
        lines.append("")
        lines.append("Recommendation:")
        if result["match"] or confidence != "high":
            lines.append("  📋 MANUAL REVIEW RECOMMENDED")
            lines.append("     An analyst should verify this match for regulatory compliance.")
        else:
            lines.append("  ✅ ARTICLE CAN LIKELY BE DISMISSED")
            lines.append("     Low probability of referring to target individual.")
        
        return "\n".join(lines)
    
    def format_json_output(self, name: str, result: Dict[Any, Any], 
                          variants: set, article_names: list) -> str:
        """Format results as JSON."""
        output = {
            "analysis_timestamp": datetime.now().isoformat(),
            "target_name": name,
            "match_result": {
                "match_found": result["match"],
                "confidence": result.get("confidence", "unknown"),
                "method": result["method"],
                "score": result.get("score"),
                "matched_name": result.get("matched_name"),
                "matched_variant": result.get("matched_variant"),
                "explanation": result.get("explanation")
            },
            "analysis_details": {
                "name_variants_generated": list(variants),
                "names_found_in_article": article_names,
                "total_variants": len(variants),
                "total_article_names": len(article_names)
            },
            "risk_assessment": {
                "requires_manual_review": result["match"] or result.get("confidence") != "high",
                "risk_level": "high" if result["match"] and result.get("confidence") == "high" 
                            else "medium" if result["match"] or result.get("confidence") != "high" 
                            else "low"
            }
        }
        
        # Add detailed scores if available
        if result.get("detailed_scores"):
            output["analysis_details"]["detailed_fuzzy_scores"] = result["detailed_scores"]
        
        return json.dumps(output, indent=2, ensure_ascii=False)
    
    def save_report(self, content: str, filepath: str, output_format: str):
        """Save the report to a file."""
        try:
            extension = ".json" if output_format == "json" else ".txt"
            if not filepath.endswith(extension):
                filepath += extension
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Report saved to: {filepath}")
        
        except Exception as e:
            print(f"Warning: Could not save report to {filepath}: {e}")
    
    def run(self):
        """Main execution method."""
        try:
            args = self.parser.parse_args()
            
            # Validate inputs
            if not args.name.strip():
                print("Error: Name cannot be empty")
                sys.exit(1)
            
            # Load article
            print(f"Loading article from: {args.filepath}")
            article_text = self.load_article(args.filepath)
            print(f"Article loaded successfully ({len(article_text)} characters)")
            
            # Process the matching
            print("Analyzing...")
            
            # Step 1: Generate name variants
            variants = generate_name_variants(args.name.strip())
            
            # Step 2: Extract names from article
            article_names = extract_person_names(article_text)
            
            # Step 3: Perform matching
            result = match_name_against_article(
                variants, article_names, 
                high_threshold=args.threshold
            )
            
            # Format output
            if args.output == "json":
                output = self.format_json_output(args.name, result, variants, article_names)
            else:
                output = self.format_text_output(args.name, result, variants, article_names, args.verbose)
            
            # Print results
            print("\n" + output)
            
            # Save report if requested
            if args.save_report:
                self.save_report(output, args.save_report, args.output)
            
            # Exit with appropriate code for automation
            sys.exit(0 if not result["match"] else 1)
            
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


def main():
    """Entry point for the CLI tool."""
    cli = NameMatchingCLI()
    cli.run()


if __name__ == "__main__":
    main()