#!/usr/bin/env python3
"""
Create a sample Excel file with phone numbers for testing MCP server
"""

import openpyxl
from datetime import datetime

def create_sample_excel(filename="test_phones.xlsx", num_phones=1000):
    """
    Create a sample Excel file with phone numbers
    
    Args:
        filename: Output filename
        num_phones: Number of phone numbers to generate
    """
    print(f"Creating {filename} with {num_phones} phone numbers...")
    
    # Create workbook and worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Phone Numbers"
    
    # Add header row
    ws.append(["Phone Number 1", "Phone Number 2", "Phone Number 3", "Phone Number 4"])
    
    # Generate phone numbers
    base_phone = "9876543210"
    
    for i in range(1, num_phones + 1):
        # Create phone number by appending sequential digits
        phone_number = base_phone + str(i % 10)
        
        # Add to multiple columns to make it realistic
        ws.append([
            phone_number,
            phone_number,
            phone_number,
            phone_number
        ])
    
    # Save the file
    wb.save(filename)
    
    print(f"[OK] Created {filename}")
    print(f"  Total rows: {num_phones + 1} (including header)")
    print(f"  File size: {os.path.getsize(filename)} bytes")
    print(f"  Created at: {datetime.now().isoformat()}")
    
    return filename

if __name__ == "__main__":
    import os
    
    print("="*60)
    print("Sample Excel File Generator for MCP Server Testing")
    print("="*60)
    print()
    
    # Create files with different sizes
    small_file = create_sample_excel("test_phones_small.xlsx", 100)
    medium_file = create_sample_excel("test_phones_medium.xlsx", 1000)
    large_file = create_sample_excel("test_phones_large.xlsx", 5000)
    
    print()
    print("="*60)
    print("Sample files created successfully!")
    print("="*60)
    print()
    print("Available files:")
    print(f"  - {small_file} ({os.path.getsize(small_file)} bytes)")
    print(f"  - {medium_file} ({os.path.getsize(medium_file)} bytes)")
    print(f"  - {large_file} ({os.path.getsize(large_file)} bytes)")
    print()
    print("You can now use these files to test the MCP server:")
    print(f"  python test_mcp.py")
    print(f"  # Then follow the prompts to use {medium_file}")
    print()
