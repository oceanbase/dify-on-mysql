#!/usr/bin/env python3
"""
Fix for pyobvector bug where spec can be a string instead of dict
"""

import os
import sys

def fix_pyobvector_reflection():
    """Fix the spec.get bug in pyobvector reflection.py"""
    
    # Find the pyobvector reflection.py file
    import site
    site_packages = site.getsitepackages()
    
    reflection_file = None
    for sp in site_packages:
        potential_file = os.path.join(sp, 'pyobvector', 'schema', 'reflection.py')
        if os.path.exists(potential_file):
            reflection_file = potential_file
            break
    
    if not reflection_file:
        # Try in virtual environment
        venv_path = os.environ.get('VIRTUAL_ENV')
        if venv_path:
            potential_file = os.path.join(venv_path, 'lib', 'python3.12', 'site-packages', 'pyobvector', 'schema', 'reflection.py')
            if os.path.exists(potential_file):
                reflection_file = potential_file
    
    if not reflection_file:
        print("Could not find pyobvector reflection.py file")
        return False
    
    print(f"Found reflection.py at: {reflection_file}")
    
    # Read the file
    try:
        with open(reflection_file, 'r') as f:
            content = f.read()
        
        # Check if already fixed
        if 'isinstance(spec, dict) and spec.get' in content:
            print("Already fixed!")
            return True
        
        # Apply the fix
        original_line = 'if spec.get("onupdate", "").lower() == "restrict":'
        fixed_line = 'if isinstance(spec, dict) and spec.get("onupdate", "").lower() == "restrict":'
        
        if original_line in content:
            content = content.replace(original_line, fixed_line)
            
            original_line2 = 'if spec.get("ondelete", "").lower() == "restrict":'
            fixed_line2 = 'if isinstance(spec, dict) and spec.get("ondelete", "").lower() == "restrict":'
            content = content.replace(original_line2, fixed_line2)
            
            # Write back the fixed content
            with open(reflection_file, 'w') as f:
                f.write(content)
            
            print("Successfully fixed pyobvector reflection.py")
            return True
        else:
            print("Could not find the problematic line to fix")
            return False
            
    except Exception as e:
        print(f"Error fixing file: {e}")
        return False

if __name__ == "__main__":
    success = fix_pyobvector_reflection()
    sys.exit(0 if success else 1) 