#!/usr/bin/env python3
"""
Simple report generator for sequence database commits and tags.

This script generates two types of simple HTML reports:
1. Commit reports: Lists sequences in alphabetical order
2. Tag reports: Lists sequences in reverse alphabetical order

Reports are saved to:
- commits/[commit_hash]/simple_commit_report.html
- tags/[tag_name]/simple_tag_report.html (only for tagged commits)
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


def get_current_commit_hash():
    """Get the current commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit hash: {e}")
        sys.exit(1)


def get_commit_tag(commit_hash=None):
    """Get tag for the specified commit, if any."""
    if commit_hash is None:
        commit_hash = "HEAD"
    
    # First check if there's an exact tag match
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--exact-match", commit_hash],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except subprocess.CalledProcessError:
        pass
    
    # If no exact match, check if we're in a GitHub Actions environment with a tag push
    if os.environ.get("GITHUB_EVENT_NAME") == "push" and os.environ.get("GITHUB_REF", "").startswith("refs/tags/"):
        # Extract tag name from GITHUB_REF (format: refs/tags/TAG_NAME)
        tag = os.environ.get("GITHUB_REF").replace("refs/tags/", "")
        print(f"Using tag from GitHub Actions environment: {tag}")
        return tag
    
    # No tag found
    return None


def get_all_sequences(sequence_dir):
    """Get all sequence files in the specified directory."""
    sequences = []
    for item in os.listdir(sequence_dir):
        if item.endswith(".seq"):
            sequences.append(item)
    return sequences


def create_commit_report(output_dir, commit_hash, tag, sequences):
    """Create a simple commit report."""
    # Sort sequences alphabetically
    sequences.sort()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate report
    report_path = os.path.join(output_dir, "simple_commit_report.html")
    
    with open(report_path, "w") as f:
        f.write("<!DOCTYPE html>\n")
        f.write("<html>\n")
        f.write("<head>\n")
        f.write("    <title>Simple Commit Report</title>\n")
        f.write("    <style>\n")
        f.write("        body { font-family: Arial, sans-serif; margin: 40px; }\n")
        f.write("        h1 { color: #333; }\n")
        f.write("        .commit-info { background-color: #f0f0f0; padding: 10px; border-left: 4px solid #333; }\n")
        f.write("        ul { margin-top: 20px; }\n")
        f.write("        li { margin-bottom: 5px; }\n")
        f.write("        .timestamp { color: #666; font-size: 0.8em; margin-top: 20px; }\n")
        f.write("    </style>\n")
        f.write("</head>\n")
        f.write("<body>\n")
        f.write("    <h1>Simple Commit Report</h1>\n")
        f.write("    <div class='commit-info'>\n")
        
        if tag:
            f.write(f"        <p>This report is based on commit {commit_hash} ({tag})</p>\n")
        else:
            f.write(f"        <p>This report is based on commit {commit_hash} (no tag)</p>\n")
            
        f.write("    </div>\n")
        f.write("    <h2>Sequences (Alphabetical Order)</h2>\n")
        f.write("    <ul>\n")
        
        for seq in sequences:
            f.write(f"        <li>{seq}</li>\n")
            
        f.write("    </ul>\n")
        f.write(f"    <p class='timestamp'>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>\n")
        f.write("</body>\n")
        f.write("</html>\n")
    
    print(f"Created commit report: {report_path}")
    return report_path


def create_tag_report(output_dir, tag, sequences):
    """Create a simple tag report."""
    # Sort sequences in reverse alphabetical order
    sequences.sort(reverse=True)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate report
    report_path = os.path.join(output_dir, "simple_tag_report.html")
    
    with open(report_path, "w") as f:
        f.write("<!DOCTYPE html>\n")
        f.write("<html>\n")
        f.write("<head>\n")
        f.write("    <title>Simple Tag Report</title>\n")
        f.write("    <style>\n")
        f.write("        body { font-family: Arial, sans-serif; margin: 40px; }\n")
        f.write("        h1 { color: #333; }\n")
        f.write("        .tag-info { background-color: #e6f7ff; padding: 10px; border-left: 4px solid #1890ff; }\n")
        f.write("        ul { margin-top: 20px; }\n")
        f.write("        li { margin-bottom: 5px; }\n")
        f.write("        .timestamp { color: #666; font-size: 0.8em; margin-top: 20px; }\n")
        f.write("    </style>\n")
        f.write("</head>\n")
        f.write("<body>\n")
        f.write("    <h1>Simple Tag Report</h1>\n")
        f.write("    <div class='tag-info'>\n")
        f.write(f"        <p>This report is based on tag {tag}</p>\n")
        f.write("    </div>\n")
        f.write("    <h2>Sequences (Reverse Alphabetical Order)</h2>\n")
        f.write("    <ul>\n")
        
        for seq in sequences:
            f.write(f"        <li>{seq}</li>\n")
            
        f.write("    </ul>\n")
        f.write(f"    <p class='timestamp'>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>\n")
        f.write("</body>\n")
        f.write("</html>\n")
    
    print(f"Created tag report: {report_path}")
    return report_path


def main():
    parser = argparse.ArgumentParser(description="Generate simple reports for sequence database")
    parser.add_argument("--output-dir", default="reports", help="Base directory for reports")
    parser.add_argument("--sequence-dir", default="onboard_sequences", help="Directory containing sequence files")
    parser.add_argument("--commit", help="Specific commit hash to report on (default: current HEAD)")
    parser.add_argument("--tag", help="Specific tag to report on (overrides automatic tag detection)")
    args = parser.parse_args()
    
    # Get commit hash
    commit_hash = args.commit if args.commit else get_current_commit_hash()
    print(f"Generating reports for commit: {commit_hash}")
    
    # Get tag (if any)
    if args.tag:
        tag = args.tag
        print(f"Using provided tag: {tag}")
    else:
        tag = get_commit_tag(commit_hash)
        if tag:
            print(f"Detected tag: {tag}")
        else:
            print("No tag detected for this commit")
    
    # Get sequences
    sequence_dir = Path(args.sequence_dir)
    sequences = get_all_sequences(sequence_dir)
    
    # Create base output directory
    base_output_dir = Path(args.output_dir)
    
    # Always create commit report
    commit_output_dir = base_output_dir / "commits" / commit_hash
    create_commit_report(commit_output_dir, commit_hash, tag, sequences)
    
    # Create tag report if commit is tagged
    if tag:
        tag_output_dir = base_output_dir / "tags" / tag
        create_tag_report(tag_output_dir, tag, sequences)
        
        # Copy commit report to tag directory for consistency
        commit_report_path = commit_output_dir / "simple_commit_report.html"
        tag_commit_report_path = tag_output_dir / "simple_commit_report.html"
        if os.path.exists(commit_report_path):
            with open(commit_report_path, "r") as src, open(tag_commit_report_path, "w") as dst:
                dst.write(src.read())
            print(f"Copied commit report to tag directory: {tag_commit_report_path}")
    
    print("Report generation complete!")


if __name__ == "__main__":
    main()
