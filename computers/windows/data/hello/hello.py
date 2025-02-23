import os

log_file = os.path.join("\\\\host.lan\\Data", "logs", "hello.log")

with open(log_file, 'w') as file:
    file.write('hello world from python')

print(f'File created at {log_file}')
