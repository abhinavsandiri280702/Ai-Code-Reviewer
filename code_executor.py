import subprocess
import os
import re

def execute_code(file_path, language):
    try:
        # 1. PYTHON
        if language == 'Python':
            result = subprocess.run(f'python "{file_path}"', shell=True, capture_output=True, text=True, timeout=5)
            return format_output(result)
            
        # 2. C
        elif language == 'C':
            exe_name = "temp_exec.exe" if os.name == 'nt' else "./temp_exec"
            compile_res = subprocess.run(f'gcc "{file_path}" -o temp_exec', shell=True, capture_output=True, text=True)
            if compile_res.returncode != 0:
                return {"status": "error", "text": f"Compilation Error:\n{compile_res.stderr}"}
            result = subprocess.run(exe_name, shell=True, capture_output=True, text=True, timeout=5)
            if os.path.exists('temp_exec.exe'): os.remove('temp_exec.exe')
            if os.path.exists('temp_exec'): os.remove('temp_exec')
            return format_output(result)

        # 3. C++
        elif language == 'C++':
            exe_name = "temp_exec.exe" if os.name == 'nt' else "./temp_exec"
            compile_res = subprocess.run(f'g++ "{file_path}" -o temp_exec', shell=True, capture_output=True, text=True)
            if compile_res.returncode != 0:
                return {"status": "error", "text": f"Compilation Error:\n{compile_res.stderr}"}
            result = subprocess.run(exe_name, shell=True, capture_output=True, text=True, timeout=5)
            if os.path.exists('temp_exec.exe'): os.remove('temp_exec.exe')
            if os.path.exists('temp_exec'): os.remove('temp_exec')
            return format_output(result)
            
        # 4. JAVASCRIPT (Using shell=True to find Node in Windows PATH)
        elif language == 'JavaScript':
            result = subprocess.run(f'node "{file_path}"', shell=True, capture_output=True, text=True, timeout=5)
            return format_output(result)

        # 5. JAVA (Advanced Handler for strict Class naming)
        elif language == 'Java':
            # Read the file to find the actual class name
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Regex to find 'class MyClassName'
            match = re.search(r'class\s+([A-Za-z0-9_]+)', content)
            
            if match:
                class_name = match.group(1)
                new_file_path = f"{class_name}.java"
                
                # Rename temp_code.java to ActualClassName.java
                os.rename(file_path, new_file_path)
                
                # Compile it
                comp = subprocess.run(f'javac "{new_file_path}"', shell=True, capture_output=True, text=True)
                if comp.returncode != 0:
                    if os.path.exists(new_file_path): os.remove(new_file_path)
                    return {"status": "error", "text": f"Compilation Error:\n{comp.stderr}"}
                    
                # Run it
                res = subprocess.run(f'java {class_name}', shell=True, capture_output=True, text=True, timeout=5)
                
                # Cleanup Java files
                if os.path.exists(new_file_path): os.remove(new_file_path)
                if os.path.exists(f"{class_name}.class"): os.remove(f"{class_name}.class")
                
                return format_output(res)
            else:
                # Fallback if no class is found
                result = subprocess.run(f'java "{file_path}"', shell=True, capture_output=True, text=True, timeout=5)
                return format_output(result)

        # 6. HTML
        elif language == 'HTML':
            return {"status": "markup", "text": "HTML successfully parsed. Rendering live preview in the UI."}
            
        # FALLBACK
        else:
            return {"status": "skipped", "text": f"Execution for {language} is not supported."}
            
    except subprocess.TimeoutExpired:
        return {"status": "error", "text": "Execution Timed Out (Possible infinite loop)."}
    except Exception as e:
        return {"status": "error", "text": f"Error executing code. Ensure compilers are installed.\nDetails: {str(e)}"}

def format_output(result):
    if result.returncode == 0:
        return {"status": "success", "text": result.stdout.strip() if result.stdout else "Code executed successfully with no output."}
    else:
        return {"status": "error", "text": result.stderr.strip()}