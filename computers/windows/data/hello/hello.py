import os

desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
file_path = os.path.join(desktop_path, 'hello_from_python.txt')

with open(file_path, 'w') as file:
    file.write('hello world from python')

print(f'File created at {file_path}')
