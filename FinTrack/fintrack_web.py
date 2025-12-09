import sqlite3
from datetime import datetime
from collections import defaultdict
import statistics

class FinTrack:

    def __init__(self, arquivo_db="fintrack.db"):
        self.db = arquivo_db
        self._criar_tabela_transacoes()
        self.transacoes = self._carregar_transacoes()

    # ---------------- BANCO ---------------- #
    def _conectar(self):
        return sqlite3.connect(self.db)

    def _criar_tabela_transacoes(self):
        conn = self._conectar()
        conn.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            valor REAL,
            categoria TEXT,
            descricao TEXT,
            data TEXT
        )
        """)
        conn.commit()
        conn.close()

    def _carregar_transacoes(self):
        conn = self._conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, tipo, valor, categoria, descricao, data FROM transacoes")
        dados = cursor.fetchall()
        conn.close()

        return [
            {
                "id": d[0],
                "tipo": d[1],
                "valor": float(d[2]),
                "categoria": d[3],
                "descricao": d[4],
                "data": d[5],
            } for d in dados
        ]

    def salvar_dados(self):
        pass  # 🔥 para manter compatibilidade, mas agora não é mais necessário


    # ---------------- OPERAÇÕES CRUD ---------------- #
    def adicionar_transacao(self, tipo, valor, categoria, descricao="", data=None):
        if data is None:
            data = datetime.now().strftime("%Y-%m-%d")

        valor = float(str(valor).replace(",", "."))

        conn = self._conectar()
        conn.execute(
            "INSERT INTO transacoes (tipo, valor, categoria, descricao, data) VALUES (?, ?, ?, ?, ?)",
            (tipo, valor, categoria, descricao, data)
        )
        conn.commit()
        conn.close()

        self.transacoes = self._carregar_transacoes()

    def listar_transacoes(self, mes=None, ano=None):
        if mes and ano:
            return [t for t in self.transacoes if t["data"][5:7] == f"{mes:02d}" and t["data"][:4] == str(ano)]
        return self.transacoes

    def editar_transacao(self, id, **novos_dados):
        conn = self._conectar()
        trans = self.buscar_transacao(id)
        if not trans:
            return False

        trans.update(novos_dados)
        conn.execute(
            "UPDATE transacoes SET tipo=?, valor=?, categoria=?, descricao=?, data=? WHERE id=?",
            (trans["tipo"], trans["valor"], trans["categoria"], trans["descricao"], trans["data"], id)
        )

        conn.commit()
        conn.close()
        self.transacoes = self._carregar_transacoes()
        return True

    def deletar_transacao(self, id):
        conn = self._conectar()
        conn.execute("DELETE FROM transacoes WHERE id=?", (id,))
        conn.commit()
        conn.close()
        self.transacoes = self._carregar_transacoes()


    # ---------------- UTILIDADES ---------------- #
    def buscar_transacao(self, id):
        return next((t for t in self.transacoes if t["id"] == id), None)

    def validar_categoria(self, categoria, tipo):
        categoria = categoria.strip().title()
        aviso = None
        # Aqui você pode manter suas regras
        return categoria, aviso


    # ---------------- ANÁLISES ---------------- #
    def analisar_gastos(self, mes=None, ano=None):
        trans = self.listar_transacoes(mes, ano)
        if not trans:
            return None

        receitas = sum(t["valor"] for t in trans if t["tipo"] == "receita")
        despesas = sum(t["valor"] for t in trans if t["tipo"] == "despesa")
        saldo = receitas - despesas

        gastos_categoria = defaultdict(float)
        for t in trans:
            if t["tipo"] == "despesa":
                gastos_categoria[t["categoria"]] += t["valor"]

        return {
            "receitas": receitas,
            "despesas": despesas,
            "saldo": saldo,
            "gastos_categoria": dict(gastos_categoria),
        }

    def prever_proximo_mes(self):
        mensal = defaultdict(lambda: {"receita":0, "despesa":0})

        for t in self.transacoes:
            chave = t["data"][:7]
            if t["tipo"]=="receita": mensal[chave]["receita"]+=t["valor"]
            if t["tipo"]=="despesa": mensal[chave]["despesa"]+=t["valor"]

        if len(mensal)<2:
            return None
        
        rec = statistics.mean(v["receita"] for v in mensal.values())
        des = statistics.mean(v["despesa"] for v in mensal.values())
        
        return {
            "receita_prevista": rec,
            "despesa_prevista": des,
            "saldo_previsto": rec-des
        }

    def gerar_recomendacoes(self):
        anal = self.analisar_gastos()
        if not anal: return None
        # Aqui você pode manter seu sistema de sugestões
        print("💡 Recomendações automáticas baseadas nos gastos.")


