import os
import fnmatch
import re

def should_ignore(filepath, ignore_patterns):
    """Checks if a file or directory should be ignored based on .gitignore and .dockerignore patterns."""
    for pattern in ignore_patterns:
       if fnmatch.fnmatch(filepath, pattern):
           return True
    return False


def load_ignore_patterns(root_dir, ignore_files):
  """Loads ignore patterns from .gitignore and .dockerignore files."""
  ignore_patterns = []
  for ignore_file in ignore_files:
      ignore_path = os.path.join(root_dir, ignore_file)
      if os.path.exists(ignore_path):
          with open(ignore_path, 'r') as f:
              for line in f:
                  line = line.strip()
                  if line and not line.startswith('#'):
                    # convert git style glob patterns to glob patterns
                    pattern = line.replace('/**', '*')
                    ignore_patterns.append(pattern)
  return ignore_patterns

def is_binary_file(filepath):
    """Quick check if a file is likely binary using file extensions."""
    binary_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.7z', '.exe', '.dll', '.bin', '.mp3', '.mp4', '.avi', '.mov']
    _, ext = os.path.splitext(filepath)
    return ext.lower() in binary_extensions


def flatten_project(root_dir, output_file):
    """Flattens the project into a single string, respecting .gitignore, .dockerignore, and specified file types."""

    ignore_files = ['.gitignore', '.dockerignore']
    ignore_patterns = load_ignore_patterns(root_dir, ignore_files)

    with open(output_file, 'w', encoding='utf-8') as of:
        of.write("/\n")  # root directory

        for root, _, files in os.walk(root_dir):
            # Convert to relative path so ignore files are honored correctly
            relative_root = os.path.relpath(root, root_dir)
            if should_ignore(relative_root, ignore_patterns) or '.venv' in relative_root.split(os.sep):
                continue
            
            for filename in files:
                filepath = os.path.join(root, filename)
                relative_path = os.path.relpath(filepath, root_dir)

                if should_ignore(relative_path, ignore_patterns):
                  continue

                _, ext = os.path.splitext(filename)
                if ext.lower() not in ['.py', '.html']:
                    continue
                
                
                if is_binary_file(filepath):
                    of.write(f"{relative_path}: \n**Binary file content skipped:** {filename}\n\n")
                    continue
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        file_contents = f.read()
                        of.write(f"{relative_path}:\n{file_contents}\n\n")
                except Exception as e:
                    of.write(f"{relative_path}:\n**Error reading file: {filename}: {e}**\n\n")

if __name__ == "__main__":
    #project_root = '.' # Current directory, you can change to your project path
    project_root = '/media/dark-angel/Dev_Drive/Arcturus_Core/'
    output_file = 'flattened_project.txt'
    flatten_project(project_root, output_file)
    print(f"Project flattened successfully to {output_file}")