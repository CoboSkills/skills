#!/usr/bin/env python3
"""Add insurance policy."""
import json
import os
import uuid
import argparse
from datetime import datetime

INSURANCE_DIR = os.path.expanduser("~/.openclaw/workspace/memory/insurance")
POLICIES_FILE = os.path.join(INSURANCE_DIR, "policies.json")

def ensure_dir():
    os.makedirs(INSURANCE_DIR, exist_ok=True)

def load_policies():
    if os.path.exists(POLICIES_FILE):
        with open(POLICIES_FILE, 'r') as f:
            return json.load(f)
    return {"policies": []}

def save_policies(data):
    ensure_dir()
    with open(POLICIES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Add insurance policy')
    parser.add_argument('--type', required=True, 
                        choices=['health', 'home', 'renters', 'auto', 'life', 'umbrella', 'business'],
                        help='Policy type')
    parser.add_argument('--carrier', required=True, help='Insurance company')
    parser.add_argument('--premium', type=float, required=True, help='Annual premium')
    parser.add_argument('--renewal', help='Renewal date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    policy_id = f"POL-{str(uuid.uuid4())[:6].upper()}"
    
    policy = {
        "id": policy_id,
        "type": args.type,
        "carrier": args.carrier,
        "premium": args.premium,
        "renewal_date": args.renewal,
        "added_at": datetime.now().isoformat(),
        "coverage_limits": {},
        "deductibles": {}
    }
    
    data = load_policies()
    data['policies'].append(policy)
    save_policies(data)
    
    print(f"✓ Policy added: {policy_id}")
    print(f"  Type: {args.type}")
    print(f"  Carrier: {args.carrier}")
    print(f"  Premium: ${args.premium:,.2f}/year")

if __name__ == '__main__':
    main()
