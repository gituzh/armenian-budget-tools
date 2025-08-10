# Armenian State Budget Processor

A Python tool for processing and analyzing Armenian State Budget articles, converting them into easily analyzable CSV format.

## Overview

This tool helps process Armenian State Budget Excel files and converts them into structured CSV files, making it easier to analyze budget data. It's designed to handle the specific format of Armenian State Budget documents and extract relevant information into a clean, tabular format.

## Features

- Process Armenian State Budget Excel files
- Flatten multi-level budget structure into a single table
- Extract state body, program, and subprogram information
- Generate easily analyzable CSV datasets
- Support for different budget years

## Requirements

- Python 3.8 or higher
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/gituzh/budget-am.git
cd budget-am
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your Armenian State Budget Excel files in the `raw_data/budget_laws/[YEAR]` directory
2. Run the processor:
```bash
python extract_budget_articles.py
```
3. Find the generated CSV files in the `output/[YEAR]` directory

## Testing

To run the test suite:

```bash
pytest
```

For more detailed test output, you can use:

```bash
pytest -v
```

To run tests with coverage report:

```bash
pytest --cov=.
```

## Documentation

- Architecture: `docs/architecture.md`
- Product Requirements: `docs/prd.md`
- Roadmap: `docs/roadmap.md`

## Output Format

The generated CSV files will contain the following columns:
- State Body (Պետական մարմին)
- State Body Total (Ընդամենը պետական մարմնի համար)
- Program Code (Ծրագրի կոդ)
- Program Code Extended (Ծրագրի կոդ երկարացված)
- Program Name (Ծրագրի անվանում)
- Program Goal (Ծրագրի նպատակ)
- Program Result Description (Ծրագրի արդյունքի նկարագրություն)
- Program Total (Ընդամենը ծրագրի համար)
- Subprogram Code (Ենթածրագրի կոդ)
- Subprogram Name (Ենթածրագրի անվանում)
- Subprogram Description (Ենթածրագրի նկարագրություն)
- Subprogram Type (Ենթածրագրի տեսակ)
- Subprogram Total (Ընդամենը ենթածրագրի համար)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
