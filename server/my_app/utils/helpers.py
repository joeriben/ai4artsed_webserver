"""
Helper functions for the AI4ArtsEd Web Server
"""
import math
import re
from datetime import datetime


def parse_model_name(model_name):
    """
    Parses a model name to extract a base name and size in billions of parameters.
    e.g., 'gemma:7b' -> ('gemma', 7)
          'llama-3.1-8b-instruct' -> ('llama', 8)
          'mistral-nemo' -> ('mistral-nemo', 0)
    """
    # Simple name part before any versioning
    base_name = model_name.split('-')[0].split(':')[0]

    # Find any number followed by 'b' or 'B'
    size_match = re.search(r'(\d+)[bB]', model_name)
    if size_match:
        return base_name, int(size_match.group(1))

    # Find name:sizeb format
    size_match = re.search(r':(\d+)[bB]?', model_name)
    if size_match:
        return base_name, int(size_match.group(1))
        
    return base_name, 0


def calculate_dimensions(size_str, ratio_str):
    """
    Calculate image dimensions based on size and aspect ratio.
    
    Args:
        size_str: Base size as string (e.g., "1024")
        ratio_str: Aspect ratio as string (e.g., "16:9")
    
    Returns:
        dict: Dictionary with 'width' and 'height' keys
    """
    try:
        side = int(size_str)
        total_pixels = side * side
        w_ratio, h_ratio = map(int, ratio_str.split(':'))
        aspect_value = w_ratio / h_ratio
        width = round(math.sqrt(total_pixels * aspect_value))
        height = round(width / aspect_value)
        # Round to multiples of 8 for better compatibility
        width = round(width / 8) * 8
        height = round(height / 8) * 8
        return {"width": width, "height": height}
    except Exception:
        # Default to square if parsing fails
        return {"width": 1024, "height": 1024}


def generate_timestamp():
    """Generate timestamp in yymmddhhmmss format"""
    return datetime.now().strftime("%y%m%d%H%M%S")


def calculate_node_execution_order(node_id, workflow_def):
    """
    Calculate execution order for a node based on dependencies
    
    Args:
        node_id: The ID of the node to calculate order for
        workflow_def: The workflow definition dictionary
    
    Returns:
        int: The execution order of the node
    """
    visited = set()
    visiting = set()
    order = 0
    
    def visit(id):
        nonlocal order
        if id in visiting:
            return 0  # Circular dependency
        if id in visited:
            return 0
        
        visiting.add(id)
        node = workflow_def.get(id)
        if node and node.get("inputs"):
            for input_val in node["inputs"].values():
                if isinstance(input_val, list) and len(input_val) > 0 and isinstance(input_val[0], str):
                    dep_id = input_val[0]
                    if dep_id in workflow_def:
                        visit(dep_id)
        visiting.remove(id)
        visited.add(id)
        order += 1
        return order
    
    return visit(node_id)


def parse_hidden_commands(prompt):
    """
    Parse and remove hidden commands from prompt.
    Commands format: #command# or #parameter:value#
    
    Args:
        prompt: The input prompt containing hidden commands
        
    Returns:
        tuple: (clean_prompt, commands_dict)
    """
    import re
    commands = {}
    
    while True:
        # Find next command pattern
        match = re.search(r'#([^:#]+)(?::([^#]+))?#', prompt)
        if not match:
            break
            
        command = match.group(1).lower()
        value = match.group(2)
        
        # Parse commands with appropriate type conversion
        if command == 'cfg' and value:
            try:
                commands['cfg'] = float(value)
            except ValueError:
                pass  # Skip invalid values
        elif command == 'seed' and value:
            try:
                commands['seed'] = int(value)
            except ValueError:
                pass  # Skip invalid values
        elif command == 'steps' and value:
            try:
                commands['steps'] = int(value)
            except ValueError:
                pass  # Skip invalid values
        elif command == 'denoise' and value:
            try:
                commands['denoise'] = float(value)
            except ValueError:
                pass  # Skip invalid values
        elif command == 'notranslate':
            commands['notranslate'] = True
        # Add more commands as needed
        
        # Remove command from prompt
        prompt = prompt[:match.start()] + prompt[match.end():]
    
    # Clean up multiple spaces
    clean_prompt = re.sub(r'\s+', ' ', prompt).strip()
    
    return clean_prompt, commands
