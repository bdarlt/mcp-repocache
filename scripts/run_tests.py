#!/usr/bin/env python3
"""
Test runner script for MCP Repository Cache.

This script provides a convenient way to run tests with various options.
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🚀 {description}")
    print(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"❌ {description} - FAILED")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run MCP Repository Cache tests")
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--markers", "-m",
        help="Run tests matching given markers (e.g., 'unit', 'integration')"
    )
    parser.add_argument(
        "--test-path", "-t",
        help="Run specific test file or directory"
    )
    parser.add_argument(
        "--no-cov",
        action="store_true",
        help="Disable coverage even if --coverage is specified"
    )
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="Generate HTML coverage report"
    )
    parser.add_argument(
        "--fix-pathlib",
        action="store_true",
        help="Work around Python 3.13 pathlib bug by disabling cache"
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ["pytest"]
    
    # Add verbose flag
    if args.verbose:
        cmd.append("-v")
    
    # Add coverage options
    if args.coverage and not args.no_cov:
        cmd.extend([
            "--cov=mcp",
            "--cov=scripts",
            "--cov-report=term-missing",
            "--cov-report=term:skip-covered"
        ])
        
        if args.html_report:
            cmd.append("--cov-report=html")
            print("📊 HTML coverage report will be generated in htmlcov/")
    
    # Add markers
    if args.markers:
        cmd.extend(["-m", args.markers])
    
    # Add test path
    if args.test_path:
        cmd.append(args.test_path)
    else:
        cmd.append("tests/")

    # Add Python 3.13 pathlib workaround if requested
    if args.fix_pathlib:
        cmd.extend(["-p", "no:cacheprovider"])
        print("🐍 Applying Python 3.13 pathlib workaround (disabling cache)")
    
    # Show test configuration
    print("🧪 MCP Repository Cache Test Runner")
    print("=" * 50)
    print(f"Test directory: {Path('tests').absolute()}")
    print(f"Coverage: {'Enabled' if args.coverage and not args.no_cov else 'Disabled'}")
    print(f"Verbose: {'Enabled' if args.verbose else 'Disabled'}")
    print(f"Python 3.13 workaround: {'Enabled' if args.fix_pathlib else 'Disabled'}")
    if args.markers:
        print(f"Markers: {args.markers}")
    if args.test_path:
        print(f"Test path: {args.test_path}")
    print("=" * 50)
    
    # Run tests
    success = run_command(cmd, "Running tests")
    
    # Additional checks after test run
    if success:
        print("\n✨ All tests passed!")
        
        if args.coverage and not args.no_cov and args.html_report:
            html_report_path = Path("htmlcov/index.html")
            if html_report_path.exists():
                print(f"📊 HTML coverage report available at: {html_report_path.absolute()}")
                print("   Open in browser to view detailed coverage information.")
    else:
        print("\n💥 Some tests failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())