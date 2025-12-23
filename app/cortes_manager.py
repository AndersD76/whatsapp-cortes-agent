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
        if os.path.exists(self.csv_path):
            df = pd.read_csv(self.csv_path, dtype=str)
            df = df.fillna("")
            return df
        else:
            df = pd.DataFrame(columns=[
                "numero", "lista_corte", "espessura", "tempo_corte",
                "opd", "data_entrega", "data_corte"
            ])
            df.to_csv(self.csv_path, index=False)
            return df

    def recarregar(self) -> None:
        self.df = self._carregar_planilha()

    def _salvar(self) -> None:
        self.df.to_csv(self.csv_path, index=False)

    def _is_concluido(self, data_corte: str) -> bool:
        return data_corte is not None and str(data_corte).strip() != ""

    def get_status_geral(self) -> Dict:
        total = len(self.df)
        concluidos = len(self.df[self.df["data_corte"].str.strip() != ""])
        pendentes = total - concluidos
        df_pendentes = self.df[self.df["data_corte"].str.strip() == ""]
        espessuras = df_pendentes["espessura"].value_counts().to_dict() if len(df_pendentes) > 0 else {}
        return {"total": total, "concluidos": concluidos, "pendentes": pendentes, "espessuras": espessuras}

    def get_pendentes(self, limite: int = 20) -> List[Dict]:
        df_pendentes = self.df[self.df["data_corte"].str.strip() == ""]
        df_pendentes = df_pendentes.sort_values("numero")
        return df_pendentes.head(limite).to_dict("records")

    def get_concluidos(self, limite: int = 20) -> List[Dict]:
        df_concluidos = self.df[self.df["data_corte"].str.strip() != ""]
        return df_concluidos.tail(limite).to_dict("records")

    def get_por_lista(self, lista: str) -> List[Dict]:
        df_filtrado = self.df[self.df["lista_corte"].str.contains(lista, case=False, na=False)]
        return df_filtrado.to_dict("records")

    def get_por_espessura(self, espessura: str) -> List[Dict]:
        df_filtrado = self.df[
            (self.df["data_corte"].str.strip() == "") &
            (self.df["espessura"].str.contains(espessura, case=False, na=False))
        ]
        return df_filtrado.to_dict("records")

    def get_por_opd(self, opd: str) -> List[Dict]:
        df_filtrado = self.df[self.df["opd"].str.contains(opd, case=False, na=False)]
        return df_filtrado.to_dict("records")

    def get_detalhe(self, numero: str) -> Optional[Dict]:
        df_corte = self.df[self.df["numero"].astype(str) == str(numero)]
        if len(df_corte) == 0:
            return None
        return df_corte.iloc[0].to_dict()

    def concluir_corte(self, numero: str) -> Dict:
        idx = self.df[self.df["numero"].astype(str) == str(numero)].index
        if len(idx) == 0:
            return {"sucesso": False, "erro": "Numero nao encontrado"}
        if self._is_concluido(self.df.loc[idx[0], "data_corte"]):
            return {"sucesso": False, "erro": "Este corte ja foi concluido"}
        self.df.loc[idx[0], "data_corte"] = datetime.now().strftime("%d/%m/%y")
        self._salvar()
        corte = self.df.loc[idx[0]].to_dict()
        return {"sucesso": True, "corte": corte}

    def buscar(self, termo: str) -> List[Dict]:
        termo = str(termo).lower()
        df_resultado = self.df[
            (self.df["numero"].astype(str).str.lower().str.contains(termo, na=False)) |
            (self.df["lista_corte"].str.lower().str.contains(termo, na=False)) |
            (self.df["opd"].str.lower().str.contains(termo, na=False))
        ]
        return df_resultado.head(20).to_dict("records")


cortes_manager = CortesManager()
