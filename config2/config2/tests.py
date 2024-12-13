import unittest
from unittest.mock import patch, mock_open
import textwrap
import visualiser

class TestDependencyVisualizer(unittest.TestCase):

    @patch('subprocess.run')
    def test_get_dependencies(self, mock_run):
        # Настройка
        package_name = "test-package"
        mock_run.return_value.stdout = b"""Depends: libfoo
Depends: libbar"""
        
        # Вызов функции
        from visualiser import get_dependencies
        dependencies = get_dependencies(package_name)

        # Проверка результата
        self.assertEqual(dependencies, ['libfoo', 'libbar'])
        mock_run.assert_called_once_with(['apt-cache', 'depends', package_name], stdout=mock_run.PIPE)

    @patch('visualiser.get_dependencies')
    def test_generate_puml(self, mock_get_dependencies):
        # Настройка
        package_name = "test-package"
        mock_get_dependencies.side_effect = [['libfoo', 'libbar'], ['libbaz'], []]

        # Вызов функции
        from visualiser import generate_puml
        puml_output = generate_puml([], package_name)

        # Ожидаемый вывод
        expected_output = textwrap.dedent(f"""\
            @startuml
            package "{package_name}" {{
                [test-package] --> [libfoo]
                [test-package] --> [libbar]
                [libfoo] --> [libbaz]
            }}
            @enduml
        """).strip()

        self.assertEqual(puml_output.strip(), expected_output)

    @patch('builtins.open', new_callable=mock_open)
    @patch('visualiser.get_dependencies')
    @patch('visualiser.generate_puml')
    def test_main(self, mock_generate_puml, mock_get_dependencies, mock_open_func):
        # Настройка
        import sys
        from visualiser import main
        
        mock_get_dependencies.return_value = ['libfoo']
        mock_generate_puml.return_value = "Some PUML content"
        
        # Создание временного файла конфигурации
        config_content = """\
        [graph_visualization]
        package_name = test-package
        output_file = output.puml
        """
        
        with patch('builtins.open', mock_open(read_data=config_content)):
            # Вызов функции
            main()

        # Проверка, что зависимости были получены
        mock_get_dependencies.assert_called_once_with('test-package')

        # Проверка, что PUML был сгенерирован
        mock_generate_puml.assert_called_once_with(['libfoo'], 'test-package')

        # Проверка, что файл был записан с правильным содержимым
        mock_open_func.assert_called_once_with('output.puml', 'w')
        mock_open_func().write.assert_called_once_with("Some PUML content")

if __name__ == '__main__':
    unittest.main()
