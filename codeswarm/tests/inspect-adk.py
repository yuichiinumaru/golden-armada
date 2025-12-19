import google.adk as adk
import inspect
import pkgutil

def generate_module_report(module_obj, module_name_str, output_lines, indent_level=0):
    """Gera recursivamente informações sobre módulos e seus membros."""
    indent = "    " * indent_level
    output_lines.append(f"{indent}Módulo: {module_name_str} (Caminho: {getattr(module_obj, '__file__', 'N/A')})")

    members = inspect.getmembers(module_obj)
    public_members = sorted([m for m in members if not m[0].startswith('_')])

    for name, member_obj in public_members:
        member_indent = "    " * (indent_level + 1)
        try:
            if inspect.ismodule(member_obj):
                # Evitar recursão infinita ou explorar demais bibliotecas de terceiros importadas pelo ADK
                if member_obj.__name__.startswith(adk.__name__): # Apenas módulos do ADK
                    output_lines.append(f"{member_indent}Sub-Módulo: {name}")
                    # generate_module_report(member_obj, f"{module_name_str}.{name}", output_lines, indent_level + 2) # Recursão opcional
                else:
                    output_lines.append(f"{member_indent}Sub-Módulo (externo): {name} ({member_obj.__name__})")
            elif inspect.isclass(member_obj):
                output_lines.append(f"{member_indent}Classe: {name}")
                try:
                    # Adiciona o caminho completo de importação se possível
                    output_lines.append(f"{member_indent}  Import: from {member_obj.__module__} import {name}")
                    # Construtor
                    init_sig = inspect.signature(member_obj.__init__)
                    output_lines.append(f"{member_indent}    __init__{init_sig}")
                except (ValueError, TypeError, AttributeError):
                     output_lines.append(f"{member_indent}    __init__(self, ...)") # Fallback

                # Lista métodos públicos
                class_methods = inspect.getmembers(member_obj, inspect.isfunction) # ou isroutine para incluir built-ins
                public_class_methods = sorted([m_name for m_name, _ in class_methods if not m_name.startswith('_')])
                if public_class_methods:
                     output_lines.append(f"{member_indent}    Métodos Públicos: {', '.join(public_class_methods)}")

            elif inspect.isfunction(member_obj) or inspect.isbuiltin(member_obj):
                output_lines.append(f"{member_indent}Função: {name}")
                try:
                    # Adiciona o caminho completo de importação se possível
                    output_lines.append(f"{member_indent}  Import: from {member_obj.__module__} import {name}")
                    sig = inspect.signature(member_obj)
                    output_lines.append(f"{member_indent}  Assinatura: {name}{sig}")
                except (ValueError, TypeError, AttributeError):
                    output_lines.append(f"{member_indent}  Assinatura: {name}(...)") # Fallback
            elif not callable(member_obj): # Constantes/Variáveis de módulo
                 output_lines.append(f"{member_indent}Constante/Variável: {name}")

        except Exception as e:
            output_lines.append(f"{member_indent}Erro ao inspecionar {name}: {e}")
    output_lines.append("")


if __name__ == "__main__":
    report_lines = []
    report_lines.append("Relatório da Estrutura da Biblioteca ADK\n=====================================\n")

    # Inspecionar o pacote ADK principal e seus submódulos diretos
    generate_module_report(adk, adk.__name__, report_lines)

    # Tentar descobrir e inspecionar submódulos do ADK
    # (pkgutil pode ser mais robusto para encontrar submódulos de um pacote instalado)
    if hasattr(adk, '__path__'):
        for importer, modname, ispkg in pkgutil.walk_packages(path=adk.__path__,
                                                              prefix=adk.__name__ + '.',
                                                              onerror=lambda x: None):
            try:
                sub_module = __import__(modname, fromlist='dummy')
                generate_module_report(sub_module, modname, report_lines, indent_level=1)
            except Exception as e:
                report_lines.append(f"    Erro ao importar ou inspecionar submódulo {modname}: {e}\n")
    
    # Imprimir o relatório
    for line in report_lines:
        print(line)