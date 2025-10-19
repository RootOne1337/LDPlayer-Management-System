"""
Intelligent Project Analyzer
============================
Анализирует структуру проекта, зависимости, использование кода и предлагает оптимизации.

Author: LDPlayer Management System
Version: 1.0.0
"""

import ast
import os
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict, Counter
import re


# ANSI Colors
class Colors:
    """ANSI цвета для консольного вывода"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


@dataclass
class ModuleInfo:
    """Информация о модуле"""
    path: str
    name: str
    imports: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    lines_of_code: int = 0
    is_used: bool = False
    complexity_score: int = 0


@dataclass
class DependencyGraph:
    """Граф зависимостей модулей"""
    nodes: Dict[str, ModuleInfo] = field(default_factory=dict)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": {k: asdict(v) for k, v in self.nodes.items()},
            "edges": [[src, dst] for src, dst in self.edges]
        }


@dataclass
class ProjectAnalysisReport:
    """Полный отчет анализа проекта"""
    timestamp: str
    project_path: str
    total_files: int = 0
    total_lines: int = 0
    total_modules: int = 0
    total_functions: int = 0
    total_classes: int = 0
    unused_modules: List[str] = field(default_factory=list)
    unused_imports: Dict[str, List[str]] = field(default_factory=dict)
    circular_dependencies: List[List[str]] = field(default_factory=list)
    dependency_graph: Optional[DependencyGraph] = None
    recommendations: List[str] = field(default_factory=list)
    database_usage: Dict[str, Any] = field(default_factory=dict)
    complexity_hotspots: List[Tuple[str, int]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.dependency_graph:
            data['dependency_graph'] = self.dependency_graph.to_dict()
        return data
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class ProjectAnalyzer:
    """Интеллектуальный анализатор проекта"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_root = project_root / "src"
        self.modules: Dict[str, ModuleInfo] = {}
        self.dependency_graph = DependencyGraph()
        
    def analyze(self) -> ProjectAnalysisReport:
        """Выполнить полный анализ проекта"""
        print(f"\n{Colors.CYAN}{'=' * 100}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}🧠 ИНТЕЛЛЕКТУАЛЬНЫЙ АНАЛИЗ ПРОЕКТА{Colors.ENDC}".center(100))
        print(f"{Colors.CYAN}{'=' * 100}{Colors.ENDC}\n")
        
        report = ProjectAnalysisReport(
            timestamp=datetime.now().isoformat(),
            project_path=str(self.project_root)
        )
        
        # 1. Сканирование всех Python файлов
        print(f"{Colors.BLUE}📂 Сканирование структуры проекта...{Colors.ENDC}")
        self._scan_project_files(report)
        
        # 2. Анализ импортов и зависимостей
        print(f"{Colors.BLUE}🔗 Анализ зависимостей между модулями...{Colors.ENDC}")
        self._analyze_dependencies(report)
        
        # 3. Поиск неиспользуемого кода
        print(f"{Colors.BLUE}🔍 Поиск неиспользуемого кода...{Colors.ENDC}")
        self._find_unused_code(report)
        
        # 4. Анализ сложности кода
        print(f"{Colors.BLUE}📊 Анализ сложности кода...{Colors.ENDC}")
        self._analyze_complexity(report)
        
        # 5. Поиск циклических зависимостей
        print(f"{Colors.BLUE}🔄 Поиск циклических зависимостей...{Colors.ENDC}")
        self._find_circular_dependencies(report)
        
        # 6. Анализ использования базы данных
        print(f"{Colors.BLUE}💾 Анализ использования базы данных...{Colors.ENDC}")
        self._analyze_database_usage(report)
        
        # 7. Генерация рекомендаций
        print(f"{Colors.BLUE}💡 Генерация рекомендаций...{Colors.ENDC}")
        self._generate_recommendations(report)
        
        # 8. Вывод результатов
        self._print_report(report)
        
        # 9. Сохранение отчета
        self._save_report(report)
        
        return report
    
    def _scan_project_files(self, report: ProjectAnalysisReport):
        """Сканировать все Python файлы проекта"""
        if not self.src_root.exists():
            print(f"{Colors.RED}❌ Директория src/ не найдена!{Colors.ENDC}")
            return
        
        total_lines = 0
        file_count = 0
        
        for py_file in self.src_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            file_count += 1
            relative_path = py_file.relative_to(self.project_root)
            module_name = str(relative_path).replace(os.sep, ".").replace(".py", "")
            
            # Подсчет строк кода
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Считаем только не пустые и не комментарии
                    code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
                    lines_count = len(code_lines)
                    total_lines += lines_count
            except:
                lines_count = 0
            
            # Парсинг модуля
            module_info = self._parse_module(py_file, module_name, lines_count)
            self.modules[module_name] = module_info
            self.dependency_graph.nodes[module_name] = module_info
        
        report.total_files = file_count
        report.total_lines = total_lines
        report.total_modules = len(self.modules)
        
        print(f"  ✅ Найдено {file_count} Python файлов ({total_lines} строк кода)")
    
    def _parse_module(self, file_path: Path, module_name: str, lines_count: int) -> ModuleInfo:
        """Парсить Python модуль и извлечь информацию"""
        module_info = ModuleInfo(
            path=str(file_path),
            name=module_name,
            lines_of_code=lines_count
        )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            # Извлечь импорты
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_info.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_info.imports.append(node.module)
                
                # Извлечь функции
                elif isinstance(node, ast.FunctionDef):
                    module_info.functions.append(node.name)
                
                # Извлечь классы
                elif isinstance(node, ast.ClassDef):
                    module_info.classes.append(node.name)
        
        except Exception as e:
            print(f"  ⚠️  Ошибка парсинга {module_name}: {e}")
        
        return module_info
    
    def _analyze_dependencies(self, report: ProjectAnalysisReport):
        """Анализировать зависимости между модулями"""
        # Построить граф зависимостей
        for module_name, module_info in self.modules.items():
            for imported in module_info.imports:
                # Проверить если это локальный импорт
                for other_module in self.modules.keys():
                    if imported in other_module or other_module.endswith("." + imported):
                        # Добавить ребро в граф
                        self.dependency_graph.edges.append((module_name, other_module))
                        
                        # Отметить что other_module используется
                        if other_module in self.modules:
                            self.modules[other_module].is_used = True
                            self.modules[other_module].imported_by.append(module_name)
        
        report.dependency_graph = self.dependency_graph
        print(f"  ✅ Построен граф зависимостей: {len(self.dependency_graph.edges)} связей")
    
    def _find_unused_code(self, report: ProjectAnalysisReport):
        """Найти неиспользуемый код"""
        # Найти неиспользуемые модули
        for module_name, module_info in self.modules.items():
            if not module_info.is_used and not module_name.endswith("__init__"):
                # Проверить не является ли это entry point (server.py, etc)
                if "server.py" not in module_info.path and "main.py" not in module_info.path:
                    report.unused_modules.append(module_name)
        
        # Найти неиспользуемые импорты (простой анализ)
        for module_name, module_info in self.modules.items():
            unused_in_module = []
            for imported in module_info.imports:
                # Проверить используется ли в коде
                # (упрощенная проверка - просто проверяем наличие в тексте файла)
                try:
                    with open(module_info.path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Убрать строку импорта
                        import_pattern = rf"import\s+{re.escape(imported)}|from\s+{re.escape(imported)}"
                        content_without_import = re.sub(import_pattern, "", content)
                        
                        # Проверить есть ли использование
                        if imported not in content_without_import:
                            unused_in_module.append(imported)
                except:
                    pass
            
            if unused_in_module:
                report.unused_imports[module_name] = unused_in_module
        
        print(f"  ✅ Найдено {len(report.unused_modules)} неиспользуемых модулей")
        print(f"  ✅ Найдено {len(report.unused_imports)} модулей с неиспользуемыми импортами")
    
    def _analyze_complexity(self, report: ProjectAnalysisReport):
        """Анализировать сложность кода"""
        complexity_scores = []
        
        for module_name, module_info in self.modules.items():
            # Простая метрика сложности: LOC + количество функций + классов
            complexity = (
                module_info.lines_of_code +
                len(module_info.functions) * 10 +
                len(module_info.classes) * 20
            )
            module_info.complexity_score = complexity
            complexity_scores.append((module_name, complexity))
        
        # Сортировать по сложности
        complexity_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Топ 10 самых сложных модулей
        report.complexity_hotspots = complexity_scores[:10]
        
        report.total_functions = sum(len(m.functions) for m in self.modules.values())
        report.total_classes = sum(len(m.classes) for m in self.modules.values())
        
        print(f"  ✅ Найдено {report.total_functions} функций и {report.total_classes} классов")
    
    def _find_circular_dependencies(self, report: ProjectAnalysisReport):
        """Найти циклические зависимости"""
        # Простой алгоритм поиска циклов (DFS)
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            # Найти всех соседей
            neighbors = [dst for src, dst in self.dependency_graph.edges if src == node]
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Найден цикл!
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)
            
            rec_stack.remove(node)
        
        # Запустить DFS для каждого узла
        for node in self.dependency_graph.nodes.keys():
            if node not in visited:
                dfs(node, [])
        
        report.circular_dependencies = cycles
        
        if cycles:
            print(f"  ⚠️  Найдено {len(cycles)} циклических зависимостей!")
        else:
            print(f"  ✅ Циклических зависимостей не найдено")
    
    def _analyze_database_usage(self, report: ProjectAnalysisReport):
        """Анализировать использование базы данных"""
        db_usage = {
            "models_defined": [],
            "migrations_count": 0,
            "query_locations": [],
            "orm_usage": []
        }
        
        # Поиск моделей БД
        for module_name, module_info in self.modules.items():
            if "models" in module_name.lower():
                db_usage["models_defined"].extend([
                    f"{module_name}.{cls}" for cls in module_info.classes
                ])
            
            # Поиск SQL запросов в коде
            try:
                with open(module_info.path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "SELECT" in content or "INSERT" in content or "UPDATE" in content:
                        db_usage["query_locations"].append(module_name)
                    
                    # Поиск ORM использования
                    if "session." in content or ".query(" in content or "db." in content:
                        db_usage["orm_usage"].append(module_name)
            except:
                pass
        
        report.database_usage = db_usage
        print(f"  ✅ Найдено {len(db_usage['models_defined'])} моделей БД")
        print(f"  ✅ Найдено {len(db_usage['query_locations'])} мест с SQL запросами")
    
    def _generate_recommendations(self, report: ProjectAnalysisReport):
        """Генерировать рекомендации по оптимизации"""
        recommendations = []
        
        # Рекомендации по неиспользуемому коду
        if report.unused_modules:
            recommendations.append(
                f"🗑️  Удалить {len(report.unused_modules)} неиспользуемых модулей для упрощения проекта"
            )
        
        if report.unused_imports:
            total_unused = sum(len(v) for v in report.unused_imports.values())
            recommendations.append(
                f"🧹 Очистить {total_unused} неиспользуемых импортов в {len(report.unused_imports)} файлах"
            )
        
        # Рекомендации по циклическим зависимостям
        if report.circular_dependencies:
            recommendations.append(
                f"⚠️  КРИТИЧНО: Устранить {len(report.circular_dependencies)} циклических зависимостей"
            )
        
        # Рекомендации по сложности
        if report.complexity_hotspots:
            top_complex = report.complexity_hotspots[0]
            recommendations.append(
                f"📊 Рефакторинг модуля '{top_complex[0]}' (сложность: {top_complex[1]})"
            )
        
        # Рекомендации по БД
        if len(report.database_usage.get("query_locations", [])) > 5:
            recommendations.append(
                "💾 Рассмотреть создание единого DAL (Data Access Layer) для работы с БД"
            )
        
        # Общие рекомендации
        if report.total_lines > 10000:
            recommendations.append(
                "📦 Проект большой - рассмотреть разделение на подпакеты"
            )
        
        report.recommendations = recommendations
    
    def _print_report(self, report: ProjectAnalysisReport):
        """Вывести отчет в консоль"""
        print(f"\n{Colors.CYAN}{'=' * 100}{Colors.ENDC}")
        print(f"{Colors.BOLD}📊 РЕЗУЛЬТАТЫ АНАЛИЗА{Colors.ENDC}".center(100))
        print(f"{Colors.CYAN}{'=' * 100}{Colors.ENDC}\n")
        
        # Общая статистика
        print(f"{Colors.BOLD}📈 Общая статистика:{Colors.ENDC}")
        print(f"  • Всего файлов: {report.total_files}")
        print(f"  • Всего модулей: {report.total_modules}")
        print(f"  • Строк кода: {report.total_lines}")
        print(f"  • Функций: {report.total_functions}")
        print(f"  • Классов: {report.total_classes}")
        print(f"  • Зависимостей: {len(report.dependency_graph.edges) if report.dependency_graph else 0}")
        
        # Неиспользуемый код
        if report.unused_modules or report.unused_imports:
            print(f"\n{Colors.YELLOW}🗑️  Неиспользуемый код:{Colors.ENDC}")
            if report.unused_modules:
                print(f"  • Неиспользуемых модулей: {len(report.unused_modules)}")
                for module in report.unused_modules[:5]:
                    print(f"    - {module}")
                if len(report.unused_modules) > 5:
                    print(f"    ... и ещё {len(report.unused_modules) - 5}")
            
            if report.unused_imports:
                print(f"  • Файлов с неиспользуемыми импортами: {len(report.unused_imports)}")
        
        # Циклические зависимости
        if report.circular_dependencies:
            print(f"\n{Colors.RED}⚠️  ВНИМАНИЕ: Циклические зависимости:{Colors.ENDC}")
            for i, cycle in enumerate(report.circular_dependencies[:3], 1):
                print(f"  {i}. {' → '.join(cycle)}")
            if len(report.circular_dependencies) > 3:
                print(f"  ... и ещё {len(report.circular_dependencies) - 3}")
        
        # Сложность кода
        if report.complexity_hotspots:
            print(f"\n{Colors.BLUE}📊 Топ-5 самых сложных модулей:{Colors.ENDC}")
            for i, (module, complexity) in enumerate(report.complexity_hotspots[:5], 1):
                print(f"  {i}. {module} (сложность: {complexity})")
        
        # База данных
        if report.database_usage:
            print(f"\n{Colors.GREEN}💾 Использование базы данных:{Colors.ENDC}")
            print(f"  • Моделей: {len(report.database_usage.get('models_defined', []))}")
            print(f"  • SQL запросов в: {len(report.database_usage.get('query_locations', []))} файлах")
            print(f"  • ORM используется в: {len(report.database_usage.get('orm_usage', []))} файлах")
        
        # Рекомендации
        if report.recommendations:
            print(f"\n{Colors.BOLD}{Colors.CYAN}💡 Рекомендации:{Colors.ENDC}")
            for rec in report.recommendations:
                print(f"  {rec}")
        
        print(f"\n{Colors.CYAN}{'=' * 100}{Colors.ENDC}\n")
    
    def _save_report(self, report: ProjectAnalysisReport):
        """Сохранить отчет в JSON файл"""
        try:
            logs_dir = self.project_root / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = logs_dir / f"project_analysis_{timestamp}.json"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report.to_json())
            
            print(f"{Colors.GREEN}💾 Отчет сохранен: {report_path}{Colors.ENDC}\n")
        except Exception as e:
            print(f"{Colors.RED}❌ Не удалось сохранить отчет: {e}{Colors.ENDC}\n")


# Global instance
_last_analysis_report: Optional[ProjectAnalysisReport] = None


def analyze_project(project_root: Optional[Path] = None) -> ProjectAnalysisReport:
    """Запустить анализ проекта"""
    global _last_analysis_report
    
    if project_root is None:
        # Определить корень проекта автоматически
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent  # Server/
    
    analyzer = ProjectAnalyzer(project_root)
    _last_analysis_report = analyzer.analyze()
    return _last_analysis_report


def get_last_analysis_report() -> Optional[ProjectAnalysisReport]:
    """Получить последний отчет анализа"""
    return _last_analysis_report


if __name__ == "__main__":
    # Тест анализатора
    analyze_project()
