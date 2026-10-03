import os
import ast
import json
from pathlib import Path
from typing import List, Dict, Any

# Directories to exclude from repository scanning
DEFAULT_IGNORE_DIRS = {
    ".git", "__pycache__", "venv", ".venv", "env", 
    "node_modules", "dist", "build", ".pytest_cache", ".idea"
}

def generate_function_response(func_name: str, args: List[str], docstring: str, body_snippet: str) -> str:
    """
    Generates an analytical response for a single function.
    Can be replaced or augmented with an external LLM API call.
    """
    param_str = ", ".join(args) if args else "no parameters"
    has_doc = "Includes docstring." if docstring else "Missing docstring."
    
    response = (
        f"Function '{func_name}' accepts {param_str}. {has_doc} "
        f"Code complexity: approximately {len(body_snippet.splitlines())} lines of code."
    )
    return response


def analyze_file(file_path: Path) -> List[Dict[str, Any]]:
    """Parses a Python source file into an AST and extracts function metadata."""
    functions_data = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()

        tree = ast.parse(source_code, filename=str(file_path))
        lines = source_code.splitlines()

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Extract arguments
                args = [arg.arg for arg in node.args.args]
                
                # Extract existing docstring
                docstring = ast.get_docstring(node) or ""
                
                # Extract source body snippet
                start_line = node.lineno - 1
                end_line = getattr(node, 'end_lineno', start_line + 10)
                body_snippet = "\n".join(lines[start_line:end_line])

                # Generate automated response/analysis for function
                response = generate_function_response(node.name, args, docstring, body_snippet)

                functions_data.append({
                    "function_name": node.name,
                    "file_path": str(file_path),
                    "line_number": node.lineno,
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                    "arguments": args,
                    "docstring": docstring,
                    "analysis_response": response
                })

    except Exception as e:
        print(f"[Warning] Failed to parse {file_path}: {e}")

    return functions_data


def scan_repository_functions(
    repo_path: str, 
    output_json: str = "repository_functions.json",
    output_md: str = "FUNCTIONS.md"
) -> List[Dict[str, Any]]:
    """
    Scans the repository directory, analyzes all functions, and writes output files.
    """
    repo_dir = Path(repo_path).resolve()
    all_functions = []

    print(f"Scanning repository at: {repo_dir}")

    for root, dirs, files in os.walk(repo_dir):
        # Exclude directories in-place
        dirs[:] = [d for d in dirs if d not in DEFAULT_IGNORE_DIRS]

        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                file_functions = analyze_file(file_path)
                all_functions.extend(file_functions)

    # 1. Export JSON Report
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_functions, f, indent=2)

    # 2. Export Markdown Report
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# Repository Functions Analysis\n\n")
        f.write(f"Total functions found: **{len(all_functions)}**\n\n")
        
        for fn in all_functions:
            f.write(f"## `{fn['function_name']}`\n")
            f.write(f"- **File:** `{fn['file_path']}:{fn['line_number']}`\n")
            f.write(f"- **Type:** `{'async def' if fn['is_async'] else 'def'}`\n")
            f.write(f"- **Arguments:** `{', '.join(fn['arguments'])}` \n")
            f.write(f"- **Response:** {fn['analysis_response']}\n\n")
            if fn['docstring']:
                f.write(f"> **Docstring:** {fn['docstring']}\n\n")
            f.write("---\n\n")

    print(f"Analysis complete. Extracted {len(all_functions)} functions.")
    print(f"Reports saved to '{output_json}' and '{output_md}'.")
    return all_functions


if __name__ == "__main__":
    # Point this to any target repository root directory
    TARGET_REPO = "."
    scan_repository_functions(TARGET_REPO)
