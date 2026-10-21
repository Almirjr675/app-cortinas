from datetime import datetime, timedelta
import json
import os
import math
import streamlit as st
from datetime import datetime, timedelta
import json
import os
import math
import streamlit as st

# 🆕 NOVAS IMPORTAÇÕES PARA O PDF (Adicione aqui)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# ==========================================================
# 🔐 CONFIGURAÇÕES E GERENCIAMENTO DE USUÁRIOS
# ==========================================================
USUARIOS_PERMITIDOS = {
    "maua": "mauamaua",
    "vendedor1": "senha456",
    "admin": "admin2026"
}

def verificar_login(usuario, senha):
    if usuario in USUARIOS_PERMITIDOS and USUARIOS_PERMITIDOS[usuario] == senha:
        return True
    return False

def renderizar_tela_login():
    st.markdown(
        """
        <style>
        .login-box {
            padding: 2rem; border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-top: 5%;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.title(' Login Mauá Tecidos')
        st.subheader('🔒 Controle de Acesso')
        usuario_input = st.text_input('Usuário:', placeholder='Digite seu usuário...')
        senha_input = st.text_input('Senha:', type='password', placeholder='Digite sua senha...')
        if st.button('Entrar', type='primary', use_container_width=True):
            if verificar_login(usuario_input.lower().strip(), senha_input):
                st.session_state['conectado'] = True
                st.session_state['usuario_atual'] = usuario_input.lower().strip()
                st.success('Acesso liberado!')
                st.rerun()
            else:
                st.error('Usuário ou senha incorretos. Tente novamente.')
        st.markdown('</div>', unsafe_allow_html=True)
        # ... Aqui termina a sua função antiga renderizar_tela_login() ...

# 🆕 COLE A FUNÇÃO GERADORA DE PDF BEM AQUI:
def gerar_pdf_orcamento(dados_pdf):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40,
        title=f"Orcamento_{dados_pdf['cliente']}"
    )
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle('TituloDoc', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor("#1A365D"), spaceAfter=5)
    style_sub = ParagraphStyle('SubDoc', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#4A5568"), spaceAfter=15)
    style_secao = ParagraphStyle('SecaoDoc', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor("#2B6CB0"), spaceBefore=12, spaceAfter=8)
    style_texto = ParagraphStyle('TextoDoc', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor("#2D3748"), leading=14)
    style_th = ParagraphStyle('TableHeader', parent=styles['Normal'], fontSize=10, textColor=colors.white, fontName="Helvetica-Bold", alignment=1)
    style_td = ParagraphStyle('TableCell', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor("#2D3748"), alignment=0)
    style_td_val = ParagraphStyle('TableCellVal', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor("#2D3748"), alignment=2)
    
    # Novo estilo centralizado para o bloco de assinaturas
    style_assinatura = ParagraphStyle('AssinaDoc', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#2D3748"), alignment=1)

    story = []
    
    # 1. CABEÇALHO
    story.append(Paragraph("<b>MAUÁ TECIDOS</b> by Almir Jr", style_titulo))
    story.append(Paragraph(f"Orçamento Técnico de Cortinas | Data: {dados_pdf['data']} | Vendedor: {dados_pdf['vendedor']}", style_sub))
    story.append(Spacer(1, 5))
    
    # 2. DADOS DO CLIENTE
    story.append(Paragraph("📋 Identificação e Local de Instalação", style_secao))
    dados_cliente_html = f"<b>Cliente:</b> {dados_pdf['cliente']}<br/><b>WhatsApp:</b> {dados_pdf['telefone']}<br/><b>CPF:</b> {dados_pdf['cpf']}<br/><b>Endereço:</b> {dados_pdf['endereco']}"
    story.append(Paragraph(dados_cliente_html, style_texto))
    
    # 3. ESPECIFICAÇÕES DO PRODUTO
    story.append(Paragraph("📐 Especificações da Cortina", style_secao))
    dados_produto_html = f"<b>Ambiente:</b> {dados_pdf['ambiente']}<br/><b>Dimensões:</b> {dados_pdf['largura']:.2f}m x {dados_pdf['altura']:.2f}m<br/><b>Modelo:</b> {dados_pdf['modelo']} ({dados_pdf['franzimento']}x)<br/><b>Abertura:</b> {dados_pdf['abertura']}"
    story.append(Paragraph(dados_produto_html, style_texto))
    
    # 4. TABELA FINANCEIRA
    story.append(Paragraph("💰 Resumo Financeiro", style_secao))
    tabela_data = [
        [Paragraph("Descrição do Item", style_th), Paragraph("Valor", style_th)],
        [Paragraph("Confecção de Cortina sob medida (Tecidos, Aviamentos e Instalação)", style_td), Paragraph(f"R$ {dados_pdf['valor_total']:.2f}", style_td_val)],
        [Paragraph("<b>VALOR TOTAL DO PEDIDO</b>", style_td), Paragraph(f"<b>R$ {dados_pdf['valor_total']:.2f}</b>", style_td_val)]
    ]
    t_financeira = Table(tabela_data, colWidths=[380, 120])
    t_financeira.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor("#1A365D")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8), ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,-1), (1,-1), colors.HexColor("#F7FAFC")),
    ]))
    story.append(t_financeira)
    
    # 5. 🆕 FORMAS DE PAGAMENTO (Adicionado aqui)
    story.append(Paragraph("💳 Formas de Pagamento Aceitas", style_secao))
    formas_pagamento_html = """
    • <b>À Vista / PIX:</b> 5% de desconto sobre o valor total do pedido.<br/>
    • <b>Cartão de Crédito:</b> Em até 6x sem juros.<br/>
    • <b>Sinal:</b> 50% de entrada no ato do pedido + 50% antes da instalação.
    """
    story.append(Paragraph(formas_pagamento_html, style_texto))
    
    # 6. TERMOS E CONDIÇÕES
    story.append(Paragraph("📅 Termos, Condições e Entrega", style_secao))
    termos_html = f"• <b>Prazo Limite:</b> {dados_pdf['prazo_entrega']} (20 dias úteis).<br/>• <b>Obs:</b> {dados_pdf['observacoes'] if dados_pdf['observacoes'] else 'Nenhuma.'}<br/>• <b>Validade:</b> 15 dias."
    story.append(Paragraph(termos_html, style_texto))
    
    story.append(Spacer(1, 35)) # Dá um espaço confortável antes das assinaturas
    
    # 7. 🆕 CAMPO DE ASSINATURAS (Adicionado no rodapé)
    tabela_assinaturas_data = [
        [
            Paragraph("_______________________________________<br/><b>Mauá Tecidos</b><br/>Responsável/Gerente", style_assinatura),
            Paragraph("_______________________________________<br/><b>Aceite do Cliente</b><br/>De acordo com as especificações", style_assinatura)
        ]
    ]
    t_assinaturas = Table(tabela_assinaturas_data, colWidths=[250, 250])
    t_assinaturas.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_assinaturas)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ----------------------------------------------------------
# Logo abaixo segue a sua linha antiga: st.set_page_config(...)

# Configuração obrigatória do Streamlit
st.set_page_config(page_title='Orçamentos Cortinas', page_icon='🪟', layout='wide')

# Verificação de segurança (Bloqueio)
if 'conectado' not in st.session_state:
    st.session_state['conectado'] = False

if not st.session_state['conectado']:
    renderizar_tela_login()
    st.stop()  # Trava o código aqui caso não esteja logado


# 1. FUNÇÃO DE PRAZO
def calcular_prazo_entrega(data_inicial, dias_uteis=20):
    data_atual = data_inicial
    dias_contados = 0
    while dias_contados < dias_uteis:
        data_atual += timedelta(days=1)
        if data_atual.weekday() < 5:
            dias_contados += 1
    return data_atual.strftime('%d/%m/%Y')

st.set_page_config(page_title='Orçamentos Cortinas', page_icon='🪟', layout='wide')

# 2. BANCO DE DADOS EM NUVEM SIMULADO (Salva em arquivo persistente na nuvem para não apagar no deploy)
DB_FILE = "historico_orcamentos.json"

def carregar_dados_nuvem():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_dados_nuvem(novo_registro):
    dados = carregar_dados_nuvem()
    dados.insert(0, novo_registro) # Adiciona no topo (mais recente primeiro)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# TABELA DE PREÇOS DOS AVIAMENTOS INTERNOS DE CONFECÇÃO (Fixos de Fábrica)
TABELA_PRECOS_INTERNOS = {
    "v_entretela": 1.80,        
    "v_argola": 4.50,           
    "v_gancho": 0.80,           
    "v_terminal": 2.50,         
    "v_rodizio": 0.60,          
    "v_limitador": 3.00,        
    "v_cordao": 5.00
}
# Menu Lateral para dar Logout
with st.sidebar:
    st.write(f"👤 Conectado como: **{st.session_state['usuario_atual'].capitalize()}**")
    if st.button("Sair / Logout", type="secondary", use_container_width=True):
        st.session_state['conectado'] = False
        st.session_state['usuario_atual'] = None
        st.rerun()
# ... DAQUI PARA BAIXO SEGUE O RESTANTE DO SEU CÓDIGO ORIGINAL (Abas, col_dados, cálculos, etc)

st.title('Orçamentos Mauá Tecidos by Almir Jr v29')
st.caption('Sistema de Orçamentos para Cortinas')

aba_calculadora, aba_historico = st.tabs(['🧮 Novo Orçamento', '🗄️ Histórico Salvo'])

with aba_calculadora:
    col_dados, col_resultado = st.columns(2)

    with col_dados:
        st.subheader('📋 Identificação do Cliente e Medidas')
        
        cliente_rapido = st.text_input('Nome do Cliente (Identificação Rápida):', placeholder='Digite o nome do cliente aqui...')
        
        c1, c2, c3 = st.columns(3)
        with c1: vendedor = st.text_input('Nome do Vendedor:', placeholder='Ex: Almir')
        with c2: data_exibicao = st.text_input('Data do Orçamento:', value=datetime.now().strftime('%d/%m/%Y'), disabled=True)
        with c3: regiao = st.selectbox('Selecione a Região:', ['Região do ABC', 'Fora do ABC'])

        c4, c5, c6 = st.columns(3)
        with c4: ambiente = st.text_input('Ambiente:', placeholder='Ex: Sala de Estar')
        with c5: largura = st.number_input('Largura do Trilho/Varão (m):', min_value=0.1, value=2.0, step=0.1)
        with c6: altura = st.number_input('Altura da Janela (m):', min_value=0.1, value=2.6, step=0.1)
        
        st.markdown('---')
        st.subheader('🧵 Detalhes dos Tecidos')
        
        modelo = st.selectbox('Escolha o Modelo da Cortina:', [
            'Ilhós (Varão)', 
            'Argola (Varão)', 
            'Prega Americana (Varão)', 
            'Prega Macho (Varão)',
            'Franzido (Trilho)',
            'Wave (Trilho)'
        ])
        
        if modelo in ['Ilhós (Varão)', 'Argola (Varão)', 'Franzido (Trilho)']:
            franzimento = st.selectbox('Selecione a Quantidade de Franzido:', [2.0, 2.5, 3.0], index=1, format_func=lambda x: f"{x}x da largura")
        else: 
            franzimento = st.selectbox('Quantidade de Franzido (Travado):', [3.5], index=0, disabled=True, format_func=lambda x: f"{x}x da largura")
            
        tem_forro = st.checkbox('Adicionar Forro nesta cortina?', value=False)
        abertura = st.selectbox('Tipo de Abertura:', ['Ao meio', 'Sem abertura / Lateral'])

        st.markdown('**Tecido da Frente:**')
        ct1, ct2, ct3 = st.columns(3)
        with ct1: cod_tec_frente = st.text_input('Código Tecido Frente:', value='TEC-01')
        with ct2: nome_tec_frente = st.text_input('Nome Tecido Frente:', value='Linho Flame')
        with ct3: v_tec_frente = st.number_input('Preço/m Frente (R$):', min_value=0.0, value=60.0, step=5.0)

        if tem_forro:
            st.markdown('**Tecido do Forro:**')
            cf1, cf2, cf3 = st.columns(3)
            with cf1: cod_tec_forro = st.text_input('Código Forro:', value='FOR-01')
            with cf2: nome_tec_forro = st.text_input('Nome Forro:', value='Forro Microfibra')
            with cf3: v_tec_forro = st.number_input('Preço/m Forro (R$):', min_value=0.0, value=35.0, step=5.0)
        else:
            cod_tec_forro, nome_tec_forro, v_tec_forro = "N/A", "N/A", 0.0

        st.markdown('---')
        st.subheader('🛠️ Acessórios')
        
        tipo_estrutura_txt = "Varão" if 'Varão' in modelo else "Trilho"
        st.markdown(f'**Barra Principal ({tipo_estrutura_txt}):**')
        ce1, ce2, ce3 = st.columns(3)
        with ce1: cod_barra = st.text_input(f'Código do {tipo_estrutura_txt}:', value='FERR-01')
        with ce2: nome_barra = st.text_input(f'Nome do {tipo_estrutura_txt}:', value=f'{tipo_estrutura_txt} Alumínio Padrão')
        with ce3: 
            if 'Varão' in modelo:
                v_varao = st.number_input('Preço/m Varão (R$):', min_value=0.0, value=40.0, step=5.0)
                v_trilho = 0.0
            else:
                v_trilho = st.number_input('Preço/m Trilho (R$):', min_value=0.0, value=35.0, step=5.0)
                v_varao = 0.0

        st.markdown('**Componentes de Argolas / Ilhós:**')
        c_sub1, c_sub2 = st.columns(2)
        with c_sub1:
            is_ilhos = (modelo == 'Ilhós (Varão)')
            cod_ilhos = st.text_input('Código do Ilhós:', value='ILH-01', disabled=not is_ilhos)
            v_ilhos = st.number_input('Valor Unitário Ilhós (R$):', min_value=0.0, value=3.50, step=0.50, disabled=not is_ilhos)
        with c_sub2:
            is_argola = ('Argola' in modelo or 'Prega' in modelo)
            cod_argola = st.text_input('Código da Argola:', value='ARG-01', disabled=not is_argola)
            v_argola_manual = st.number_input('Valor Unitário Argola (R$):', min_value=0.0, value=4.50, step=0.50, disabled=not is_argola)

        st.markdown('**Suportes e Ponteiras:**')
        is_varao = ('Varão' in modelo)
        
        c_acc1, c_acc2 = st.columns(2)
        with c_acc1:
            cod_suporte = st.text_input('Código do Suporte:', value='SUP-01', disabled=not is_varao)
            v_suporte = st.number_input('Valor Unitário Suporte (R$):', min_value=0.0, value=12.0, step=1.0, disabled=not is_varao)
            st.write("") 
            cod_ponteira_m = st.text_input('Código Ponteira (M):', value='PTM-01', disabled=not is_varao)
            v_ponteira_m = st.number_input('Valor Unitário Ponteira (M) (R$):', min_value=0.0, value=15.0, step=1.0, disabled=not is_varao)
        with c_acc2:
            st.write("") 
            st.write("") 
            st.write("")
            cod_ponteira_g = st.text_input('Código Ponteira (G):', value='PTG-01', disabled=not is_varao)
            v_ponteira_g = st.number_input('Valor Unitário Ponteira (G) (R$):', min_value=0.0, value=25.0, step=1.0, disabled=not is_varao)
        st.markdown('---')
        st.subheader('📝 Observações do Pedido')
        obs_pedido = st.text_area('Informações adicionais:', placeholder='Ex: Cliente vai retirar na loja, conferir estampa...', height=80)
        
        st.markdown('---')
        finalizar = st.checkbox('📝 Habilitar Cadastro Completo do Cliente', value=False)
        
        cliente_final, cpf_cliente, telefone_cliente, cep_cliente, endereco_cliente = '', 'Não Informado', 'Não Informado', 'Não Informado', 'Não Informado'
        if finalizar:
            cliente_final = st.text_input('Nome Completo do Cliente:')
            c_doc, c_tel = st.columns(2)
            with c_doc: cpf_cliente = st.text_input('CPF do Cliente:', placeholder='000.000.000-00')
            with c_tel: telefone_cliente = st.text_input('Telefone / WhatsApp:', placeholder='(11) 99999-9999')
            c_cep, c_end = st.columns(2)
            with c_cep: cep_cliente = st.text_input('CEP:', placeholder='00000-000')
            with c_end: endereco_cliente = st.text_input('Endereço de Instalação:')
        
        cliente_definitivo = cliente_final if (finalizar and cliente_final) else cliente_rapido
    # ==========================================================
    # ⚙️ LOGICA DA ENGENHARIA AUTOMÁTICA COM REGRA DE ALTURAS
    # ==========================================================
    largura_tecido_esticado = largura * franzimento
    usando_regra_alturas = altura > 2.50

    if usando_regra_alturas:
        qtd_alturas = math.ceil(largura_tecido_esticado / 2.80)
        comprimento_por_altura = altura + 0.30
        q_tec_frente = qtd_alturas * comprimento_por_altura
        q_tec_forro = q_tec_frente if tem_forro else 0.0
        q_entretela = largura_tecido_esticado  
    else:
        qtd_alturas = 1
        q_tec_frente = largura_tecido_esticado
        q_tec_forro = q_tec_frente if tem_forro else 0.0
        q_entretela = q_tec_frente

    # Inicialização das variáveis de quantidade
    q_ilhos = q_argola = q_gancho = q_terminal = q_rodizio = q_limitador = q_cordao = 0
    q_trilho = q_varao = q_suporte = q_ponteira_m = q_ponteira_g = 0

    tamanho_barra = largura + 0.20  
    
    if 'Varão' in modelo:
        q_varao = tamanho_barra
        q_suporte = 2 if largura <= 2.0 else 3  
        q_ponteira_m = 2 
    else:
        q_trilho = tamanho_barra
        q_terminal = 2 if abertura == 'Sem abertura / Lateral' else 4

    # Distribuição Física e Espaçamentos Técnicos de Engenharia
    if modelo == 'Ilhós (Varão)':
        calculo_cru = math.ceil(q_tec_frente / 0.13)
        q_ilhos = calculo_cru if calculo_cru % 2 == 0 else calculo_cru + 1
        
    elif modelo == 'Argola (Varão)':
        q_argola = math.ceil(q_varao / 0.10)
        q_gancho = q_argola  
        
    elif modelo in ['Prega Americana (Varão)', 'Prega Macho (Varão)']:
        q_argola = math.ceil(q_varao / 0.10)
        q_gancho = q_argola

    elif modelo == 'Franzido (Trilho)':
        q_rodizio = math.ceil(q_trilho / 0.08)
        
    elif modelo == 'Wave (Trilho)':
        q_cordao = largura
        q_rodizio = math.ceil(q_trilho / 0.05) 
        q_limitador = 2

    # ==========================================
    # 💰 CÁLCULOS FINANCEIROS DINÂMICOS
    # ==========================================
    total_frente = q_tec_frente * v_tec_frente
    total_forro = q_tec_forro * v_tec_forro
    
    calc_entretela = q_entretela * TABELA_PRECOS_INTERNOS["v_entretela"]
    
    # Multiplica pelo preço dinâmico da tela se o modelo exigir argolas
    calc_argola = q_argola * v_argola_manual if is_argola else 0.0
    
    calc_gancho = q_gancho * TABELA_PRECOS_INTERNOS["v_gancho"]
    calc_terminal = q_terminal * TABELA_PRECOS_INTERNOS["v_terminal"]
    calc_rodizio = q_rodizio * TABELA_PRECOS_INTERNOS["v_rodizio"]
    calc_limitador = q_limitador * TABELA_PRECOS_INTERNOS["v_limitador"]
    calc_cordao = q_cordao * TABELA_PRECOS_INTERNOS["v_cordao"]

    # Grupo 1 (Confecção)
    subtotal_grupo1 = total_frente + total_forro + calc_entretela + calc_argola + calc_gancho + calc_terminal + calc_rodizio + calc_limitador + calc_cordao
    valor_com_mao_de_obra = subtotal_grupo1 / 0.6 if subtotal_grupo1 > 0 else 0.0

    # Grupo 2 (Ferragens)
    calc_ilhos = q_ilhos * v_ilhos 
    calc_trilho = q_trilho * v_trilho
    calc_varao = q_varao * v_varao
    calc_suporte = q_suporte * v_suporte
    calc_ponteira = (q_ponteira_m * v_ponteira_m) + (q_ponteira_g * v_ponteira_g)

    # Taxa de Instalação
    if regiao == 'Região do ABC':
        taxa_instalacao = 100.0 if largura <= 3.0 else 200.0
    else:
        taxa_instalacao = 150.0 if largura <= 3.0 else 300.0

    soma_com_estruturais = valor_com_mao_de_obra + calc_ilhos + calc_trilho + calc_varao + calc_suporte + calc_ponteira + taxa_instalacao
    
    valor_final_cortina = soma_com_estruturais * 1.12
    data_limite_entrega = calcular_prazo_entrega(datetime.now())

    # ==========================================================
    # 💎 4. INTERFACE DA COLUNA DIREITA ORIGINAL RESTAURADA
    # ==========================================================
    with col_resultado:
        st.subheader('💰 Total')
        
        # Blocos métricos solicitados
        bx1, bx2 = st.columns(2)
        with bx1:
            st.metric(label="Valor Final do Orçamento", value=f"R$ {valor_final_cortina:,.2f}")
        with bx2:
            st.metric(label="Prazo de Entrega Estimado", value=data_limite_entrega)
            
        st.info(f'VALOR FINAL DO ORÇAMENTO: R$ {valor_final_cortina:.2f}')
        st.warning(f'📅 **Prazo Limite de Entrega:** {data_limite_entrega} (20 dias úteis após o pagamento)')
        
        if usando_regra_alturas:
            st.error(f'⚠️ **Atenção:** Altura ({altura}m) maior que 2.50m. O sistema calculou automaticamente o consumo usando **{qtd_alturas} alturas (panos)** de tecido emendados verticalmente.')

        st.markdown('### 📋 Detalhamento dos Itens')
        
        st.markdown('**🧵 Tecidos Utilizados:**')
        if q_tec_frente > 0: 
            st.write(f'• Frente: **[{cod_tec_frente}] {nome_tec_frente}** — {q_tec_frente:.2f}m x R$ {v_tec_frente:.2f} = R$ {total_frente:.2f}')
        if tem_forro and q_tec_forro > 0: 
            st.write(f'• Forro: **[{cod_tec_forro}] {nome_tec_forro}** — {q_tec_forro:.2f}m x R$ {v_tec_forro:.2f} = R$ {total_forro:.2f}')
            
        st.markdown('**⛓️ Aviamentos para confecção:**')
        if q_entretela > 0: st.write(f'• Entretela: {q_entretela:.2f}m x R$ {TABELA_PRECOS_INTERNOS["v_entretela"]:.2f} = R$ {calc_entretela:.2f}')
        if q_argola > 0: st.write(f'• Argolas/Argolas de Prega: **[{cod_argola}]** {q_argola} un x R$ {v_argola_manual:.2f} = R$ {calc_argola:.2f}')
        if q_gancho > 0: st.write(f'• Ganchos: {q_gancho} un x R$ {TABELA_PRECOS_INTERNOS["v_gancho"]:.2f} = R$ {calc_gancho:.2f}')
        if q_terminal > 0: st.write(f'• Terminais: {q_terminal} un x R$ {TABELA_PRECOS_INTERNOS["v_terminal"]:.2f} = R$ {calc_terminal:.2f}')
        if q_rodizio > 0: st.write(f'• Rodízios: {q_rodizio} un x R$ {TABELA_PRECOS_INTERNOS["v_rodizio"]:.2f} = R$ {calc_rodizio:.2f}')
        if q_limitador > 0: st.write(f'• Limitadores: {q_limitador} un x R$ {TABELA_PRECOS_INTERNOS["v_limitador"]:.2f} = R$ {calc_limitador:.2f}')
        if q_cordao > 0: st.write(f'• Cordão Wave: {q_cordao:.2f}m x R$ {TABELA_PRECOS_INTERNOS["v_cordao"]:.2f} = R$ {calc_cordao:.2f}')
        
        st.markdown('**🛠️ Acessórios para Instalação:**')
        if q_ilhos > 0: st.write(f'• Ilhós: **[{cod_ilhos}]** {q_ilhos} un x R$ {v_ilhos:.2f} = R$ {calc_ilhos:.2f}')
        if q_trilho > 0:
            st.write(f'• Trilho: **[{cod_barra}] {nome_barra}** — {q_trilho:.2f}m x R$ {v_trilho:.2f} = R$ {calc_trilho:.2f}')
        if q_varao > 0:
            st.write(f'• Varão: **[{cod_barra}] {nome_barra}** — {q_varao:.2f}m x R$ {v_varao:.2f} = R$ {calc_varao:.2f}')
        if q_suporte > 0: 
            st.write(f'• Suportes: **[{cod_suporte}]** {q_suporte} un x R$ {v_suporte:.2f} = R$ {calc_suporte:.2f}')
        if q_ponteira_m > 0: st.write(f'• Ponteira (M): **[{cod_ponteira_m}]** {q_ponteira_m} un x R$ {v_ponteira_m:.2f} = R$ {(q_ponteira_m * v_ponteira_m):.2f}')
        if q_ponteira_g > 0: st.write(f'• Ponteira (G): **[{cod_ponteira_g}]** {q_ponteira_g} un x R$ {v_ponteira_g:.2f} = R$ {(q_ponteira_g * v_ponteira_g):.2f}')
        st.write(f'• Taxa de Instalação ({regiao}): R$ {taxa_instalacao:.2f}')
        
        if obs_pedido:
            st.markdown('**📝 Observações:**')
            st.write(obs_pedido)

        with st.expander('🔍 Ver memória de cálculo'):
            if usando_regra_alturas:
                st.write(f'• *Cálculo de Alturas:* {largura_tecido_esticado:.2f}m de tecido esticado / 2.80m de rolo = {qtd_alturas} panos.')
                st.write(f'• *Consumo do Pano:* {qtd_alturas} panos x ({altura}m de altura + 0.30m bainhas) = {q_tec_frente:.2f}m de tecido comprado.')
            st.write(f'• Custo Insumos Base: R$ {subtotal_grupo1:.2f}')
            st.write(f'• Custo com Mão de Obra (/0.6): R$ {valor_com_mao_de_obra:.2f}')
            st.write(f'• Subtotal Geral: R$ {soma_com_estruturais:.2f}')
            st.write(f'• Lucro Adicional (12%): R$ {(valor_final_cortina - soma_com_estruturais):.2f}')
        
        st.markdown('---')
        
        if st.button('💾 SALVAR NO HISTÓRICO', type='primary', use_container_width=True, key="btn_salvar_historico_maua"):
            if not cliente_definitivo:
                st.error('Insira o nome do cliente para salvar.')
            else:
                try:
                    # MODIFICADO: Lógica de salvamento em JSON para nuvem estável
                    novo_registro = {
                        "data": datetime.now().strftime('%d/%m/%Y %H:%M'),
                        "vendedor": vendedor,
                        "cliente": cliente_definitivo,
                        "cpf": cpf_cliente,
                        "telefone": telefone_cliente,
                        "endereco": endereco_cliente,
                        "ambiente": ambiente,
                        "largura": largura,
                        "altura": altura,
                        "modelo": modelo,
                        "franzimento": franzimento,
                        "valor_total": valor_final_cortina
                    }
                    salvar_dados_nuvem(novo_registro)
                    st.success(f'Orçamento de {cliente_definitivo} salvo com sucesso na nuvem!')
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
                # ... Linhas antigas do botão de salvar ...
            # ... Lógica interna do botão que você já tem ...
            pass # (não apague o código que está aqui dentro)
                # ... Mantém todo o dicionário "dados_para_pdf" idêntico ...
                # ... Mantém todo o dicionário "dados_para_pdf" idêntico ...
        dados_para_pdf = {
            "data": datetime.now().strftime('%d/%m/%Y'),
            "vendedor": vendedor,
            "cliente": cliente_definitivo if cliente_definitivo else "Cliente Não Informado",
            "cpf": cpf_cliente, "telefone": telefone_cliente, "endereco": endereco_cliente,
            "ambiente": ambiente if ambiente else "Geral", "largura": largura, "altura": altura,
            "modelo": modelo, "franzimento": franzimento, "regiao": regiao,
            "valor_total": valor_final_cortina, "prazo_entrega": data_limite_entrega,
            "abertura": abertura, "observacoes": obs_pedido
        }
        
        pdf_gerado = gerar_pdf_orcamento(dados_para_pdf)
        
        st.write("") # dá um espacinho visual
        
        # 🌟 CORREÇÃO: Nome limpo para a chave dinâmica
        nome_limpo_cliente = dados_para_pdf['cliente'].lower().replace(' ', '_')
        
        # O download_button agora possui uma chave dinâmica e exclusiva baseada no cliente atual
        st.download_button(
            label="📥 GERAR ORÇAMENTO EM PDF",
            data=pdf_gerado,
            file_name=f"Orcamento_Maua_{nome_limpo_cliente}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key=f"btn_pdf_{nome_limpo_cliente}"  # <--- Garante ID único em qualquer aba ou recarregamento
        )


# 5. HISTÓRICO LOCAL EM NUVEM
with aba_historico:
    st.subheader('🗄️ Histórico Local de Orçamentos')
    # MODIFICADO: Busca os dados salvos em JSON
    dados = carregar_dados_nuvem()
    if not dados:
        st.info('Nenhum orçamento arquivado.')
    else:
        for idx, item in enumerate(dados):
            with st.expander(f"📋 Cód: {len(dados) - idx} | Cliente: {item['cliente']} | Total: R$ {item['valor_total']:.2f}"):
                st.write(f"**Data:** {item['data']}")
                st.write(f"**Vendedor:** {item['vendedor']}")
                st.write(f"**CPF:** {item['cpf']}")
                st.write(f"**Telefone:** {item['telefone']}")
                st.write(f"**Endereço:** {item['endereco']}")
                st.write(f"**Ambiente:** {item['ambiente']}")
                st.write(f"**Largura:** {item['largura']} m")
                st.write(f"**Altura:** {item['altura']} m")
                st.write(f"**Modelo:** {item['modelo']}")
                st.write(f"**Franzimento:** {item['franzimento']}x")
                st.write(f"**Valor Total do Orçamento:** R$ {item['valor_total']:.2f}")
