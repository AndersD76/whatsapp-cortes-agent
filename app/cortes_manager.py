import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_PATH


class CortesManager:
    def __init__(self, csv_path: str = DATA_PATH):
        self.csv_path = csv_path
        self.df = self._carregar_planilha()

    def _carregar_planilha(self) -> pd.DataFrame:
        """Carrega a planilha CSV."""
        if os.path.exists(self.csv_path):
            df = pd.read_csv(self.csv_path, dtype=str)
            df = df.fillna("")
            return df
        else:
            # Cria planilha vazia se não existir
            df = pd.DataFrame(columns=[
                "codigo", "descricao", "status", "data_prevista",
                "data_conclusao", "responsavel", "prioridade"
            ])
            df.to_csv(self.csv_path, index=False)
            return df

    def recarregar(self) -> None:
        """Recarrega a planilha do disco."""
        self.df = self._carregar_planilha()

    def _salvar(self) -> None:
        """Salva a planilha no disco."""
        self.df.to_csv(self.csv_path, index=False)

    def get_status_geral(self) -> Dict:
        """Retorna o status geral dos cortes."""
        total = len(self.df)
        concluidos = len(self.df[self.df["status"] == "concluido"])
        pendentes = total - concluidos

        # Conta por prioridade (apenas pendentes)
        df_pendentes = self.df[self.df["status"] == "pendente"]
        prioridade_alta = len(df_pendentes[df_pendentes["prioridade"] == "alta"])
        prioridade_media = len(df_pendentes[df_pendentes["prioridade"] == "media"])
        prioridade_baixa = len(df_pendentes[df_pendentes["prioridade"] == "baixa"])

        return {
            "total": total,
            "concluidos": concluidos,
            "pendentes": pendentes,
            "prioridade_alta": prioridade_alta,
            "prioridade_media": prioridade_media,
            "prioridade_baixa": prioridade_baixa
        }

    def get_pendentes(self) -> List[Dict]:
        """Retorna lista de cortes pendentes."""
        df_pendentes = self.df[self.df["status"] == "pendente"]
        # Ordena por prioridade (alta > media > baixa)
        ordem_prioridade = {"alta": 0, "media": 1, "baixa": 2}
        df_pendentes = df_pendentes.copy()
        df_pendentes["ordem"] = df_pendentes["prioridade"].map(ordem_prioridade)
        df_pendentes = df_pendentes.sort_values("ordem")

        return df_pendentes.drop(columns=["ordem"]).to_dict("records")

    def get_concluidos(self) -> List[Dict]:
        """Retorna lista de cortes concluídos."""
        df_concluidos = self.df[self.df["status"] == "concluido"]
        return df_concluidos.to_dict("records")

    def get_por_prioridade(self, prioridade: str) -> List[Dict]:
        """Retorna cortes pendentes de uma prioridade específica."""
        df_filtrado = self.df[
            (self.df["status"] == "pendente") &
            (self.df["prioridade"] == prioridade.lower())
        ]
        return df_filtrado.to_dict("records")

    def get_detalhe(self, codigo: str) -> Optional[Dict]:
        """Retorna detalhes de um corte específico."""
        df_corte = self.df[self.df["codigo"].str.upper() == codigo.upper()]
        if len(df_corte) == 0:
            return None
        return df_corte.iloc[0].to_dict()

    def concluir_corte(self, codigo: str) -> Dict:
        """Marca um corte como concluído."""
        idx = self.df[self.df["codigo"].str.upper() == codigo.upper()].index

        if len(idx) == 0:
            return {"sucesso": False, "erro": "Código não encontrado"}

        if self.df.loc[idx[0], "status"] == "concluido":
            return {"sucesso": False, "erro": "Este corte já foi concluído"}

        # Atualiza o status e data de conclusão
        self.df.loc[idx[0], "status"] = "concluido"
        self.df.loc[idx[0], "data_conclusao"] = datetime.now().strftime("%Y-%m-%d")
        self._salvar()

        corte = self.df.loc[idx[0]].to_dict()
        return {"sucesso": True, "corte": corte}

    def adicionar_corte(self, dados: Dict) -> Dict:
        """Adiciona um novo corte à lista."""
        codigo = dados.get("codigo", "").upper()

        # Verifica se já existe
        if len(self.df[self.df["codigo"].str.upper() == codigo]) > 0:
            return {"sucesso": False, "erro": "Código já existe"}

        novo_corte = {
            "codigo": codigo,
            "descricao": dados.get("descricao", ""),
            "status": "pendente",
            "data_prevista": dados.get("data_prevista", ""),
            "data_conclusao": "",
            "responsavel": dados.get("responsavel", ""),
            "prioridade": dados.get("prioridade", "media").lower()
        }

        self.df = pd.concat([self.df, pd.DataFrame([novo_corte])], ignore_index=True)
        self._salvar()

        return {"sucesso": True, "corte": novo_corte}


# Instância global
cortes_manager = CortesManager()
