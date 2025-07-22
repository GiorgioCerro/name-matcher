# evaluation/evaluator.py

import json
from typing import List, Dict, Tuple
from dataclasses import dataclass
from matcher.name_variants import generate_name_variants
from matcher.article_parser import extract_person_names
from matcher.matcher import match_name_against_article

@dataclass
class TestCase:
    """Structure for a test case."""
    name: str
    article_text: str
    expected_match: bool
    case_type: str  # e.g., "exact_match", "nickname", "initials", "false_positive"
    notes: str = ""

class NameMatchingEvaluator:
    """Comprehensive evaluation framework for the name matching system."""
    
    def __init__(self):
        self.test_cases = []
        self.results = []
    
    def add_test_case(self, test_case: TestCase):
        """Add a test case to the evaluation suite."""
        self.test_cases.append(test_case)
    
    def create_synthetic_test_cases(self) -> List[TestCase]:
        """Generate synthetic test cases covering various scenarios."""
        test_cases = []
        
        # 1. Exact matches
        test_cases.append(TestCase(
            name="John Smith",
            article_text="John Smith, a local businessman, was arrested yesterday for fraud.",
            expected_match=True,
            case_type="exact_match"
        ))
        
        # 2. Nickname variations
        test_cases.append(TestCase(
            name="William Johnson",
            article_text="Bill Johnson announced his retirement from the company today.",
            expected_match=True,
            case_type="nickname"
        ))
        
        # 3. Initial usage
        test_cases.append(TestCase(
            name="Mary Elizabeth Anderson",
            article_text="M.E. Anderson was promoted to senior vice president.",
            expected_match=True,
            case_type="initials"
        ))
        
        # 4. Middle name as first name
        test_cases.append(TestCase(
            name="James Robert Wilson",
            article_text="Robert Wilson testified in court about the incident.",
            expected_match=True,
            case_type="middle_as_first"
        ))
        
        # 5. False positive - different person
        test_cases.append(TestCase(
            name="Michael Brown",
            article_text="Michelle Brown won the award for her outstanding research.",
            expected_match=False,
            case_type="false_positive"
        ))
        
        # 6. Hyphenated names
        test_cases.append(TestCase(
            name="Sarah Johnson-Smith",
            article_text="Sarah Smith was quoted in the article about climate change.",
            expected_match=True,
            case_type="hyphenated"
        ))
        
        # 7. Cultural name variations
        test_cases.append(TestCase(
            name="José María González",
            article_text="Jose Gonzalez announced his candidacy for mayor.",
            expected_match=True,
            case_type="cultural_variation"
        ))
        
        return test_cases
    
    def run_evaluation(self) -> Dict:
        """Run evaluation on all test cases and return metrics."""
        if not self.test_cases:
            self.test_cases = self.create_synthetic_test_cases()
        
        results = []
        
        for i, test_case in enumerate(self.test_cases):
            print(f"Running test case {i+1}/{len(self.test_cases)}: {test_case.case_type}")
            
            # Generate variants
            variants = generate_name_variants(test_case.name)
            
            # Extract names from article
            article_names = extract_person_names(test_case.article_text)
            
            # Perform matching
            match_result = match_name_against_article(variants, article_names)
            
            # Record result
            result = {
                "test_case": test_case,
                "variants_generated": list(variants),
                "article_names_extracted": article_names,
                "match_result": match_result,
                "predicted_match": match_result["match"],
                "expected_match": test_case.expected_match,
                "correct": match_result["match"] == test_case.expected_match
            }
            
            results.append(result)
            self.results = results
        
        return self.calculate_metrics()
    
    def calculate_metrics(self) -> Dict:
        """Calculate evaluation metrics."""
        if not self.results:
            return {}
        
        total = len(self.results)
        correct = sum(1 for r in self.results if r["correct"])
        
        # Calculate precision, recall, F1
        true_positives = sum(1 for r in self.results 
                           if r["predicted_match"] and r["expected_match"])
        false_positives = sum(1 for r in self.results 
                            if r["predicted_match"] and not r["expected_match"])
        false_negatives = sum(1 for r in self.results 
                            if not r["predicted_match"] and r["expected_match"])
        true_negatives = sum(1 for r in self.results 
                           if not r["predicted_match"] and not r["expected_match"])
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Breakdown by case type
        case_type_results = {}
        for result in self.results:
            case_type = result["test_case"].case_type
            if case_type not in case_type_results:
                case_type_results[case_type] = {"correct": 0, "total": 0}
            case_type_results[case_type]["total"] += 1
            if result["correct"]:
                case_type_results[case_type]["correct"] += 1
        
        for case_type in case_type_results:
            case_type_results[case_type]["accuracy"] = (
                case_type_results[case_type]["correct"] / 
                case_type_results[case_type]["total"]
            )
        
        return {
            "overall_accuracy": correct / total,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "total_cases": total,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "true_negatives": true_negatives,
            "case_type_breakdown": case_type_results
        }
    
    def print_detailed_results(self):
        """Print detailed results for analysis."""
        metrics = self.calculate_metrics()
        
        print("\n" + "="*60)
        print("NAME MATCHING SYSTEM EVALUATION RESULTS")
        print("="*60)
        
        print(f"Overall Accuracy: {metrics['overall_accuracy']:.2%}")
        print(f"Precision: {metrics['precision']:.2%}")
        print(f"Recall: {metrics['recall']:.2%}")
        print(f"F1 Score: {metrics['f1_score']:.2%}")
        
        print(f"\nConfusion Matrix:")
        print(f"True Positives: {metrics['true_positives']}")
        print(f"False Positives: {metrics['false_positives']}")
        print(f"False Negatives: {metrics['false_negatives']}")
        print(f"True Negatives: {metrics['true_negatives']}")
        
        print(f"\nResults by Case Type:")
        for case_type, stats in metrics['case_type_breakdown'].items():
            print(f"  {case_type}: {stats['correct']}/{stats['total']} ({stats['accuracy']:.2%})")
        
        print(f"\nDetailed Results:")
        for i, result in enumerate(self.results):
            status = "✓" if result["correct"] else "✗"
            print(f"{status} Case {i+1} ({result['test_case'].case_type}): "
                  f"'{result['test_case'].name}' -> "
                  f"Expected: {result['expected_match']}, "
                  f"Predicted: {result['predicted_match']} "
                  f"(Method: {result['match_result']['method']})")
            
            if not result["correct"]:
                print(f"    Explanation: {result['match_result']['explanation']}")
                print(f"    Article names found: {result['article_names_extracted']}")

if __name__ == "__main__":
    evaluator = NameMatchingEvaluator()
    evaluator.run_evaluation()
    evaluator.print_detailed_results()