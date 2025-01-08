# Documentation

This directory contains the documentation for UniProtMapper.

## Building Documentation Locally

1. Install documentation dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Build the documentation:
   ```bash
   make html
   ```

3. View the documentation by opening `build/html/index.html` in your web browser.

## Documentation Structure

- `source/`: Documentation source files
  - `conf.py`: Sphinx configuration
  - `index.rst`: Homepage
  - `api/`: API reference
  - `tutorials/`: Usage tutorials
- `requirements.txt`: Documentation dependencies
- `Makefile` & `make.bat`: Build scripts
