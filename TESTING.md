# MCP Repository Cache - Testing Guide

This guide covers the testing setup and how to run tests for the MCP Repository Cache project.

## 🧪 Test Structure

```
tests/
├── __init__.py              # Tests package initialization
├── conftest.py              # Shared fixtures and configuration
├── test_models.py           # Tests for data models
├── test_storage.py          # Tests for storage/indexing functionality
├── test_git_fetcher.py      # Tests for Git operations
├── test_server.py           # Tests for FastAPI server
└── test_index_docs.py       # Tests for main indexing script
```

## 📦 Test Dependencies

The project uses pytest with several plugins for comprehensive testing:

### Core Testing Dependencies
- `pytest` - Main testing framework
- `pytest-cov` - Coverage reporting
- `pytest-asyncio` - Async test support
- `pytest-mock` - Mocking utilities
- `httpx` - For FastAPI test client

### Development Dependencies
- `black` - Code formatting
- `flake8` - Code linting

## 🚀 Running Tests

### Quick Start

```bash
# Install test dependencies
poetry install

# Run all tests
poetry run pytest

# Or use the test runner script
poetry run python scripts/run_tests.py
```

### Test Runner Script Options

```bash
# Run tests with coverage
poetry run python scripts/run_tests.py --coverage

# Run tests in verbose mode
poetry run python scripts/run_tests.py --verbose

# Run specific test markers
poetry run python scripts/run_tests.py --markers unit
poetry run python scripts/run_tests.py --markers integration

# Run specific test file
poetry run python scripts/run_tests.py --test-path tests/test_models.py

# Generate HTML coverage report
poetry run python scripts/run_tests.py --coverage --html-report
```

### Direct pytest Commands

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=mcp --cov=scripts --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_models.py

# Run specific test function
poetry run pytest tests/test_models.py::TestDocument::test_document_creation

# Run tests matching a pattern
poetry run pytest -k "test_document"

# Run tests with specific markers
poetry run pytest -m unit
poetry run pytest -m "not slow"
```

## 🏷️ Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (may use external resources)
- `@pytest.mark.slow` - Slow tests (skip during quick test runs)
- `@pytest.mark.git` - Tests that require Git operations

## 🔧 Test Fixtures

### Available Fixtures

The `conftest.py` file provides several shared fixtures:

#### `temp_dir`
Creates a temporary directory that is automatically cleaned up after the test.

```python
def test_example(temp_dir):
    # temp_dir is a path to a temporary directory
    assert os.path.exists(temp_dir)
```

#### `test_data_dir`
Creates a complete test data directory structure with raw, zim, sqlite, and vectors directories.

```python
def test_with_data_dirs(test_data_dir):
    temp_path, data_dirs = test_data_dir
    # data_dirs contains paths to raw, zim, sqlite, vectors directories
    assert data_dirs['raw'].exists()
```

#### `sample_config`
Provides a sample configuration dictionary for testing.

```python
def test_config(sample_config):
    assert "repositories" in sample_config
    assert "paths" in sample_config
```

#### `sample_document`
Provides a sample Document object for testing.

```python
def test_document(sample_document):
    assert sample_document["repo"] == "test-repo"
```

#### `mock_git_repo`
Creates a mock Git repository with sample files.

```python
def test_git_operations(mock_git_repo):
    # mock_git_repo is a path to a directory with sample files
    assert os.path.exists(mock_git_repo)
```

#### `client`
Provides a FastAPI test client for testing API endpoints.

```python
def test_api_endpoint(client):
    response = client.get("/docs")
    assert response.status_code == 200
```

## 🧪 Test Categories

### Unit Tests
Fast, isolated tests that verify individual components:

- **Models**: Document and Repository model validation
- **Storage**: Database operations and document indexing
- **Utilities**: Helper functions and data transformations

### Integration Tests
Tests that verify component interactions:

- **Git Fetcher**: Repository cloning and file extraction
- **Server**: API endpoints and database queries
- **Main Script**: Complete indexing workflow

### Mock Tests
Tests that use mocking to isolate components:

- Git operations (without actual repository cloning)
- File system operations
- External dependencies

## 📊 Coverage Reporting

### Generate Coverage Report
```bash
# Terminal coverage report
poetry run pytest --cov=mcp --cov=scripts --cov-report=term-missing

# HTML coverage report
poetry run pytest --cov=mcp --cov=scripts --cov-report=html

# Both terminal and HTML
poetry run pytest --cov=mcp --cov=scripts --cov-report=term-missing --cov-report=html
```

### Coverage Goals
- **Line Coverage**: Target 80%+ 
- **Branch Coverage**: Target 70%+
- **Critical Paths**: 90%+ (models, storage, main workflows)

### View Coverage Report
```bash
# After generating HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## 🐛 Debugging Tests

### Verbose Output
```bash
# Run with verbose output
poetry run pytest -v

# Show print statements
poetry run pytest -s

# Show local variables in tracebacks
poetry run pytest -l
```

### Debugging Specific Tests
```bash
# Run specific test with debugging
poetry run pytest tests/test_models.py::TestDocument::test_document_creation -v -s

# Run with Python debugger
poetry run pytest --pdb tests/test_models.py::TestDocument::test_document_creation

# Run until first failure
poetry run pytest -x
```

### Common Debugging Scenarios

1. **Test Discovery Issues**
   ```bash
   # Check what tests are discovered
   poetry run pytest --collect-only
   ```

2. **Fixture Issues**
   ```bash
   # Show fixture setup/teardown
   poetry run pytest --setup-show
   ```

3. **Performance Issues**
   ```bash
   # Show slowest tests
   poetry run pytest --durations=10
   ```

## 🔍 Test Writing Guidelines

### Best Practices

1. **Use Descriptive Names**
   ```python
   def test_document_creation_with_valid_data():
       # Good: descriptive
       pass
   
   def test_doc():
       # Bad: not descriptive
       pass
   ```

2. **Arrange-Act-Assert Pattern**
   ```python
   def test_document_serialization():
       # Arrange
       doc = Document(repo="test", path="readme.md", content="# Test")
       
       # Act
       result = doc.model_dump()
       
       # Assert
       assert result["repo"] == "test"
   ```

3. **Use Fixtures for Setup**
   ```python
   def test_with_fixture(sample_document):
       # Use fixture instead of manual setup
       result = process_document(sample_document)
       assert result is not None
   ```

4. **Mock External Dependencies**
   ```python
   def test_git_operations():
       with patch('mcp.git_fetcher.Repo.clone_from') as mock_clone:
           mock_clone.return_value = Mock()
           result = fetch_repo(sample_repo, temp_dir)
           mock_clone.assert_called_once()
   ```

5. **Test Edge Cases**
   ```python
   def test_document_validation():
       # Test normal case
       doc = Document(repo="test", path="readme.md", content="# Test")
       
       # Test edge cases
       doc_empty = Document(repo="test", path="empty.md", content="")
       doc_special = Document(repo="test", path="special.md", content="Content with 🚀 emoji")
   ```

### Test Organization

- Group related tests in classes
- Use `@pytest.mark` decorators for categorization
- Keep tests focused (one assertion per test when possible)
- Use helper functions for complex setup

## 🚀 Continuous Integration

### Pre-commit Checks
```bash
# Format code
poetry run black tests/ mcp/ scripts/

# Run linting
poetry run flake8 tests/ mcp/ scripts/

# Run tests
poetry run pytest
```

### Test Automation
The test suite is designed to run in CI/CD environments:

1. **Fast Feedback**: Unit tests run first
2. **Comprehensive**: Integration tests run after unit tests pass
3. **Coverage**: Coverage reports generated for quality gates

## 📈 Test Quality Metrics

### Key Metrics to Monitor
- **Test Execution Time**: Should complete in under 30 seconds
- **Coverage Percentage**: Maintain 80%+ line coverage
- **Test Flakiness**: Monitor for intermittent failures
- **Assertion Density**: Aim for 3-5 assertions per test

### Performance Benchmarks
- Unit tests: < 100ms per test
- Integration tests: < 1s per test
- Full test suite: < 30s total

## 🎯 Future Test Enhancements

### Planned Improvements
1. **Property-based testing** with Hypothesis
2. **Load testing** for API endpoints
3. **Security testing** for input validation
4. **Database migration testing**
5. **End-to-end testing** with real repositories

### Test Data Management
- **Factory pattern** for test data creation
- **Snapshot testing** for API responses
- **Test database** with seeded data

For questions or issues with testing, please refer to the main project documentation or create an issue in the repository.