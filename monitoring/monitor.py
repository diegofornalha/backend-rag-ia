#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime
import importlib.util
import argparse


def import_check_module(name):
    """Importa um módulo de verificação dinamicamente"""
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(os.path.dirname(__file__), f"check_{name}.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checks(checks=None):
    """Executa as verificações especificadas ou todas"""
    available_checks = ["env", "deps", "network"]
    results = {"timestamp": datetime.now().isoformat(), "checks_run": []}

    checks_to_run = checks if checks else available_checks

    for check in checks_to_run:
        if check in available_checks:
            try:
                module = import_check_module(check)
                check_result = module.main()
                results["checks_run"].append(
                    {"name": check, "status": "success", "result": check_result}
                )
            except Exception as e:
                results["checks_run"].append(
                    {"name": check, "status": "error", "error": str(e)}
                )

    return results


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Monitor de ambiente Render")
    parser.add_argument(
        "--checks",
        nargs="+",
        help="Lista de verificações para executar (env, deps, network)",
    )
    parser.add_argument(
        "--output", choices=["json", "text"], default="json", help="Formato de saída"
    )

    args = parser.parse_args()
    results = run_checks(args.checks)

    if args.output == "json":
        print(json.dumps(results, indent=2))
    else:
        for check in results["checks_run"]:
            print(f"\n=== {check['name'].upper()} ===")
            if check["status"] == "success":
                print(json.dumps(check["result"], indent=2))
            else:
                print(f"ERROR: {check['error']}")


if __name__ == "__main__":
    main()
