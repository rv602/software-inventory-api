import json
import os
import subprocess

class DatasetGenerator:
    def __init__(self, mapping_file, output_dir):
        self.mapping_file = mapping_file
        self.output_dir = output_dir
        self.projects = self._load_mapping()

    def _load_mapping(self):
        with open(self.mapping_file, 'r') as f:
            return json.load(f)

    def _create_js_project(self, project_info):
        project_name = project_info['project_name']
        project_path = os.path.join(self.output_dir, project_name)
        
        # Create project directory
        os.makedirs(project_path, exist_ok=True)
        
        # Create package.json
        package_json = {
            "name": project_name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "description": f"Sample {project_name} project",
            "main": "index.js",
            "scripts": {
                "start": "node index.js",
                "test": "echo \"Error: no test specified\" && exit 1"
            },
            "dependencies": {
                dep['name']: dep['version'] for dep in project_info['dependencies']
            }
        }
        
        with open(os.path.join(project_path, 'package.json'), 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Create basic project structure
        os.makedirs(os.path.join(project_path, 'src'), exist_ok=True)
        with open(os.path.join(project_path, 'src', 'index.js'), 'w') as f:
            f.write('// Sample JavaScript project\nconsole.log("Hello, World!");')
        
        # Create README.md
        readme_content = f"""# {project_name}

This is a sample JavaScript project with the following dependencies:

{self._format_dependencies(project_info['dependencies'])}

## Setup

1. Install dependencies:
```bash
npm install
```

2. Run the project:
```bash
npm start
```
"""
        with open(os.path.join(project_path, 'README.md'), 'w') as f:
            f.write(readme_content)
        
        # Initialize git repository
        subprocess.run(['git', 'init'], cwd=project_path)

    def _create_python_project(self, project_info):
        project_name = project_info['project_name']
        project_path = os.path.join(self.output_dir, project_name)
        
        # Create project directory
        os.makedirs(project_path, exist_ok=True)
        
        # Create requirements.txt
        requirements = [f"{dep['name']}=={dep['version']}" for dep in project_info['dependencies']]
        with open(os.path.join(project_path, 'requirements.txt'), 'w') as f:
            f.write('\n'.join(requirements))
        
        # Create basic project structure
        os.makedirs(os.path.join(project_path, 'src'), exist_ok=True)
        with open(os.path.join(project_path, 'src', '__init__.py'), 'w') as f:
            f.write('# Sample Python project\n')
        
        with open(os.path.join(project_path, 'src', 'main.py'), 'w') as f:
            f.write('def main():\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    main()')
        
        # Create README.md
        readme_content = f"""# {project_name}

This is a sample Python project with the following dependencies:

{self._format_dependencies(project_info['dependencies'])}

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the project:
```bash
python src/main.py
```
"""
        with open(os.path.join(project_path, 'README.md'), 'w') as f:
            f.write(readme_content)
        
        # Initialize git repository
        subprocess.run(['git', 'init'], cwd=project_path)

    def _format_dependencies(self, dependencies):
        deps_text = []
        for dep in dependencies:
            deps_text.append(f"- {dep['name']} v{dep['version']}")
            deps_text.append("  CVEs:")
            for cve in dep['cves']:
                deps_text.append(f"  - {cve['cve_id']} ({cve['type']}, {cve['severity']})")
            deps_text.append("")
        return "\n".join(deps_text)

    def generate(self):
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        for project in self.projects:
            print(f"Generating {project['project_name']}...")
            
            if "(JS)" in project['project_name']:
                self._create_js_project(project)
            else:
                self._create_python_project(project)
            
            print(f"Completed generating {project['project_name']}")

def main():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths
    mapping_file = os.path.join(current_dir, 'mapping.json')
    output_dir = os.path.join(current_dir, 'repositories')
    
    # Create and run the dataset generator
    generator = DatasetGenerator(mapping_file, output_dir)
    generator.generate()

if __name__ == "__main__":
    main()
