
import os
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import re  
import sqlite3
from datetime import datetime

class FinTrack:  # Aplicativo funcional feito para portifólio (propriedade autoral/intelectual de Eduardo J.)'''
    # ================================
    #  🔻 1. Inicializa e conecta ao banco
    # ================================
    def __init__(self, banco='fintrack.db'):
        self.conexao = sqlite3.connect(banco)
        self.cursor = self.conexao.cursor()
        self.criar_tabela()

    # ================================
    #  🔻 2. Criação automática da tabela
    # ================================
    def criar_tabela(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                descricao TEXT,
                valor REAL NOT NULL,
                data TEXT NOT NULL
            )
        """)
        self.conexao.commit()

    # ================================
    #  🔻 3. Adicionar transação (C - Create)
    # ================================
    def adicionar_transacao(self, tipo, descricao, valor, data=None):
        if data is None:
            data = datetime.now().strftime("%Y-%m-%d")

        self.cursor.execute("""
            INSERT INTO transacoes (tipo, descricao, valor, data)
            VALUES (?, ?, ?, ?)
        """, (tipo, descricao, valor, data))

        self.conexao.commit()
        print("✔ Transação adicionada com sucesso!")

    # ================================
    #  🔻 4. Listar transações (R - Read)
    # ================================
    def listar_transacoes(self):
        self.cursor.execute("SELECT * FROM transacoes ORDER BY data DESC")
        transacoes = self.cursor.fetchall()

        print("\n=== LISTA DE TRANSAÇÕES ===")
        for t in transacoes:
            print(f"ID: {t[0]} | Tipo: {t[1]} | Descrição: {t[2]} | Valor: {t[3]} | Data: {t[4]}")

    # ================================
    #  🔻 5. Editar transação (U - Update)
    # ================================
    def editar_transacao(self, id, novo_tipo, nova_desc, novo_valor, nova_data):
        self.cursor.execute("""
            UPDATE transacoes
            SET tipo = ?, descricao = ?, valor = ?, data = ?
            WHERE id = ?
        """, (novo_tipo, nova_desc, novo_valor, nova_data, id))

        self.conexao.commit()
        print("✔ Transação atualizada!")

    # ================================
    #  🔻 6. Excluir transação (D - Delete)
    # ================================
    def excluir_transacao(self, id):
        self.cursor.execute("DELETE FROM transacoes WHERE id = ?", (id,))
        self.conexao.commit()
        print("❌ Transação removida com sucesso.")

    # ================================
    #  🔻 7. Fechar banco
    # ================================
    def fechar(self):
        self.conexao.close()

# =======================================================================================
# 📌 Exemplo de uso no terminal
# =======================================================================================
if __name__ == "__main__":
    app = FinTrack()

    while True:
        print("\n========================")
        print("   FINTRACK - SQLITE   ")
        print("========================")
        print("[1] Adicionar transação")
        print("[2] Listar transações")
        print("[3] Editar transação")
        print("[4] Excluir transação")
        print("[5] Sair")
        opcao = input("Escolha: ")

        if opcao == "1":
            tipo = input("Tipo (entrada/saída): ")
            desc = input("Descrição: ")
            valor = float(input("Valor: "))
            app.adicionar_transacao(tipo, desc, valor)

        elif opcao == "2":
            app.listar_transacoes()

        elif opcao == "3":
            id = int(input("ID para editar: "))
            tipo = input("Novo tipo: ")
            desc = input("Nova descrição: ")
            valor = float(input("Novo valor: "))
            data = input("Nova data (YYYY-MM-DD): ")
            app.editar_transacao(id, tipo, desc, valor, data)

        elif opcao == "4":
            id = int(input("ID para excluir: "))
            app.excluir_transacao(id)

        elif opcao == "5":
            app.fechar()
            print("Encerrando...")
            break

        else:
            print("❗ Opção inválida, tente novamente.")  

    


    def validar_valor(self, entrada):
        """Valida e converte entrada de valor monetário"""
        # Remove espaços, R$, vírgulas
        entrada = str(entrada).strip().replace('R$', '').replace(' ', '').replace(',', '.')
        
        # Remove múltiplos pontos (ex: 1.500.00 -> 1500.00)
        partes = entrada.split('.')
        if len(partes) > 2:
            entrada = ''.join(partes[:-1]) + '.' + partes[-1]
        
        try:
            valor = float(entrada)
            if valor < 0:
                raise ValueError("Valor não pode ser negativo")
            if valor > 1000000000:  # 1 bilhão
                raise ValueError("Valor muito alto")
            return valor
        except ValueError:
            raise ValueError("Valor inválido")
    
    def validar_categoria(self, categoria, tipo):
        """Valida se categoria existe ou sugere alternativas"""
        categoria = categoria.strip().title()
        
        if not categoria:
            return None, "Categoria não pode ser vazia"
        
        categorias_disponiveis = self.categorias_padrao[tipo]
        
        # Aceita categoria exata
        if categoria in categorias_disponiveis:
            return categoria, None
        
        # Busca categoria similar (case-insensitive)
        for cat in categorias_disponiveis:
            if cat.lower() == categoria.lower():
                return cat, None
        
        # Busca parcial
        sugestoes = [cat for cat in categorias_disponiveis 
                     if categoria.lower() in cat.lower() or cat.lower() in categoria.lower()]
        
        if sugestoes:
            return categoria, f"⚠️  '{categoria}' não encontrada. Você quis dizer: {', '.join(sugestoes)}?"
        
        return categoria, f"⚠️  '{categoria}' é uma categoria nova. Será adicionada ao sistema."
    
    def validar_data(self, data_str):
        """Valida formato de data"""
        if not data_str or data_str.strip() == '':
            return datetime.now().strftime('%Y-%m-%d'), None
        
        # Aceita formatos: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD
        padroes = [
            (r'(\d{2})[/-](\d{2})[/-](\d{4})', '%d/%m/%Y'),  # DD/MM/YYYY
            (r'(\d{4})[/-](\d{2})[/-](\d{2})', '%Y-%m-%d'),  # YYYY-MM-DD
        ]
        
        for padrao, formato in padroes:
            match = re.match(padrao, data_str.strip())
            if match:
                try:
                    if formato == '%d/%m/%Y':
                        dia, mes, ano = match.groups()
                        data = datetime.strptime(f"{dia}/{mes}/{ano}", formato)
                    else:
                        data = datetime.strptime(data_str.strip(), formato)
                    
                    # Verifica se data não é muito antiga ou futura
                    hoje = datetime.now()
                    if data.year < 2000 or data.year > hoje.year + 1:
                        return None, f"Ano inválido: {data.year}"
                    
                    return data.strftime('%Y-%m-%d'), None
                except ValueError:
                    return None, "Data inválida (dia/mês incorretos)"
        
        return None, "Formato inválido. Use: DD/MM/AAAA ou AAAA-MM-DD"
    
    def adicionar_transacao(self, tipo, valor, categoria, descricao='', data=None):
        """Adiciona uma nova transação com validações"""
        transacao = {
            'id': len(self.transacoes) + 1,
            'tipo': tipo,
            'valor': float(valor),
            'categoria': categoria,
            'descricao': descricao,
            'data': data
        }
        
        self.transacoes.append(transacao)
        self.salvar_dados()
        data_formatada = datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%Y')
        print(f"\n✅ Transação adicionada com sucesso!")
        print(f"   {tipo.upper()}: R$ {valor:.2f} | {categoria} | {data_formatada}")
    
    def listar_transacoes(self, mes=None, ano=None):
        """Lista transações filtradas por mês/ano"""
        if mes is None:
            mes = datetime.now().month
        if ano is None:
            ano = datetime.now().year
        
        try:
            filtradas = [t for t in self.transacoes 
                         if datetime.strptime(t['data'], '%Y-%m-%d').month == mes
                         and datetime.strptime(t['data'], '%Y-%m-%d').year == ano]
        except (ValueError, KeyError) as e:
            print(f"❌ Erro ao filtrar transações: {e}")
            return []
        
        if not filtradas:
            print(f"\n📭 Nenhuma transação encontrada para {mes:02d}/{ano}")
            return []
        
        print(f"\n📊 Transações de {mes:02d}/{ano}:")
        print("-" * 90)
        print(f"{'Data':<12} {'Tipo':<10} {'Categoria':<18} {'Valor':>12} {'Descrição':<30}")
        print("-" * 90)
        
        for t in sorted(filtradas, key=lambda x: x['data']):
            simbolo = "➕ Receita" if t['tipo'] == 'receita' else "➖ Despesa"
            valor_fmt = f"R$ {t['valor']:>8.2f}"
            desc = t['descricao'][:27] + '...' if len(t['descricao']) > 30 else t['descricao']
            # Converter data de YYYY-MM-DD para DD/MM/YYYY
            data_formatada = datetime.strptime(t['data'], '%Y-%m-%d').strftime('%d/%m/%Y')
            print(f"{data_formatada:<12} {simbolo:<10} {t['categoria']:<18} {valor_fmt:>12} {desc:<30}")
        
        print("-" * 90)
        return filtradas
    
    def analisar_gastos(self, mes=None, ano=None):
        """Módulo Analytics - Detecta padrões e consumo excessivo"""
        if mes is None:
            mes = datetime.now().month
        if ano is None:
            ano = datetime.now().year
        
        transacoes_mes = [t for t in self.transacoes 
                          if datetime.strptime(t['data'], '%Y-%m-%d').month == mes
                          and datetime.strptime(t['data'], '%Y-%m-%d').year == ano]
        
        if not transacoes_mes:
            print(f"\n📭 Nenhuma transação para analisar em {mes:02d}/{ano}")
            return None
        
        receitas = sum(t['valor'] for t in transacoes_mes if t['tipo'] == 'receita')
        despesas = sum(t['valor'] for t in transacoes_mes if t['tipo'] == 'despesa')
        saldo = receitas - despesas
        
        gastos_categoria = defaultdict(float)
        for t in transacoes_mes:
            if t['tipo'] == 'despesa':
                gastos_categoria[t['categoria']] += t['valor']
        
        print(f"\n{'='*90}")
        print(f"💰 ANÁLISE FINANCEIRA - {mes:02d}/{ano}".center(90))
        print(f"{'='*90}")
        print(f"\n{'Receitas:':<20} R$ {receitas:>12,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"{'Despesas:':<20} R$ {despesas:>12,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"{'-'*90}")
        
        saldo_fmt = f"R$ {abs(saldo):>12,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        if saldo >= 0:
            print(f"{'Saldo Positivo:':<20} {saldo_fmt} ✅")
        else:
            print(f"{'Saldo Negativo:':<20} {saldo_fmt} ⚠️")
        
        if despesas > 0:
            print(f"\n📈 Distribuição de Gastos por Categoria:")
            print("-" * 90)
            categorias_ordenadas = sorted(gastos_categoria.items(), key=lambda x: x[1], reverse=True)
            
            for cat, valor in categorias_ordenadas:
                percentual = (valor / despesas) * 100
                barra = '█' * int(percentual / 2)
                valor_fmt = f"R$ {valor:>8,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                print(f"  {cat:<18} {valor_fmt:>15} ({percentual:5.1f}%) {barra}")
            
            cat_maior = categorias_ordenadas[0]
            print(f"\n🔍 INSIGHT: Maior gasto em '{cat_maior[0]}' - R$ {cat_maior[1]:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            
            if cat_maior[1] / despesas > 0.4:
                print(f"⚠️  ALERTA: '{cat_maior[0]}' representa {(cat_maior[1]/despesas*100):.1f}% dos gastos!")
            
            if receitas > 0:
                taxa_economia = (saldo / receitas) * 100
                print(f"\n💹 Taxa de Economia: {taxa_economia:.1f}%", end='')
                if taxa_economia < 0:
                    print(" 🔴 (Gastando mais que ganha)")
                elif taxa_economia < 10:
                    print(" 🟡 (Baixa)")
                elif taxa_economia < 20:
                    print(" 🟢 (Boa)")
                else:
                    print(" 🟢🟢 (Excelente!)")
        
        return {
            'receitas': receitas,
            'despesas': despesas,
            'saldo': saldo,
            'gastos_categoria': dict(gastos_categoria)
        }
    
    def prever_proximo_mes(self):
        """Módulo Preditivo - Estima balanço futuro baseado em histórico"""
        hoje = datetime.now()
        historico = []
        
        for i in range(1, 4):
            data_ref = hoje - timedelta(days=30*i)
            trans = [t for t in self.transacoes 
                    if datetime.strptime(t['data'], '%Y-%m-%d').month == data_ref.month
                    and datetime.strptime(t['data'], '%Y-%m-%d').year == data_ref.year]
            
            if trans:
                receitas = sum(t['valor'] for t in trans if t['tipo'] == 'receita')
                despesas = sum(t['valor'] for t in trans if t['tipo'] == 'despesa')
                historico.append({'receitas': receitas, 'despesas': despesas, 'mes': data_ref.strftime('%m/%Y')})
        
        if len(historico) < 2:
            print(f"\n{'='*90}")
            print("🔮 PREVISÃO PARA O PRÓXIMO MÊS".center(90))
            print(f"{'='*90}")
            print("\n⚠️  Dados insuficientes para fazer previsão precisa.")
            print("💡 Dica: Registre transações por pelo menos 2 meses para ativar este recurso.")
            return None
        
        media_receitas = statistics.mean([h['receitas'] for h in historico])
        media_despesas = statistics.mean([h['despesas'] for h in historico])
        saldo_previsto = media_receitas - media_despesas
        
        desvio_receitas = statistics.stdev([h['receitas'] for h in historico]) if len(historico) > 1 else 0
        desvio_despesas = statistics.stdev([h['despesas'] for h in historico]) if len(historico) > 1 else 0
        
        proximo_mes = (hoje.month % 12) + 1
        proximo_ano = hoje.year if hoje.month < 12 else hoje.year + 1
        
        print(f"\n{'='*90}")
        print(f"🔮 PREVISÃO PARA {proximo_mes:02d}/{proximo_ano}".center(90))
        print(f"{'='*90}")
        print(f"\n📊 Baseado em {len(historico)} meses de histórico: {', '.join([h['mes'] for h in historico])}")
        print(f"\n{'Receita esperada:':<25} R$ {media_receitas:>12,.2f} (±{desvio_receitas:,.2f})".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"{'Despesa esperada:':<25} R$ {media_despesas:>12,.2f} (±{desvio_despesas:,.2f})".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"{'-'*90}")
        
        if saldo_previsto >= 0:
            print(f"{'Saldo previsto:':<25} R$ {saldo_previsto:>12,.2f} ✅".replace(',', 'X').replace('.', ',').replace('X', '.'))
            print(f"\n🎉 Parabéns! Você deve terminar o mês com saldo positivo!")
        else:
            print(f"{'Déficit previsto:':<25} R$ {abs(saldo_previsto):>12,.2f} ⚠️".replace(',', 'X').replace('.', ',').replace('X', '.'))
            print(f"\n⚠️  ALERTA: Possível déficit de R$ {abs(saldo_previsto):,.2f}!".replace(',', 'X').replace('.', ',').replace('X', '.'))
            print(f"💡 Sugestão: Reduza gastos ou busque receita extra de R$ {abs(saldo_previsto):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        return {
            'receita_prevista': media_receitas,
            'despesa_prevista': media_despesas,
            'saldo_previsto': saldo_previsto
        }
    
    def gerar_recomendacoes(self):
        """Módulo Recomendador - Gera insights e estratégias personalizadas"""
        analise = self.analisar_gastos()
        
        if not analise:
            return
        
        print(f"\n{'='*90}")
        print("💡 RECOMENDAÇÕES INTELIGENTES".center(90))
        print(f"{'='*90}\n")
        
        recomendacoes = []
        
        # Recomendação 1: Taxa de economia
        if analise['receitas'] > 0:
            taxa_economia = (analise['saldo'] / analise['receitas']) * 100
            
            if taxa_economia < 0:
                recomendacoes.append({
                    'prioridade': '🔴 CRÍTICO',
                    'titulo': 'Você está gastando mais do que ganha!',
                    'acao': f'Corte imediatamente R$ {abs(analise['saldo']):,.2f} em despesas'.replace(',', 'X').replace('.', ',').replace('X', '.')
                })
            elif taxa_economia < 10:
                recomendacoes.append({
                    'prioridade': '🟡 ATENÇÃO',
                    'titulo': f'Taxa de economia baixa ({taxa_economia:.1f}%)',
                    'acao': f'Meta ideal: economizar 20% da receita (R$ {analise["receitas"]*0.20:,.2f})'.replace(',', 'X').replace('.', ',').replace('X', '.')
                })
            elif taxa_economia >= 20:
                recomendacoes.append({
                    'prioridade': '🟢 PARABÉNS',
                    'titulo': f'Excelente taxa de economia ({taxa_economia:.1f}%)!',
                    'acao': f'Considere investir os R$ {analise["saldo"]:,.2f} economizados'.replace(',', 'X').replace('.', ',').replace('X', '.')
                })
        
        # Recomendação 2: Categoria problemática
        if analise['gastos_categoria'] and analise['despesas'] > 0:
            cat_maior = max(analise['gastos_categoria'].items(), key=lambda x: x[1])
            percentual_cat = (cat_maior[1] / analise['despesas']) * 100
            
            if percentual_cat > 35:
                reducao_sugerida = cat_maior[1] * 0.15
                recomendacoes.append({
                    'prioridade': '🟡 OPORTUNIDADE',
                    'titulo': f'{cat_maior[0]} representa {percentual_cat:.1f}% dos gastos',
                    'acao': f'Tente reduzir 15% = economia de R$ {reducao_sugerida:,.2f}/mês'.replace(',', 'X').replace('.', ',').replace('X', '.')
                })
        
        # Recomendação 3: Meta de economia
        if analise['receitas'] > 0:
            economia_sugerida = analise['receitas'] * 0.20
            gasto_maximo = analise['receitas'] - economia_sugerida
            
            if analise['despesas'] > gasto_maximo:
                recomendacoes.append({
                    'prioridade': '🎯 META',
                    'titulo': 'Estabeleça um teto de gastos',
                    'acao': f'Gasto máximo ideal: R$ {gasto_maximo:,.2f} (está em R$ {analise["despesas"]:,.2f})'.replace(',', 'X').replace('.', ',').replace('X', '.')
                })
        
        # Exibir recomendações
        for i, rec in enumerate(recomendacoes, 1):
            print(f"{i}. {rec['prioridade']} | {rec['titulo']}")
            print(f"   → {rec['acao']}\n")
        
        if not recomendacoes:
            print("✅ Suas finanças estão equilibradas! Continue assim! 🎉\n")
    
    def deletar_transacao(self, transacao_id):
        """Deleta uma transação pelo ID"""
        transacao = next((t for t in self.transacoes if t['id'] == transacao_id), None)
        
        if not transacao:
            print(f"❌ Transação #{transacao_id} não encontrada")
            return False
        
        # Mostra detalhes da transação
        data_formatada = datetime.strptime(transacao['data'], '%Y-%m-%d').strftime('%d/%m/%Y')
        print(f"\n🗑️  Transação a ser deletada:")
        print(f"   ID: {transacao['id']}")
        print(f"   Tipo: {transacao['tipo'].upper()}")
        print(f"   Valor: R$ {transacao['valor']:.2f}")
        print(f"   Categoria: {transacao['categoria']}")
        print(f"   Descrição: {transacao['descricao']}")
        print(f"   Data: {data_formatada}")
        
        confirma = input("\n⚠️  Tem certeza que deseja deletar? (S/n): ").strip().lower()
        
        if confirma == 's':
            self.transacoes.remove(transacao)
            self.salvar_dados()
            print("✅ Transação deletada com sucesso!")
            return True
        else:
            print("❌ Operação cancelada")
            return False
    
    def editar_transacao(self, transacao_id):
        """Edita uma transação existente"""
        transacao = next((t for t in self.transacoes if t['id'] == transacao_id), None)
        
        if not transacao:
            print(f"❌ Transação #{transacao_id} não encontrada")
            return False
        
        # Mostra detalhes atuais
        data_formatada = datetime.strptime(transacao['data'], '%Y-%m-%d').strftime('%d/%m/%Y')
        print(f"\n✏️  Editando transação #{transacao_id}")
        print("="*90)
        print(f"Tipo: {transacao['tipo'].upper()}")
        print(f"Valor atual: R$ {transacao['valor']:.2f}")
        print(f"Categoria atual: {transacao['categoria']}")
        print(f"Descrição atual: {transacao['descricao']}")
        print(f"Data atual: {data_formatada}")
        print("\n💡 Pressione ENTER para manter o valor atual")
        print("-"*90)
        
        try:
            # Editar valor
            novo_valor = input(f"\n💵 Novo valor (atual: R$ {transacao['valor']:.2f}): ").strip()
            if novo_valor:
                transacao['valor'] = self.validar_valor(novo_valor)
            
            # Editar categoria
            nova_categoria = input(f"📁 Nova categoria (atual: {transacao['categoria']}): ").strip()
            if nova_categoria:
                categoria_validada, aviso = self.validar_categoria(nova_categoria, transacao['tipo'])
                if aviso:
                    print(aviso)
                    confirma = input("   Deseja continuar? (S/n): ").strip().lower()
                    if confirma != 'n':
                        transacao['categoria'] = categoria_validada
                else:
                    transacao['categoria'] = categoria_validada
            
            # Editar descrição
            nova_descricao = input(f"📝 Nova descrição (atual: {transacao['descricao']}): ").strip()
            if nova_descricao:
                transacao['descricao'] = nova_descricao
            
            # Editar data
            nova_data = input(f"📅 Nova data (atual: {data_formatada}, formato: DD/MM/AAAA): ").strip()
            if nova_data:
                data_validada, erro_data = self.validar_data(nova_data)
                if erro_data:
                    print(f"❌ {erro_data} - Mantendo data original")
                else:
                    transacao['data'] = data_validada
            
            self.salvar_dados()
            data_final = datetime.strptime(transacao['data'], '%Y-%m-%d').strftime('%d/%m/%Y')
            print("\n✅ Transação editada com sucesso!")
            print(f"   Valor: R$ {transacao['valor']:.2f}")
            print(f"   Categoria: {transacao['categoria']}")
            print(f"   Descrição: {transacao['descricao']}")
            print(f"   Data: {data_final}")
            return True
            
        except ValueError as e:
            print(f"❌ Erro: {e}")
            print("Edição cancelada")
            return False
    
    def listar_transacoes_para_gerenciar(self, mes=None, ano=None):
        """Lista transações com IDs para facilitar gerenciamento"""
        if mes is None:
            mes = datetime.now().month
        if ano is None:
            ano = datetime.now().year
        
        try:
            filtradas = [t for t in self.transacoes 
                         if datetime.strptime(t['data'], '%Y-%m-%d').month == mes
                         and datetime.strptime(t['data'], '%Y-%m-%d').year == ano]
        except (ValueError, KeyError) as e:
            print(f"❌ Erro ao filtrar transações: {e}")
            return []
        
        if not filtradas:
            print(f"\n📭 Nenhuma transação encontrada para {mes:02d}/{ano}")
            return []
        
        print(f"\n📋 Transações de {mes:02d}/{ano}:")
        print("="*90)
        print(f"{'ID':<5} {'Data':<12} {'Tipo':<10} {'Categoria':<18} {'Valor':>12} {'Descrição':<25}")
        print("-"*90)
        
        for t in sorted(filtradas, key=lambda x: x['data']):
            simbolo = "Receita" if t['tipo'] == 'receita' else "Despesa"
            valor_fmt = f"R$ {t['valor']:>8.2f}"
            desc = t['descricao'][:22] + '...' if len(t['descricao']) > 25 else t['descricao']
            # Converter data de YYYY-MM-DD para DD/MM/YYYY
            data_formatada = datetime.strptime(t['data'], '%Y-%m-%d').strftime('%d/%m/%Y')
            print(f"{t['id']:<5} {data_formatada:<12} {simbolo:<10} {t['categoria']:<18} {valor_fmt:>12} {desc:<25}")
        
        print("="*90)
        return filtradas
    
    def dashboard_simples(self):
        """Exibe um dashboard textual completo"""
        analise = self.analisar_gastos()
        
        if not analise:
            return
        
        print(f"\n{'='*90}")
        print("📊 DASHBOARD FINTRACK".center(90))
        print(f"{'='*90}\n")
        
        # Barra de progresso do orçamento
        if analise['receitas'] > 0:
            uso_orcamento = min((analise['despesas'] / analise['receitas']) * 100, 100)
            barra_cheia = int(uso_orcamento / 2)
            barra_vazia = 50 - barra_cheia
            
            print(f"💳 Uso do Orçamento Mensal: {uso_orcamento:.1f}%")
            print(f"[{'█'*barra_cheia}{'░'*barra_vazia}] {analise['despesas']:,.2f}/{analise['receitas']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            
            if uso_orcamento <= 70:
                print("✅ Uso saudável do orçamento")
            elif uso_orcamento <= 90:
                print("⚠️  Atenção: Orçamento em 90%")
            elif uso_orcamento <= 100:
                print("🔴 ALERTA: Orçamento quase esgotado!")
            else:
                print("🔴🔴 CRÍTICO: Você excedeu seu orçamento!")
            
            print()
        
        # Status geral
        print("📈 Status Financeiro:")
        if analise['saldo'] > 0:
            print(f"   ✅ Saldo positivo de R$ {analise['saldo']:,.2f}".replace(','))


def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def pausar():
    """Pausa e aguarda usuário pressionar ENTER"""
    input("\n💬 Pressione ENTER para continuar...")


def obter_numero(mensagem, permitir_vazio=False, valor_min=None, valor_max=None):
    """Solicita entrada numérica com validação robusta"""
    while True:
        try:
            entrada = input(mensagem).strip()
            
            if permitir_vazio and entrada == '':
                return None
            
            # Remove formatação comum
            entrada = entrada.replace('R$', '').replace(' ', '').replace(',', '.')
            
            # Remove múltiplos pontos
            partes = entrada.split('.')
            if len(partes) > 2:
                entrada = ''.join(partes[:-1]) + '.' + partes[-1]
            
            valor = float(entrada)
            
            if valor_min is not None and valor < valor_min:
                print(f"❌ Valor deve ser maior que {valor_min}")
                continue
            
            if valor_max is not None and valor > valor_max:
                print(f"❌ Valor deve ser menor que {valor_max}")
                continue
            
            return valor
            
        except ValueError:
            print("❌ Digite um número válido (ex: 150 ou 150.50)")
            if permitir_vazio:
                print("   Ou pressione ENTER para usar o padrão")


def obter_inteiro(mensagem, permitir_vazio=False, valor_min=None, valor_max=None):
    """Solicita entrada de número inteiro com validação"""
    while True:
        try:
            entrada = input(mensagem).strip()
            
            if permitir_vazio and entrada == '':
                return None
            
            valor = int(entrada)
            
            if valor_min is not None and valor < valor_min:
                print(f"❌ Valor deve ser maior ou igual a {valor_min}")
                continue
            
            if valor_max is not None and valor > valor_max:
                print(f"❌ Valor deve ser menor ou igual a {valor_max}")
                continue
            
            return valor
            
        except ValueError:
            print("❌ Digite um número inteiro válido")
            if permitir_vazio:
                print("   Ou pressione ENTER para usar o padrão")


def menu_principal():
    """Interface de menu do sistema com validações robustas"""
    sistema = FinTrack()
    
    while True:
        limpar_tela()
        print(f"\n{'='*90}")
        print("💰 FINTRACK - Sistema Inteligente de Controle Financeiro".center(90))
        print(f"{'='*90}\n")
        print("1. ➕ Adicionar Receita")
        print("2. ➖ Adicionar Despesa")
        print("3. 📋 Listar Transações")
        print("4. 📊 Analisar Gastos (Analytics)")
        print("5. 🔮 Previsão Próximo Mês")
        print("6. 💡 Recomendações Inteligentes")
        print("7. 📈 Dashboard Completo")
        print("8. ✏️  Editar Transação")
        print("9. 🗑️  Deletar Transação")
        print("0. 🚪 Sair")
        print(f"\n{'='*90}")
        
        opcao = input("\n👉 Escolha uma opção: ").strip()
        
        if opcao == '1':
            limpar_tela()
            print("\n➕ ADICIONAR RECEITA")
            print("="*90)
            print(f"Categorias disponíveis: {', '.join(sistema.categorias_padrao['receita'])}")
            print("-"*90)
            
            try:
                valor = obter_numero("💵 Valor: R$ ", valor_min=0, valor_max=1000000000)
                categoria = input("📁 Categoria: ").strip()
                
                categoria_validada, aviso = sistema.validar_categoria(categoria, 'receita')
                if aviso:
                    print(aviso)
                    confirma = input("   Deseja continuar? (S/n): ").strip().lower()
                    if confirma == 'n':
                        print("❌ Operação cancelada")
                        pausar()
                        continue
                
                descricao = input("📝 Descrição (opcional): ").strip()
                
                data_input = input("📅 Data (DD/MM/AAAA ou ENTER para hoje): ").strip()
                data_validada, erro_data = sistema.validar_data(data_input)
                
                if erro_data:
                    print(f"❌ {erro_data}")
                    pausar()
                    continue
                
                sistema.adicionar_transacao('receita', valor, categoria_validada, descricao, data_validada)
                
            except KeyboardInterrupt:
                print("\n\n❌ Operação cancelada pelo usuário")
            except Exception as e:
                print(f"\n❌ Erro inesperado: {e}")
            
            pausar()
        
        elif opcao == '2':
            limpar_tela()
            print("\n➖ ADICIONAR DESPESA")
            print("="*90)
            print(f"Categorias disponíveis: {', '.join(sistema.categorias_padrao['despesa'])}")
            print("-"*90)
            
            try:
                valor = obter_numero("💵 Valor: R$ ", valor_min=0, valor_max=1000000000)
                categoria = input("📁 Categoria: ").strip()
                
                categoria_validada, aviso = sistema.validar_categoria(categoria, 'despesa')
                if aviso:
                    print(aviso)
                    confirma = input("   Deseja continuar? (S/n): ").strip().lower()
                    if confirma == 'n':
                        print("❌ Operação cancelada")
                        pausar()
                        continue
                
                descricao = input("📝 Descrição (opcional): ").strip()
                
                data_input = input("📅 Data (DD/MM/AAAA ou ENTER para hoje): ").strip()
                data_validada, erro_data = sistema.validar_data(data_input)
                
                if erro_data:
                    print(f"❌ {erro_data}")
                    pausar()
                    continue
                
                sistema.adicionar_transacao('despesa', valor, categoria_validada, descricao, data_validada)
                
            except KeyboardInterrupt:
                print("\n\n❌ Operação cancelada pelo usuário")
            except Exception as e:
                print(f"\n❌ Erro inesperado: {e}")
            
            pausar()
        
        elif opcao == '3':
            limpar_tela()
            mes = obter_inteiro("📅 Mês (1-12, ENTER para mês atual): ", permitir_vazio=True, valor_min=1, valor_max=12)
            ano = obter_inteiro("📅 Ano (ENTER para ano atual): ", permitir_vazio=True, valor_min=2000, valor_max=2100)
            sistema.listar_transacoes(mes, ano)
            pausar()
        
        elif opcao == '4':
            limpar_tela()
            sistema.analisar_gastos()
            pausar()
        
        elif opcao == '5':
            limpar_tela()
            sistema.prever_proximo_mes()
            pausar()
        
        elif opcao == '6':
            limpar_tela()
            sistema.gerar_recomendacoes()
            pausar()
        
        elif opcao == '7':
            limpar_tela()
            sistema.dashboard_simples()
            pausar()
        
        elif opcao == '8':
            limpar_tela()
            print("\n✏️  EDITAR TRANSAÇÃO")
            print("="*90)
            
            mes = obter_inteiro("📅 Mês (1-12, ENTER para mês atual): ", permitir_vazio=True, valor_min=1, valor_max=12)
            ano = obter_inteiro("📅 Ano (ENTER para ano atual): ", permitir_vazio=True, valor_min=2000, valor_max=2100)
            
            transacoes = sistema.listar_transacoes_para_gerenciar(mes, ano)
            
            if transacoes:
                transacao_id = obter_inteiro("\n🔢 Digite o ID da transação para editar (0 para cancelar): ", valor_min=0)
                if transacao_id > 0:
                    sistema.editar_transacao(transacao_id)
            
            pausar()
        
        elif opcao == '9':
            limpar_tela()
            print("\n🗑️  DELETAR TRANSAÇÃO")
            print("="*90)
            
            mes = obter_inteiro("📅 Mês (1-12, ENTER para mês atual): ", permitir_vazio=True, valor_min=1, valor_max=12)
            ano = obter_inteiro("📅 Ano (ENTER para ano atual): ", permitir_vazio=True, vdiralor_min=2000, valor_max=2100)
            
            transacoes = sistema.listar_transacoes_para_gerenciar(mes, ano)
            
            if transacoes:
                transacao_id = obter_inteiro("\n🔢 Digite o ID da transação para deletar (0 para cancelar): ", valor_min=0)
                if transacao_id > 0:
                    sistema.deletar_transacao(transacao_id)
            
            pausar()
        
        elif opcao == '0':
            limpar_tela()
            print("\n" + "="*90)
            print("👋 Obrigado por usar o FinTrack!".center(90))
            print("💰 Cuide bem das suas finanças!".center(90))
            print("="*90 + "\n")
            break
        
        else:
            print("\n❌ Opção inválida! Escolha um número de 0 a 9")
            pausar()


if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Programa encerrado pelo usuário. Até logo!")
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        print("Por favor, reporte este erro ao desenvolvedor.")
