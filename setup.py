from setuptools import setup, find_packages

# The root directory contains __init__.py, making it the AIComps package
# Find all packages starting from the root directory
packages = find_packages(where=".", include=["AIComps", "AIComps.*"])

# If find_packages doesn't find anything (because we're IN the package),
# manually build the package list
if not packages:
    import os
    packages = ["AIComps"]
    
    # Add subpackages
    for root_pkg in ["tasks", "comps"]:
        pkg_path = os.path.join(".", root_pkg)
        if os.path.isdir(pkg_path) and os.path.exists(os.path.join(pkg_path, "__init__.py")):
            packages.append(f"AIComps.{root_pkg}")
            
            # Find all subpackages
            for root, dirs, files in os.walk(pkg_path):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                rel_path = os.path.relpath(root, ".")
                if '__init__.py' in files and rel_path != root_pkg:
                    package_name = f"AIComps.{rel_path.replace(os.sep, '.')}"
                    if package_name not in packages:
                        packages.append(package_name)

print("Found packages:", packages)

setup(
    packages=packages,
    package_dir={"AIComps": "."},
)
