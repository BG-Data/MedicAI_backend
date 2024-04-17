import importlib
import os
import sys

def fetch_modules_from_folder(folder_path):
    modules = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.py'):
            module_name = file_name[:-3]  # Remove the .py extension
            try:
                module = importlib.import_module(f".{module_name}", package="api")
                modules[module_name] = module
            except ImportError:
                print(f"Failed to import module '{module_name}' from folder '{folder_path}'.")
    return modules

def fetch_classes_from_modules(modules):
    classes = {}
    for module_name, module in modules.items():
        module_classes = [cls for cls in module.__dict__.values() if isinstance(cls, type)]
        classes[module_name] = module_classes
    return classes

def instantiate_classes(classes):
    instances = {}
    for module_name, module_classes in classes.items():
        module_instances = {}
        for cls in module_classes:
            try:
                instance = cls()  # Instantiate the class
                module_instances[cls.__name__] = instance
            except Exception as e:
                print(f"Failed to instantiate class '{cls.__name__}' from module '{module_name}': {e}")
        instances[module_name] = module_instances
    return instances

folder_path = "/full/path/to/your/api/folder"  # Replace with the full path to the folder containing the modules
sys.path.append(folder_path)  # Add the folder path to sys.path if necessary

modules = fetch_modules_from_folder(folder_path)
classes = fetch_classes_from_modules(modules)
instances = instantiate_classes(classes)

# Now you have instances of all fetched classes
