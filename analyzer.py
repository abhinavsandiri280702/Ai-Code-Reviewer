import subprocess
import json

def run_static_analysis(file_path, language):
    if language == 'Python':
        try:
            process = subprocess.run(
                ['ruff', 'check', file_path, '--output-format=json'], 
                capture_output=True, text=True
            )
            return json.loads(process.stdout)
        except FileNotFoundError:
            return {"error": "Ruff is not installed. Run 'pip install ruff'."}
        except json.JSONDecodeError:
            return {"message": "Code is clean or failed to parse."}
            
    elif language in ['C', 'C++']:
        return {"message": "Static analysis skipped. Use AI Review for security/structure."}
            
    elif language == 'HTML':
        return {"message": "Static analysis skipped for HTML. Relying on deep AI review."}
            
    return {"message": f"Static analysis for {language} is not configured natively. Relying on AI review."}