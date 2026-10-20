from datetime import datetime, timedelta
import json
import os
import math
import streamlit as st

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
    "v_entretela": 6.50,        
    "v_argola": 4.50,           
    "v_gancho": 0.80,           
    "v_terminal": 2.50,         
    "v_rodizio": 0.60,          
    "v_limitador": 3.00,        
    "v_cordao": 5.00
}

st.title(' Orçamentos Mauá by Almir Jr v29')
st.caption('Sistema de Orçamentos Conectado em Nuvem')

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

        v_suporte = st.number_input('Valor Unitário Suporte (R$):', min_value=0.0, value=12.0, step=1.0, disabled=not is_varao)

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
        
        if st.button('💾 SALVAR NO HISTÓRICO', type='primary', use_container_width=True):
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
