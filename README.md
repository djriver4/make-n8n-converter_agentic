# Make.com to n8n Workflow Converter

This application converts Make.com (formerly Integromat) JSON workflow blueprints to n8n format, allowing users to migrate their workflows between these automation platforms.

## Features

- **GUI-based conversion tool** with a simple and intuitive interface
- **AI-powered conversion** using CrewAI framework with specialized agents
- **Research-enhanced accuracy** via Perplexity API for up-to-date platform information
- **Simulated conversion mode** for demonstration purposes when no API key is provided
- **Detailed research results** on Make.com and n8n platforms and their differences

## Requirements

- **Python 3.10+** (required due to CrewAI's dependency on the pipe operator (`|`) for union types)
- Required packages:
  - tkinter
  - crewai
  - perplexityai
  - requests

## Installation

### Using pip (Python 3.10+ required)

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/make-to-n8n-converter.git
   cd make-to-n8n-converter
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Using conda (recommended)

If you don't have Python 3.10+, you can use conda to create an environment with the correct Python version:

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/make-to-n8n-converter.git
   cd make-to-n8n-converter
   ```

2. Create and activate a conda environment:
   ```bash
   conda env create -f environment.yml
   conda activate make_n8n
   ```

## Usage

1. Run the application:
   ```bash
   python src/make_to_n8n_converter.py
   ```

2. Enter your API keys:
   - **AI API Key**: For CrewAI framework (OpenAI API key or compatible)
   - **Perplexity API Key**: For researching the latest platform documentation

3. Research platform information (optional but recommended):
   - Click "Research Platforms" to get the latest information about Make.com and n8n platforms

4. Load a Make.com JSON workflow file:
   - Click "Browse..." and select your Make.com JSON blueprint file
   - The JSON will be displayed in the input tab

5. Convert the workflow:
   - Click "Convert to n8n" to start the conversion process
   - The converted n8n JSON will appear in the output tab when complete

6. Save the converted workflow:
   - Click "Save n8n JSON" to save the converted workflow to a file
   - Import this file into your n8n instance

## How It Works

### Conversion Process

The application uses a team of specialized AI agents to handle different aspects of the conversion process:

1. **Make.com Structure Analyzer**: Analyzes the Make.com JSON structure to identify all modules, connections, and features
2. **n8n Structure Mapper**: Maps each Make.com component to its equivalent n8n node type and configuration
3. **Connection Flow Specialist**: Specializes in recreating the exact connection structure between nodes following n8n's connection format
4. **n8n Schema Expert**: Ensures the generated workflow adheres to n8n's JSON schema requirements
5. **n8n JSON Validator**: Performs final validation to ensure the workflow will import and run correctly in n8n

This specialized approach ensures high-quality conversion that accurately preserves the original workflow's functionality and structure.

### AI Research Integration

The Perplexity API is used to research:
- Latest Make.com and n8n platform documentation
- Current module/node types and their parameters
- Best practices for mapping between platforms
- Edge cases and limitations

This research enhances the accuracy of the conversion by incorporating the latest information about both platforms.

## Notes

- The conversion process is not perfect and may require manual adjustments
- Some Make.com features may not have direct equivalents in n8n
- For best results, use the research feature to get the latest platform information

## License

MIT

## Acknowledgments

- CrewAI framework for providing the AI agent infrastructure
- Perplexity API for real-time research capabilities
- Make.com and n8n documentation

## Project Structure

```
make-to-n8n-converter/
├── src/                  # Source code
│   └── make_to_n8n_converter.py  # Main converter script
├── tests/                # Test files
├── docs/                 # Documentation
│   ├── make_workflow_json_structure.md  # Make.com JSON structure research
│   └── n8n_workflow_json_structure.md   # n8n JSON structure research
├── examples/             # Example Make.com and n8n workflows
└── README.md             # This file
```

## Documentation

For detailed information about the workflow structures and conversion process, please refer to:

- [Make.com Workflow JSON Structure](docs/make_workflow_json_structure.md) - Detailed analysis of Make.com's workflow format
- [n8n Workflow JSON Structure](docs/n8n_workflow_json_structure.md) - Comprehensive guide to n8n's workflow structure

These documents provide in-depth technical information about both platforms' JSON structures, which is essential for understanding the conversion process. # make-n8n-converter_agentic
