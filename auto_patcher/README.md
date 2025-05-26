# Automated Vulnerability Patching Tool

The Automated Vulnerability Patching Tool is an intelligent module designed to streamline the process of automatically updating vulnerable packages in Node.js and Python projects. It uses OpenAI GPT-4o to generate optimized Dockerfiles and ensures updates are safe through comprehensive testing in isolated environments.

## Features

- **Smart Dockerfile Generation**: Uses OpenAI GPT-4o to generate optimized Dockerfiles based on project analysis
- **Isolated Testing**: Tests updates in isolated Docker containers before applying changes
- **Multi-Layered Validation**:
  - Unit Tests: Ensures basic functionality remains intact
  - Smoke Tests: Detects regressions caused by updates
  - Build Verification: Validates successful builds after updates
- **Comprehensive Reporting**: Generates detailed reports of all operations
- **Project Analysis**: Automatically detects project type and dependencies
- **Safe Update Process**: Only applies changes if all tests pass

## Prerequisites

- Python 3.8 or higher
- Docker installed and running
- OpenAI API key

## Installation

1. Navigate to the auto_patcher directory:

```bash
cd software-inventory-api/auto_patcher
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

The tool can be used in three different ways:

### 1. Generate Dockerfiles Only

This will analyze all projects in the repositories directory and generate appropriate Dockerfiles:

```bash
python main.py \
  --repositories /path/to/dataset/repositories \
  --openai-key your-openai-api-key
```

### 2. Generate Dockerfiles and Update Vulnerabilities

This will generate Dockerfiles and then update a specific package in all projects:

```bash
python main.py \
  --repositories /path/to/dataset/repositories \
  --openai-key your-openai-api-key \
  --package requests \
  --version 2.31.0
```

### 3. Update a Specific Project

This will update a specific package in a single project:

```bash
python main.py \
  --repositories /path/to/dataset/repositories \
  --openai-key your-openai-api-key \
  --package requests \
  --version 2.31.0 \
  --project project_name
```

## Command Line Arguments

- `--repositories`: Path to the repositories directory (required)
- `--openai-key`: Your OpenAI API key (required)
- `--output`: Output file for the patch report (default: patch_report.json)
- `--package`: Package name to update (optional)
- `--version`: New version of the package (optional)
- `--project`: Specific project to update (optional)

## Report Format

The tool generates a detailed JSON report with the following structure:

```json
{
  "total_updates": 5,
  "successful_updates": 3,
  "failed_updates": 2,
  "success_rate": 60.0,
  "detailed_reports": [
    {
      "project_path": "/path/to/project1",
      "package_name": "requests",
      "new_version": "2.31.0",
      "tests_passed": true,
      "smoke_tests_passed": true,
      "build_successful": true,
      "success": true,
      "message": "Successfully updated requests to 2.31.0"
    }
  ]
}
```

## Workflow

1. **Project Analysis**

   - Detects project type (Node.js/Python)
   - Analyzes dependencies
   - Identifies build configuration

2. **Dockerfile Generation**

   - Uses GPT-4o to generate optimized Dockerfile
   - Includes all necessary build steps
   - Configures for both development and production

3. **Update Process**

   - Updates dependency in appropriate file
   - Builds and tests in isolated container
   - Only applies changes if all tests pass

4. **Reporting**
   - Generates detailed report of all operations
   - Includes success/failure status
   - Provides comprehensive error information

## Important Notes

1. Make sure Docker is running on your system
2. The OpenAI API key must be valid
3. Projects must be in a supported format (Node.js or Python)
4. The tool will only update dependencies if all tests pass in the isolated environment
5. Each project should have appropriate test files (e.g., `test` script in package.json for Node.js or pytest for Python)

## Error Handling

The tool includes comprehensive error handling:

- Logs all operations with timestamps
- Provides detailed error messages
- Maintains project stability by only applying successful updates
- Generates detailed reports for failed updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
