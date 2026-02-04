#!/usr/bin/env python3

import os
import csv
from pathlib import Path
from collections import defaultdict

def merge_customer_files(source_folder, output_file):
    """Merge all customer entry files into one consolidated CSV"""
    print('Merging customer data files...')
    
    # Dictionary to track customers
    # We'll use multiple matching strategies to find duplicates
    customers_by_phone = {}
    customers_by_email = {}
    customers_by_address = {}
    all_customers = []
    
    csv_files = list(Path(source_folder).glob('*.csv'))
    
    # Read all entries
    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get('Name', '').strip()
                    address = row.get('Address', '').strip()
                    phone = row.get('Phone', '').strip()
                    email = row.get('Email', '').strip()
                    
                    # Skip completely empty entries
                    if not any([name, address, phone, email]):
                        continue
                    
                    customer = {
                        'names': {name} if name else set(),
                        'addresses': {address} if address else set(),
                        'phones': {phone} if phone else set(),
                        'emails': {email} if email else set()
                    }
                    
                    # Try to find existing customer by phone, email, or address
                    existing = None
                    
                    if phone and phone in customers_by_phone:
                        existing = customers_by_phone[phone]
                    elif email and email in customers_by_email:
                        existing = customers_by_email[email]
                    elif address and address in customers_by_address:
                        existing = customers_by_address[address]
                    
                    if existing:
                        # Merge with existing customer
                        if name:
                            existing['names'].add(name)
                        if address:
                            existing['addresses'].add(address)
                        if phone:
                            existing['phones'].add(phone)
                        if email:
                            existing['emails'].add(email)
                        
                        # Update indexes
                        if phone:
                            customers_by_phone[phone] = existing
                        if email:
                            customers_by_email[email] = existing
                        if address:
                            customers_by_address[address] = existing
                    else:
                        # New customer
                        all_customers.append(customer)
                        if phone:
                            customers_by_phone[phone] = customer
                        if email:
                            customers_by_email[email] = customer
                        if address:
                            customers_by_address[address] = customer
                            
        except Exception as e:
            print(f"  Error reading {csv_file.name}: {e}")
    
    print(f"  Read entries from {len(csv_files)} files")
    print(f"  Consolidated into {len(all_customers)} unique customers")
    
    # Write consolidated file
    if all_customers:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Address', 'Phone', 'Email'])
            
            for customer in all_customers:
                # Join multiple values with " | " separator
                names_str = ' | '.join(sorted(customer['names']))
                addresses_str = ' | '.join(sorted(customer['addresses']))
                phones_str = ' | '.join(sorted(customer['phones']))
                emails_str = ' | '.join(sorted(customer['emails']))
                
                writer.writerow([
                    names_str,
                    addresses_str,
                    phones_str,
                    emails_str
                ])
        
        print(f"  ✓ Saved to: {output_file}")
        print(f"  ✓ {len(all_customers)} unique customers")
    else:
        print(f"  No customer data found")

def main():
    downloads_path = Path.home() / 'Downloads' / 'MapData'
    
    if not downloads_path.exists():
        print(f"ERROR: MapData folder not found at: {downloads_path}")
        print("Make sure the extension has created some files first.")
        return
    
    print("=" * 60)
    print("Map Data Collector - Smart Merge")
    print("=" * 60)
    print(f"\nProcessing: {downloads_path}\n")
    
    # Merge all entries
    entries_folder = downloads_path / 'entries'
    if entries_folder.exists():
        merge_customer_files(
            entries_folder,
            downloads_path / 'consolidated_customers.csv'
        )
    else:
        print('No entries folder found')
    
    print("\n" + "=" * 60)
    print("✓ Merge complete!")
    print("=" * 60)
    print(f"\nConsolidated file: {downloads_path / 'consolidated_customers.csv'}")
    print("\nFeatures:")
    print("  • Removed duplicate customers")
    print("  • Merged ALL data for same person")
    print("  • Matched by phone, email, or address")
    print("  • Multiple values separated by ' | '")
    print(f"\nOriginal files kept in: {entries_folder}")

if __name__ == '__main__':
    main()
