# ER Diagram CLI Tool

A command-line tool to convert Mermaid ER diagrams to Draw.io XML format.

## Installation

1. Ensure Python 3.6+ is installed.
2. Clone or download the repository.
3. Set up the virtual environment: The project includes a `.venv` directory.

## Usage

```bash
python main.py [input_file] [-o output_file]
```

- `input_file`: Path to the Mermaid ER diagram file. If not provided, reads from stdin.
- `-o output_file`: Path to the output Draw.io XML file. If not provided, writes to stdout.

## Example

```bash
python main.py diagram.mmd -o diagram.xml
```

Or pipe input:

```bash
cat diagram.mmd | python main.py > diagram.xml
```

## Supported Mermaid ER Syntax

- Entities with attributes: `ENTITY { type attr }`
- Relationships: `ENT1 ||--o{ ENT2 : label` (one to many), etc.

Cardinalities supported:
- `||--||`: One to one
- `||--o{` or `||--|{`: One to many
- `o{--||`: Many to one
- `o{--o{`: Many to many

## Output

The tool generates a Draw.io XML file that can be imported into Draw.io via File → Import From → Text.
