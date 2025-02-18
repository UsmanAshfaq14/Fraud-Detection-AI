import json
import csv
from typing import Dict, List, Union
from datetime import datetime

class FraudDetectionSystem:
    def __init__(self):
        self.THRESHOLD_AMOUNT = 10000
        self.ALLOWED_LOCATIONS = {"New York", "Los Angeles", "Chicago", "Houston", "Phoenix"}
        self.REQUIRED_FIELDS = {"transaction_id", "transaction_amount", "transaction_currency", "transaction_location"}
    
    def validate_data_structure(self, transactions: List[Dict]) -> Dict:
        """Validate the basic data structure of transactions."""
        return {
            "num_transactions": len(transactions),
            "num_fields_per_transaction": len(self.REQUIRED_FIELDS)
        }
    
    def validate_required_fields(self, transaction: Dict, row_num: int) -> None:
        """Check if all required fields are present."""
        missing_fields = self.REQUIRED_FIELDS - set(transaction.keys())
        if missing_fields:
            raise ValueError(f"ERROR: Missing required field(s) at row {row_num}: {', '.join(missing_fields)}")
    
    def validate_data_types(self, transaction: Dict, row_num: int) -> None:
        """Validate data types and values."""
        # Check transaction amount
        try:
            amount = float(transaction['transaction_amount'])
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError(f"ERROR: Invalid data type for transaction_amount at row {row_num}")
        
        # Check currency
        if transaction['transaction_currency'] != "USD":
            raise ValueError(f"ERROR: Unsupported currency detected at row {row_num}. Please use USD.")
        
        # Check location type
        if not isinstance(transaction['transaction_location'], str):
            raise ValueError(f"ERROR: Invalid data type for transaction_location at row {row_num}")
    
    def analyze_transaction(self, transaction: Dict) -> Dict:
        """Analyze a single transaction for potential fraud."""
        amount = float(transaction['transaction_amount'])
        location = transaction['transaction_location']
        
        analysis = {
            "input_data": {
                "transaction_id": transaction['transaction_id'],
                "amount": f"${amount:,.2f}",
                "currency": transaction['transaction_currency'],
                "location": location
            },
            "decision_steps": [],
            "calculations": [],
            "final_status": {}
        }
        
        # Check amount threshold
        if amount > self.THRESHOLD_AMOUNT:
            difference = amount - self.THRESHOLD_AMOUNT
            analysis["calculations"].append({
                "type": "difference",
                "formula": r"Difference = transaction\_amount - threshold\_amount",
                "latex": f"$\\text{{Difference}} = {amount:,.2f} - {self.THRESHOLD_AMOUNT:,.2f} = {difference:,.2f}$"
            })
            analysis["final_status"] = {
                "status": "Flagged for Fraud: High Amount",
                "explanation": f"Transaction amount (${amount:,.2f}) exceeds threshold (${self.THRESHOLD_AMOUNT:,.2f}) by ${difference:,.2f}"
            }
        # Check location
        elif location not in self.ALLOWED_LOCATIONS:
            analysis["final_status"] = {
                "status": "Flagged for Fraud: Unusual Location",
                "explanation": f"Transaction location '{location}' is not in the list of usual locations: {', '.join(self.ALLOWED_LOCATIONS)}"
            }
        else:
            analysis["final_status"] = {
                "status": "Not Flagged",
                "explanation": "Transaction amount and location are within acceptable parameters"
            }
        
        return analysis
    
    def generate_report(self, data: str, format_type: str = "json") -> str:
        """Generate a comprehensive fraud detection report."""
        try:
            # Parse input data
            if format_type.lower() == "json":
                transactions = json.loads(data)["transactions"]
            else:  # CSV
                transactions = list(csv.DictReader(data.splitlines()))
            
            # Validate and analyze each transaction
            structure_info = self.validate_data_structure(transactions)
            analyzed_transactions = []
            
            for i, transaction in enumerate(transactions, 1):
                self.validate_required_fields(transaction, i)
                self.validate_data_types(transaction, i)
                analyzed_transactions.append(self.analyze_transaction(transaction))
            
            # Generate report
            report = [
                "# Data Validation Report",
                "## 1. Data Structure Check:",
                f"- Number of transactions: {structure_info['num_transactions']}",
                f"- Number of fields per transaction: {structure_info['num_fields_per_transaction']}",
                "",
                "## 2. Required Fields Check:",
                "- All required fields present in all transactions",
                "",
                "## 3. Data Type & Value Validation:",
                "- All data types and values are valid",
                "",
                "## Validation Summary:",
                "Data validation is successful! Proceeding with analysis...",
                "",
                "# Fraud Analysis Summary",
                f"Total Transactions Evaluated: {len(transactions)}",
                "",
                "# Detailed Analysis per Transaction"
            ]
            
            for analysis in analyzed_transactions:
                report.extend([
                    f"## Transaction {analysis['input_data']['transaction_id']}",
                    "### Input Data:",
                    f"- Transaction Amount: {analysis['input_data']['amount']}",
                    f"- Transaction Currency: {analysis['input_data']['currency']}",
                    f"- Transaction Location: {analysis['input_data']['location']}",
                    "",
                    "### Decision Analysis:"
                ])
                
                if analysis["calculations"]:
                    for calc in analysis["calculations"]:
                        report.append(f"- Calculate the difference:")
                        report.append(f"  {calc['latex']}")
                
                report.extend([
                    "",
                    "### Final Status:",
                    f"- Fraud Status: {analysis['final_status']['status']}",
                    f"- Explanation: {analysis['final_status']['explanation']}",
                    ""
                ])
            
            return "\n".join(report)
            
        except json.JSONDecodeError:
            return "ERROR: Invalid JSON format. Please check your input data."
        except csv.Error:
            return "ERROR: Invalid CSV format. Please check your input data."
        except Exception as e:
            return str(e)

# Example usage
if __name__ == "__main__":
    # Example JSON input
    example_json = '''
    {
    "transactions": [
        { "transaction_id": "TXB001", "transaction_amount": 3200, "transaction_currency": "USD", "transaction_location": "New York" },
        { "transaction_id": "TXB002", "transaction_amount": 14200, "transaction_currency": "USD", "transaction_location": "Los Angeles" },
        { "transaction_id": "TXB003", "transaction_amount": 7500, "transaction_currency": "USD", "transaction_location": "Chicago" },
        { "transaction_id": "TXB004", "transaction_amount": 15800, "transaction_currency": "USD", "transaction_location": "Houston" },
        { "transaction_id": "TXB005", "transaction_amount": 6800, "transaction_currency": "USD", "transaction_location": "Phoenix" },
        { "transaction_id": "TXB006", "transaction_amount": 8700, "transaction_currency": "USD", "transaction_location": "New York" },
        { "transaction_id": "TXB007", "transaction_amount": 9800, "transaction_currency": "USD", "transaction_location": "Los Angeles" },
        { "transaction_id": "TXB008", "transaction_amount": 11000, "transaction_currency": "USD", "transaction_location": "Chicago" },
        { "transaction_id": "TXB009", "transaction_amount": 4500, "transaction_currency": "USD", "transaction_location": "Houston" },
        { "transaction_id": "TXB010", "transaction_amount": 12500, "transaction_currency": "USD", "transaction_location": "Phoenix" },
        { "transaction_id": "TXB011", "transaction_amount": 5400, "transaction_currency": "USD", "transaction_location": "New York" },
        { "transaction_id": "TXB012", "transaction_amount": 13400, "transaction_currency": "USD", "transaction_location": "Los Angeles" },
        { "transaction_id": "TXB013", "transaction_amount": 9200, "transaction_currency": "USD", "transaction_location": "Chicago" },
        { "transaction_id": "TXB014", "transaction_amount": 15600, "transaction_currency": "USD", "transaction_location": "Houston" },
        { "transaction_id": "TXB015", "transaction_amount": 4800, "transaction_currency": "USD", "transaction_location": "Phoenix" }
    ]
    }

    '''
    
    detector = FraudDetectionSystem()
    report = detector.generate_report(example_json, "json")
    print(report)