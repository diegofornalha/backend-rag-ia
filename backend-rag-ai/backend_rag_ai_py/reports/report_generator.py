import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd

from ..metrics.workflow_metrics import WorkflowMetrics

logger = logging.getLogger(__name__)


class ReportGenerator:
    def __init__(self, metrics: WorkflowMetrics, output_dir: str = "reports"):
        """
        Inicializa gerador de relatórios

        Args:
            metrics: Instância de WorkflowMetrics
            output_dir: Diretório para salvar relatórios
        """
        self.metrics = metrics
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        logger.info(f"ReportGenerator inicializado em: {output_dir}")

    def generate_cycle_time_report(self) -> pd.DataFrame:
        """
        Gera relatório de tempo de ciclo

        Returns:
            DataFrame com dados de tempo de ciclo
        """
        data = []
        for embate_id in self.metrics.state_changes.keys():
            cycle_time = self.metrics.get_cycle_time(embate_id)
            if cycle_time:
                data.append(
                    {"embate_id": embate_id, "cycle_time_days": cycle_time.total_seconds() / 86400}
                )

        df = pd.DataFrame(data)

        # Salva CSV
        csv_path = os.path.join(self.output_dir, "cycle_time_report.csv")
        df.to_csv(csv_path, index=False)

        # Gera gráfico
        plt.figure(figsize=(10, 6))
        plt.hist(df["cycle_time_days"], bins=20)
        plt.xlabel("Tempo de Ciclo (dias)")
        plt.ylabel("Frequência")
        plt.title("Distribuição de Tempo de Ciclo")

        plot_path = os.path.join(self.output_dir, "cycle_time_distribution.png")
        plt.savefig(plot_path)
        plt.close()

        logger.info(f"Relatório de tempo de ciclo gerado: {csv_path}")
        return df

    def generate_state_distribution_report(self) -> pd.DataFrame:
        """
        Gera relatório de distribuição de estados

        Returns:
            DataFrame com distribuição de estados
        """
        stats = self.metrics.get_statistics()
        distribution = stats["state_distribution"]

        df = pd.DataFrame(
            [{"estado": state, "quantidade": count} for state, count in distribution.items()]
        )

        # Salva CSV
        csv_path = os.path.join(self.output_dir, "state_distribution_report.csv")
        df.to_csv(csv_path, index=False)

        # Gera gráfico
        plt.figure(figsize=(10, 6))
        plt.bar(df["estado"], df["quantidade"])
        plt.xlabel("Estado")
        plt.ylabel("Quantidade")
        plt.title("Distribuição de Estados")
        plt.xticks(rotation=45)

        plot_path = os.path.join(self.output_dir, "state_distribution.png")
        plt.savefig(plot_path, bbox_inches="tight")
        plt.close()

        logger.info(f"Relatório de distribuição de estados gerado: {csv_path}")
        return df

    def generate_operations_report(self) -> pd.DataFrame:
        """
        Gera relatório de operações

        Returns:
            DataFrame com contagem de operações
        """
        stats = self.metrics.get_statistics()
        operations = stats["operations"]

        df = pd.DataFrame(
            [{"operacao": op, "quantidade": count} for op, count in operations.items()]
        )

        # Salva CSV
        csv_path = os.path.join(self.output_dir, "operations_report.csv")
        df.to_csv(csv_path, index=False)

        # Gera gráfico
        plt.figure(figsize=(12, 6))
        plt.bar(df["operacao"], df["quantidade"])
        plt.xlabel("Operação")
        plt.ylabel("Quantidade")
        plt.title("Contagem de Operações")
        plt.xticks(rotation=45)

        plot_path = os.path.join(self.output_dir, "operations_distribution.png")
        plt.savefig(plot_path, bbox_inches="tight")
        plt.close()

        logger.info(f"Relatório de operações gerado: {csv_path}")
        return df

    def generate_state_duration_report(self) -> pd.DataFrame:
        """
        Gera relatório de duração em cada estado

        Returns:
            DataFrame com duração média em cada estado
        """
        data = []
        states = {"aberto", "em_andamento", "bloqueado", "fechado"}

        for embate_id in self.metrics.state_changes.keys():
            for state in states:
                duration = self.metrics.get_state_duration(embate_id, state)
                data.append(
                    {
                        "embate_id": embate_id,
                        "estado": state,
                        "duracao_dias": duration.total_seconds() / 86400,
                    }
                )

        df = pd.DataFrame(data)

        # Calcula média por estado
        avg_duration = df.groupby("estado")["duracao_dias"].mean().reset_index()

        # Salva CSV
        csv_path = os.path.join(self.output_dir, "state_duration_report.csv")
        avg_duration.to_csv(csv_path, index=False)

        # Gera gráfico
        plt.figure(figsize=(10, 6))
        plt.bar(avg_duration["estado"], avg_duration["duracao_dias"])
        plt.xlabel("Estado")
        plt.ylabel("Duração Média (dias)")
        plt.title("Duração Média em Cada Estado")
        plt.xticks(rotation=45)

        plot_path = os.path.join(self.output_dir, "state_duration.png")
        plt.savefig(plot_path, bbox_inches="tight")
        plt.close()

        logger.info(f"Relatório de duração de estados gerado: {csv_path}")
        return avg_duration

    def generate_summary_report(self) -> dict:
        """
        Gera relatório resumido com principais métricas

        Returns:
            Dicionário com resumo das métricas
        """
        stats = self.metrics.get_statistics()

        summary = {
            "total_embates": stats["total_embates"],
            "total_state_changes": stats["state_changes"],
            "avg_cycle_time_days": stats["avg_cycle_time"] / 86400
            if stats["avg_cycle_time"]
            else None,
            "state_distribution": stats["state_distribution"],
            "total_operations": sum(stats["operations"].values()),
            "operations_breakdown": stats["operations"],
            "generated_at": datetime.now().isoformat(),
        }

        # Salva JSON
        json_path = os.path.join(self.output_dir, "summary_report.json")
        with open(json_path, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Relatório resumido gerado: {json_path}")
        return summary

    def generate_all_reports(self) -> None:
        """Gera todos os relatórios disponíveis"""
        self.generate_cycle_time_report()
        self.generate_state_distribution_report()
        self.generate_operations_report()
        self.generate_state_duration_report()
        self.generate_summary_report()

        logger.info("Todos os relatórios foram gerados")
