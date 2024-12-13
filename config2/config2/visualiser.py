import configparser
import subprocess
import os
import sys



def get_dependencies(package_name):
    # Использует dpkg для получения зависимостей
    result = subprocess.run(['apt-cache', 'depends', package_name], stdout=subprocess.PIPE)
    dependencies = []
    for line in result.stdout.decode('utf-8').split('\n'):
        if 'Depends:' in line:
            dependencies.append(line.split(':')[1].strip())
    return dependencies

"""def get_dependency_tree(package_name):
    try:
        result = subprocess.run(['apt-cache', 'depends', package_name], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        dependencies = output.splitlines()
        return dependencies
    except Exception as e:
        print(f"Ошибка при получении зависимостей: {e}")
        return []"""

def generate_puml(dependencies, package_name):
    visited=set()
    puml_lines = ["@startuml", f"package \"{package_name}\" {{"]
    def add_dependencies(pak, level):
        if pak in visited:
        	return
        visited.add(pak)
        # Добавляем пакет в UML
        #puml_lines.append(f"{' ' * level}- {pak}")
        sub_deps = get_dependencies(pak)
        #print(sub_deps)
        for dep in sub_deps:
            if dep:  # Фильтрация
                dep_name = dep.split()[0]  # Получаем только имя пакета
                print(f"{' ' * level} [{pak}] --> [{dep_name}]")
                puml_lines.append(f"{' ' * level} [{pak}] --> [{dep_name}]")
                add_dependencies(dep_name, level + 4)  # Увеличиваем уровень вложенности

    add_dependencies(package_name, 4)
    puml_lines.append("}")
    puml_lines.append("@enduml")
    
    return "\n".join(puml_lines)

def main():
    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    package_name = config['graph_visualization']['package_name']
    
    output_file = config['graph_visualization']['output_file']
    
    dependencies = get_dependencies(package_name)

    puml_output = generate_puml(dependencies, package_name)

    # Сохранение в файл
    with open(output_file, 'w') as file:
        file.write(puml_output)


if __name__ == '__main__':
    main()
