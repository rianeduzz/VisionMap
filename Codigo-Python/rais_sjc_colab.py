# Acesso ao código: o código Python está disponível no arquivo .py. Para visualizar e utilizar o código completo, é necessário clicar no ícone/botão de download e baixar o arquivo.

































# %% [markdown]
# # Base de estabelecimentos RAIS – São José dos Campos (SP)
#
# Notebook para o **Google Colab**. Ele lê o arquivo **RAIS_ESTAB_PUB.txt**
# (microdados RAIS Estabelecimentos, do Ministério do Trabalho e Emprego), que
# está no Google Drive **de outra pessoa**. Depois gera a base tratada só com
# **São José dos Campos**.
#
# **Etapa da sprint:** selecionar as fontes públicas, filtrar SJC, corrigir
# inconsistências, eliminar duplicidades, padronizar os campos, classificar as
# empresas e registrar a origem dos dados.
#
# **Entrega:** um Excel com filtros (base, resumo, log de qualidade, dicionário,
# fontes e backlog da sprint) e um CSV pronto para o painel, salvos no **seu** Drive.
#
# **Antes de começar:** o dono do arquivo precisa ter compartilhado com o seu
# e-mail, ou você precisa ter o link. Execute as células em ordem.

# %% [markdown]
# ## 1. Configuração
# * Se tiver o **link** do arquivo, cole em `LINK_ARQUIVO` (é o jeito mais garantido).
# * Se o arquivo foi compartilhado diretamente com o seu e-mail, pode deixar o
#   link vazio: o notebook procura pelo nome.
# * `ANO_BASE`: ano de referência da RAIS (vai para a base e para a aba Fontes).

# %%
NOME_ARQUIVO = "RAIS_ESTAB_PUB.txt"
LINK_ARQUIVO = ""        # ex.: "https://drive.google.com/file/d/XXXXXXXX/view?usp=sharing"
ANO_BASE     = ""        # ex.: "2024"  (deixe vazio se não souber)
PASTA_SAIDA  = "/content/drive/MyDrive/saida_rais_sjc"   # resultado vai para o SEU Drive

# A RAIS pública não tem CNPJ: linhas idênticas podem ser estabelecimentos
# diferentes (ex.: duas lojas iguais no mesmo CEP). Com False, elas são só
# sinalizadas na coluna flag_possivel_duplicata. Com True, as cópias são removidas.
REMOVER_DUPLICATAS_EXATAS = False

# %% [markdown]
# ## 2. Autorizar o Google e trazer o arquivo para o Colab
# O arquivo é copiado de Drive para Drive, para o disco temporário do Colab.
# Nada passa pelo seu computador. Com 3 GB, leva de 1 a 3 minutos.

# %%
import io, os, re, time
from google.colab import auth, drive
auth.authenticate_user()
drive.mount("/content/drive")

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

svc = build("drive", "v3")

def extrai_id(link):
    m = re.search(r"(?:/d/|[?&]id=|/folders/)([\w-]{20,})", link or "")
    return m.group(1) if m else None

file_id = extrai_id(LINK_ARQUIVO)
if file_id:
    meta = svc.files().get(fileId=file_id, fields="id,name,size,owners(emailAddress),modifiedTime",
                           supportsAllDrives=True).execute()
else:
    nome_q = NOME_ARQUIVO.replace("'", "\\'")
    res = svc.files().list(
        q=f"name = '{nome_q}' and trashed = false",
        corpora="allDrives", includeItemsFromAllDrives=True, supportsAllDrives=True,
        fields="files(id,name,size,owners(emailAddress),modifiedTime)", pageSize=20).execute()
    arqs = res.get("files", [])
    if not arqs:
        raise SystemExit(
            f"Não encontrei '{NOME_ARQUIVO}' entre os arquivos que você pode ver.\n"
            "Peça o LINK ao dono do arquivo e cole em LINK_ARQUIVO na célula 1.")
    for a in arqs:
        print(f"- {a['name']} | {int(a.get('size', 0))/1024**3:.2f} GB | dono: "
              f"{a.get('owners', [{}])[0].get('emailAddress', '?')} | id: {a['id']}")
    meta = max(arqs, key=lambda a: int(a.get("size", 0)))   # se houver mais de um, usa o maior

tam_total = int(meta.get("size", 0))
DONO_ARQUIVO = meta.get("owners", [{}])[0].get("emailAddress", "não informado")
ARQUIVO_LOCAL = f"/content/{meta['name']}"
print(f"\nArquivo: {meta['name']} ({tam_total/1024**3:.2f} GB) | dono: {DONO_ARQUIVO}")

if os.path.exists(ARQUIVO_LOCAL) and os.path.getsize(ARQUIVO_LOCAL) == tam_total:
    print("Já estava copiado no Colab. Pulando o download.")
else:
    req = svc.files().get_media(fileId=meta["id"], supportsAllDrives=True)
    t0 = time.time()
    with io.FileIO(ARQUIVO_LOCAL, "wb") as fh:
        dl = MediaIoBaseDownload(fh, req, chunksize=200 * 1024 * 1024)
        feito = False
        while not feito:
            status, feito = dl.next_chunk()
            if status:
                print(f"\r  copiando... {status.progress()*100:5.1f}%  ({time.time()-t0:,.0f}s)", end="")
    print(f"\nCópia concluída: {os.path.getsize(ARQUIVO_LOCAL)/1024**3:.2f} GB")

# %% [markdown]
# ## 3. Conferir o arquivo (cabeçalho e primeiras linhas)

# %%
def detecta_encoding(caminho):
    with open(caminho, "rb") as f:
        amostra = f.read(2_000_000)
    try:
        amostra.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "latin-1"

ENCODING = detecta_encoding(ARQUIVO_LOCAL)
with open(ARQUIVO_LOCAL, "r", encoding=ENCODING, errors="replace") as f:
    cab = f.readline()
    SEPARADOR = max([";", ",", "\t", "|"], key=cab.count)
    print(f"Codificação: {ENCODING} | separador: '{SEPARADOR}'\n")
    print("Colunas:", [c.strip().strip('"') for c in cab.rstrip("\n").split(SEPARADOR)])
    print()
    for _ in range(3):
        print(f.readline().rstrip())

# %% [markdown]
# ## 4. Funções de tratamento
# Basta executar esta célula; não é preciso alterar nada.

# %%
import unicodedata
from datetime import date, datetime
import pandas as pd
import numpy as np

# ---------------- São José dos Campos ----------------
MUNICIPIO_NOME = "SAO JOSE DOS CAMPOS"
COD_IBGE_6 = "354990"      # código usado na RAIS
COD_IBGE_7 = "3549904"
UF_SIGLA, UF_COD = "SP", "35"

URL_RAIS = "https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatisticas-trabalho/microdados-rais-e-caged"
URL_PDET = "https://pdet.mte.gov.br/microdados-rais-e-caged"
URL_CNAE_API = "https://servicodados.ibge.gov.br/api/v2/cnae/subclasses"
URL_CNAE = "https://concla.ibge.gov.br/busca-online-cnae.html"

# ---------------- Dicionários RAIS ----------------
TAMANHO_ESTAB = {
    "1": ("01 - Zero", 0, 0), "2": ("02 - Até 4", 1, 4), "3": ("03 - De 5 a 9", 5, 9),
    "4": ("04 - De 10 a 19", 10, 19), "5": ("05 - De 20 a 49", 20, 49),
    "6": ("06 - De 50 a 99", 50, 99), "7": ("07 - De 100 a 249", 100, 249),
    "8": ("08 - De 250 a 499", 250, 499), "9": ("09 - De 500 a 999", 500, 999),
    "10": ("10 - 1000 ou mais", 1000, 10**9),
}
IBGE_SUBSETOR = {
    "1": "Extrativa mineral", "2": "Ind. de produtos minerais não metálicos",
    "3": "Indústria metalúrgica", "4": "Indústria mecânica",
    "5": "Ind. do material elétrico e de comunicações", "6": "Ind. do material de transporte",
    "7": "Ind. da madeira e do mobiliário", "8": "Ind. do papel, papelão, editorial e gráfica",
    "9": "Ind. da borracha, fumo, couros, peles e diversas",
    "10": "Ind. química, farmacêutica, veterinária e perfumaria",
    "11": "Ind. têxtil, do vestuário e artefatos de tecidos", "12": "Indústria de calçados",
    "13": "Ind. de alimentos, bebidas e álcool etílico", "14": "Serviços industriais de utilidade pública",
    "15": "Construção civil", "16": "Comércio varejista", "17": "Comércio atacadista",
    "18": "Instituições de crédito, seguros e capitalização",
    "19": "Com. e adm. de imóveis, valores mobiliários, serv. técnicos",
    "20": "Transportes e comunicações",
    "21": "Serv. de alojamento, alimentação, reparação, manutenção",
    "22": "Serviços médicos, odontológicos e veterinários", "23": "Ensino",
    "24": "Administração pública direta e autárquica",
    "25": "Agricultura, silvicultura, criação de animais, pesca",
}
TIPO_ESTAB = {"1": "CNPJ", "3": "CAEPF", "4": "CNO"}
NATUREZA_GRUPO = {"1": "Administração Pública", "2": "Entidades Empresariais",
                  "3": "Entidades sem Fins Lucrativos", "4": "Pessoas Físicas",
                  "5": "Organizações Internacionais"}

SECOES_CNAE = [
    ("A", 1, 3, "Agricultura, pecuária, produção florestal, pesca e aquicultura", "Agropecuária"),
    ("B", 5, 9, "Indústrias extrativas", "Indústria"),
    ("C", 10, 33, "Indústrias de transformação", "Indústria"),
    ("D", 35, 35, "Eletricidade e gás", "Indústria"),
    ("E", 36, 39, "Água, esgoto, gestão de resíduos e descontaminação", "Indústria"),
    ("F", 41, 43, "Construção", "Construção"),
    ("G", 45, 47, "Comércio; reparação de veículos automotores e motocicletas", "Comércio"),
    ("H", 49, 53, "Transporte, armazenagem e correio", "Serviços"),
    ("I", 55, 56, "Alojamento e alimentação", "Serviços"),
    ("J", 58, 63, "Informação e comunicação", "Serviços"),
    ("K", 64, 66, "Atividades financeiras, de seguros e serviços relacionados", "Serviços"),
    ("L", 68, 68, "Atividades imobiliárias", "Serviços"),
    ("M", 69, 75, "Atividades profissionais, científicas e técnicas", "Serviços"),
    ("N", 77, 82, "Atividades administrativas e serviços complementares", "Serviços"),
    ("O", 84, 84, "Administração pública, defesa e seguridade social", "Administração Pública"),
    ("P", 85, 85, "Educação", "Serviços"),
    ("Q", 86, 88, "Saúde humana e serviços sociais", "Serviços"),
    ("R", 90, 93, "Artes, cultura, esporte e recreação", "Serviços"),
    ("S", 94, 96, "Outras atividades de serviços", "Serviços"),
    ("T", 97, 97, "Serviços domésticos", "Serviços"),
    ("U", 99, 99, "Organismos internacionais e outras instituições extraterritoriais", "Serviços"),
]
CADEIAS_SJC = [
    ("Aeroespacial e Defesa", ("3041", "3042", "3050", "2550", "3319", "5240", "7210")),
    ("Automotiva", ("291", "292", "293", "294", "295", "4511", "4512", "452", "453")),
    ("Tecnologia da Informação", ("62", "631")),
    ("Química, Petróleo e Plásticos", ("19", "20", "22")),
    ("Saúde", ("86", "87", "88", "2121", "2123", "3250", "4644", "4771")),
    ("Educação", ("85",)),
    ("Logística", ("49", "50", "51", "52", "53")),
    ("Pesquisa e Engenharia", ("711", "712", "72")),
]

# ---------------- Mapeamento das colunas da RAIS ----------------
# (nome normalizado -> nome padronizado). Aceita variações entre anos.
REGRAS_COLUNAS = [
    ("cnae_subclasse", lambda n: "cnae" in n and "subclasse" in n),
    ("cnae95_classe", lambda n: "cnae" in n and "95" in n),
    ("cnae_classe", lambda n: "cnae" in n and "classe" in n and "95" not in n),
    ("qtd_vinculos_clt", lambda n: "vinc" in n and "clt" in n),
    ("qtd_vinculos_estatutarios", lambda n: "vinc" in n and "estatut" in n),
    ("qtd_vinculos_ativos", lambda n: "vinc" in n and "ativo" in n),
    ("ind_atividade_ano", lambda n: n.startswith("ind") and "atividade" in n),
    ("ind_cei_vinculado", lambda n: n.startswith("ind") and "cei" in n),
    ("ind_pat", lambda n: n.startswith("ind") and "pat" in n),
    ("ind_rais_negativa", lambda n: n.startswith("ind") and "negativa" in n),
    ("ind_simples", lambda n: n.startswith("ind") and "simples" in n),
    ("municipio", lambda n: n.startswith("munic")),
    ("natureza_juridica", lambda n: "natureza" in n),
    ("tamanho_estabelecimento", lambda n: "tamanho" in n),
    ("tipo_estab_desc", lambda n: n.startswith("tipo_estab") and n not in ("tipo_estab", "tipo_estabelecimento")),
    ("tipo_estab", lambda n: n in ("tipo_estab", "tipo_estabelecimento")),
    ("uf", lambda n: n == "uf"),
    ("ibge_subsetor", lambda n: "subsetor" in n),
    ("cep", lambda n: "cep" in n),
    ("bairros_sp", lambda n: "bairro" in n and n.endswith("sp")),
    ("bairros_fortaleza", lambda n: "bairro" in n and "fortaleza" in n),
    ("bairros_rj", lambda n: "bairro" in n and n.endswith("rj")),
    ("distritos_sp", lambda n: "distrito" in n),
    ("regioes_adm_df", lambda n: "regi" in n and "df" in n),
]
# Colunas que só existem para SP-capital, Fortaleza, RJ e DF (não servem para SJC)
COLUNAS_OUTRAS_CIDADES = ["bairros_sp", "bairros_fortaleza", "bairros_rj", "distritos_sp", "regioes_adm_df"]
NULOS = {"", "nan", "none", "-1", "{ñ class}", "{n class}", "{ñ", "ignorado", "{ñ class"}


def sem_acento(t):
    return "".join(c for c in unicodedata.normalize("NFKD", str(t)) if not unicodedata.combining(c))

def normaliza_nome(c):
    return re.sub(r"[^a-z0-9]+", "_", sem_acento(c).lower()).strip("_")

def mapear_colunas(colunas):
    mapa, usados = {}, set()
    for original in colunas:
        n = normaliza_nome(original)
        for padrao, regra in REGRAS_COLUNAS:
            if padrao not in usados and regra(n):
                mapa[original] = padrao
                usados.add(padrao)
                break
        else:
            mapa[original] = n
    return mapa

def limpa(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    s = re.sub(r"\s+", " ", str(v)).strip().strip('"')
    return None if s.lower() in NULOS else s

def digitos(v):
    return re.sub(r"\D", "", str(v)) if v is not None else ""

def para_int(v):
    s = limpa(v)
    if s is None:
        return None
    s = s.replace(".", "").replace(",", ".")
    try:
        return int(float(s))
    except ValueError:
        return None

def sim_nao(v):
    s = limpa(v)
    return {"1": "Sim", "0": "Não"}.get(s, "Não informado")

def secao_cnae(cnae):
    if len(cnae) < 2 or not cnae[:2].isdigit():
        return (None, "NAO CLASSIFICADO", "Não classificado")
    d = int(cnae[:2])
    for sec, ini, fim, desc, macro in SECOES_CNAE:
        if ini <= d <= fim:
            return (sec, desc, macro)
    return (None, "NAO CLASSIFICADO", "Não classificado")

def cadeia_sjc(cnae):
    for nome, pref in CADEIAS_SJC:
        if cnae.startswith(pref):
            return nome
    return "Outras"

def porte_sebrae(vinculos, setor):
    """Critério SEBRAE/IBGE por número de empregados."""
    if vinculos is None or pd.isna(vinculos):
        return "Não informado"
    v = int(vinculos)
    if v == 0:
        return "0 - Sem vínculos"
    if setor == "Indústria" or setor == "Construção":
        faixas = [(19, "1 - Micro"), (99, "2 - Pequena"), (499, "3 - Média")]
    else:
        faixas = [(9, "1 - Micro"), (49, "2 - Pequena"), (99, "3 - Média")]
    for lim, nome in faixas:
        if v <= lim:
            return nome
    return "4 - Grande"

def carrega_cnae_ibge():
    """Descrições oficiais das subclasses/classes CNAE pela API do IBGE."""
    try:
        import requests
        r = requests.get(URL_CNAE_API, timeout=60)
        r.raise_for_status()
        sub, cla = {}, {}
        for item in r.json():
            sub[str(item["id"]).zfill(7)] = item["descricao"].upper()
            c = item.get("classe") or {}
            if c:
                cla[str(c["id"]).zfill(5)] = c["descricao"].upper()
        print(f"  CNAE IBGE: {len(sub):,} subclasses e {len(cla):,} classes carregadas")
        return sub, cla
    except Exception as e:
        print(f"  [aviso] não foi possível consultar a API CNAE do IBGE ({e}). Seguindo sem descrições.")
        return {}, {}


# ---------------- 1) Leitura + filtro de SJC ----------------
def ler_rais_sjc(caminho, sep, encoding, chunksize=500_000):
    tam = os.path.getsize(caminho)
    partes, lidas, t0 = [], 0, time.time()
    leitor = pd.read_csv(caminho, sep=sep, dtype=str, encoding=encoding, chunksize=chunksize,
                         on_bad_lines="warn", encoding_errors="replace", keep_default_na=False)
    mapa, col_mun, col_uf = None, None, None
    for ch in leitor:
        if mapa is None:
            mapa = mapear_colunas(ch.columns)
            inv = {v: k for k, v in mapa.items()}
            col_mun, col_uf = inv.get("municipio"), inv.get("uf")
            if col_mun is None:
                raise SystemExit(f"Coluna de município não encontrada. Colunas: {list(ch.columns)}")
            print(f"  filtrando pela coluna '{col_mun}' = {COD_IBGE_6} (São José dos Campos)")
        mun = ch[col_mun].str.strip().str.strip('"')
        mask = mun.isin([COD_IBGE_6, COD_IBGE_7]) | \
               mun.map(lambda x: sem_acento(x).upper()).str.contains(MUNICIPIO_NOME, regex=False)
        if mask.any():
            sel = ch[mask].copy()
            sel["linha_origem"] = sel.index + 2        # +1 cabeçalho, +1 base 1
            partes.append(sel)
        lidas += len(ch)
        print(f"\r  linhas lidas: {lidas:,} | SJC: {sum(len(p) for p in partes):,} | "
              f"{time.time()-t0:,.0f}s", end="")
    print()
    df = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()
    return df.rename(columns=mapa or {}), lidas


# ---------------- 2) Tratamento ----------------
def tratar_rais(df, log, cnae_sub, cnae_cla, ano_base, arquivo):
    log.append(("Filtro", "Estabelecimentos de São José dos Campos encontrados na RAIS", len(df)))

    # --- Remove colunas que só valem para outras cidades
    fora = [c for c in COLUNAS_OUTRAS_CIDADES if c in df.columns]
    df = df.drop(columns=fora)
    log.append(("Seleção", f"Colunas específicas de outras cidades removidas: {', '.join(fora) or '-'}", len(fora)))

    # --- Valores nulos padronizados ({ñ class}, -1, vazio)
    cols_orig = [c for c in df.columns if c != "linha_origem"]
    antes_nulos = df[cols_orig].apply(lambda s: s.str.strip().str.lower().isin(NULOS - {""}).sum()).sum()
    for c in cols_orig:
        df[c] = df[c].map(limpa)
    log.append(("Padronização", "Células com código de 'não classificado' ({ñ class}, -1) convertidas para vazio", int(antes_nulos)))

    # --- Duplicidades
    # A RAIS pública não traz CNPJ. Duas lojas diferentes com o mesmo CNAE, CEP e nº de
    # vínculos geram linhas idênticas, e cada uma é um estabelecimento real. Por isso o
    # padrão é SINALIZAR. Se REMOVER_DUPLICATAS_EXATAS = True, as cópias são removidas.
    dup = df.duplicated(subset=cols_orig, keep="first")
    if REMOVER_DUPLICATAS_EXATAS:
        df = df[~dup].reset_index(drop=True)
        log.append(("Duplicidade", "Linhas idênticas removidas (REMOVER_DUPLICATAS_EXATAS = True)", int(dup.sum())))
    else:
        df["flag_possivel_duplicata"] = dup.map({True: "Sim", False: "Não"}).values
        log.append(("Duplicidade", "Linhas idênticas a outra (possível duplicata; sinalizadas, não removidas)",
                    int(dup.sum())))

    # --- Localização
    if "uf" in df.columns:
        uf_err = (df["uf"].fillna("") != UF_COD).sum()
        log.append(("Localização", "UF diferente de 35 (SP) corrigida", int(uf_err)))
    df["municipio"] = MUNICIPIO_NOME
    df["uf"] = UF_SIGLA
    df["cod_municipio_ibge"] = COD_IBGE_7

    # --- CEP
    if "cep" in df.columns:
        cep = df["cep"].map(digitos).str.zfill(8)
        ok = cep.str.match(r"^12[2-9]\d{5}$")          # faixa de CEP de SJC: 12200-000 a 12249-999 (+ distritos)
        log.append(("Endereço", "CEP inválido ou fora da faixa de SJC convertido para vazio",
                    int((~ok & df["cep"].notna()).sum())))
        df["cep"] = cep.where(ok).map(lambda c: f"{c[:5]}-{c[5:]}" if isinstance(c, str) else None)
        df["flag_cep_ausente"] = df["cep"].isna().map({True: "Sim", False: "Não"})

    # --- CNAE
    sub = df.get("cnae_subclasse", pd.Series([None]*len(df))).map(lambda v: digitos(v).zfill(7) if v else "")
    sub = sub.where(sub.str.len() == 7, "")
    cla = df.get("cnae_classe", pd.Series([None]*len(df))).map(lambda v: digitos(v).zfill(5) if v else "")
    cla = cla.where(cla.str.len() == 5, "")
    cla = cla.where(cla != "", sub.str[:5])             # classe a partir da subclasse, se faltar
    cnae_base = sub.where(sub != "", cla)
    log.append(("CNAE", "Estabelecimentos sem CNAE válido", int((cnae_base == "").sum())))
    if cnae_sub:
        inexist = (sub != "") & ~sub.isin(cnae_sub.keys())
        log.append(("CNAE", "Subclasse CNAE inexistente na tabela oficial do IBGE (sinalizado)", int(inexist.sum())))
        df["flag_cnae_inexistente"] = inexist.map({True: "Sim", False: "Não"})
    df["cnae_subclasse"] = sub.map(lambda s: f"{s[:4]}-{s[4]}/{s[5:]}" if s else None)
    df["cnae_subclasse_descricao"] = sub.map(cnae_sub).where(sub != "") if cnae_sub else None
    df["cnae_classe"] = cla.map(lambda s: f"{s[:2]}.{s[2:4]}-{s[4]}" if s else None)
    df["cnae_classe_descricao"] = cla.map(cnae_cla).where(cla != "") if cnae_cla else None
    df["cnae_divisao"] = cnae_base.str[:2].replace("", None)
    sec = cnae_base.map(secao_cnae)
    df["cnae_secao"] = sec.map(lambda x: x[0])
    df["cnae_secao_descricao"] = sec.map(lambda x: x[1])
    df["setor_economico"] = sec.map(lambda x: x[2])
    df["cadeia_produtiva_sjc"] = cnae_base.map(cadeia_sjc)

    # --- Subsetor IBGE
    if "ibge_subsetor" in df.columns:
        cod = df["ibge_subsetor"].map(lambda v: str(int(v)) if v and str(v).isdigit() else None)
        df["ibge_subsetor_cod"] = cod
        df["ibge_subsetor"] = cod.map(IBGE_SUBSETOR).fillna("Não classificado")

    # --- Vínculos (números)
    for c in ["qtd_vinculos_ativos", "qtd_vinculos_clt", "qtd_vinculos_estatutarios"]:
        if c in df.columns:
            v = df[c].map(para_int)
            neg = (v < 0).sum()
            nulo = v.isna().sum()
            v = v.where(v >= 0)
            log.append(("Vínculos", f"{c}: valores negativos/não numéricos convertidos para 0",
                        int(neg + nulo)))
            df[c] = v.fillna(0).astype(int)
    if {"qtd_vinculos_ativos", "qtd_vinculos_clt", "qtd_vinculos_estatutarios"} <= set(df.columns):
        inc = (df["qtd_vinculos_clt"] + df["qtd_vinculos_estatutarios"]) > df["qtd_vinculos_ativos"]
        df["flag_vinculos_inconsistentes"] = inc.map({True: "Sim", False: "Não"})
        log.append(("Vínculos", "CLT + estatutários maior que vínculos ativos (sinalizado)", int(inc.sum())))

    # --- Tamanho do estabelecimento (faixa RAIS) x vínculos
    if "tamanho_estabelecimento" in df.columns:
        cod = df["tamanho_estabelecimento"].map(lambda v: str(int(v)) if v and str(v).isdigit() else None)
        df["tamanho_estab_faixa"] = cod.map(lambda c: TAMANHO_ESTAB.get(c, ("Não informado",))[0])
        if "qtd_vinculos_ativos" in df.columns:
            def fora_faixa(c, v):
                if c not in TAMANHO_ESTAB:
                    return False
                _, lo, hi = TAMANHO_ESTAB[c]
                return not (lo <= v <= hi)
            ff = pd.Series([fora_faixa(c, v) for c, v in zip(cod, df["qtd_vinculos_ativos"])], index=df.index)
            df["flag_tamanho_divergente"] = ff.map({True: "Sim", False: "Não"})
            log.append(("Vínculos", "Faixa de tamanho não bate com a qtd. de vínculos ativos (sinalizado)",
                        int(ff.sum())))
        df = df.drop(columns="tamanho_estabelecimento")

    # --- Porte (SEBRAE, por nº de empregados e setor)
    if "qtd_vinculos_ativos" in df.columns:
        df["porte_sebrae"] = [porte_sebrae(v, s) for v, s in zip(df["qtd_vinculos_ativos"], df["setor_economico"])]

    # --- Natureza jurídica
    if "natureza_juridica" in df.columns:
        nj = df["natureza_juridica"].map(lambda v: digitos(v).zfill(4) if v else None)
        df["natureza_juridica"] = nj.map(lambda s: f"{s[:3]}-{s[3]}" if s else None)
        df["natureza_juridica_grupo"] = nj.map(lambda s: NATUREZA_GRUPO.get(s[0], "Não informado") if s else "Não informado")

    # --- Tipo de estabelecimento
    if "tipo_estab" in df.columns:
        df["tipo_estab"] = df["tipo_estab"].map(lambda v: TIPO_ESTAB.get(str(v).lstrip("0"), v) if v else "Não informado")
    if "tipo_estab_desc" in df.columns:
        df["tipo_estab_desc"] = df["tipo_estab_desc"].map(lambda v: sem_acento(v).upper() if v else None)

    # --- Indicadores 0/1 -> Sim/Não
    for c in ["ind_atividade_ano", "ind_cei_vinculado", "ind_pat", "ind_rais_negativa", "ind_simples"]:
        if c in df.columns:
            df[c] = df[c].map(sim_nao)
    if "ind_atividade_ano" in df.columns:
        df["status_atividade"] = df["ind_atividade_ano"].map({"Sim": "Com atividade no ano", "Não": "Sem atividade no ano"}).fillna("Não informado")
    if {"ind_rais_negativa", "qtd_vinculos_ativos"} <= set(df.columns):
        rn = (df["ind_rais_negativa"] == "Sim") & (df["qtd_vinculos_ativos"] > 0)
        df["flag_rais_negativa_com_vinculo"] = rn.map({True: "Sim", False: "Não"})
        log.append(("Consistência", "RAIS negativa, mas com vínculos ativos (sinalizado)", int(rn.sum())))
    if "ind_simples" in df.columns:
        df = df.rename(columns={"ind_simples": "optante_simples"})
    if "cnae95_classe" in df.columns:
        df = df.drop(columns="cnae95_classe")      # classificação antiga, substituída pela CNAE 2.0

    # --- Qualidade do registro
    chave = [c for c in ["cnae_subclasse", "cep", "natureza_juridica", "ibge_subsetor_cod"] if c in df.columns]
    df["qualidade_registro_pct"] = (df[chave].notna().mean(axis=1) * 100).round(0).astype(int)

    # --- Origem dos dados
    df.insert(0, "id_registro", [f"SJC-{i:06d}" for i in range(1, len(df) + 1)])
    df["ano_base_rais"] = ano_base or "Não informado"
    df["fonte_dados"] = "RAIS - Relação Anual de Informações Sociais (MTE) - Microdados Estabelecimentos"
    df["url_fonte"] = URL_PDET
    df["arquivo_origem"] = arquivo
    df["data_tratamento"] = date.today()

    ordem = ["id_registro", "ano_base_rais", "municipio", "uf", "cod_municipio_ibge", "cep",
             "cnae_subclasse", "cnae_subclasse_descricao", "cnae_classe", "cnae_classe_descricao",
             "cnae_divisao", "cnae_secao", "cnae_secao_descricao", "setor_economico",
             "ibge_subsetor_cod", "ibge_subsetor", "cadeia_produtiva_sjc",
             "qtd_vinculos_ativos", "qtd_vinculos_clt", "qtd_vinculos_estatutarios",
             "tamanho_estab_faixa", "porte_sebrae", "natureza_juridica", "natureza_juridica_grupo",
             "tipo_estab", "tipo_estab_desc", "optante_simples", "status_atividade",
             "ind_atividade_ano", "ind_rais_negativa", "ind_pat", "ind_cei_vinculado",
             "qualidade_registro_pct", "flag_cep_ausente", "flag_cnae_inexistente",
             "flag_vinculos_inconsistentes", "flag_tamanho_divergente", "flag_rais_negativa_com_vinculo",
             "flag_possivel_duplicata",
             "fonte_dados", "url_fonte", "arquivo_origem", "linha_origem", "data_tratamento"]
    ordem = [c for c in ordem if c in df.columns] + [c for c in df.columns if c not in ordem]
    df = df[ordem]
    log.append(("Resultado", "Estabelecimentos na base tratada", len(df)))
    return df


# ---------------- 3) Exportação ----------------
DESCRICOES = {
    "id_registro": "Identificador do registro na base tratada (a RAIS pública não traz CNPJ)",
    "ano_base_rais": "Ano de referência da RAIS",
    "municipio": "Sempre SAO JOSE DOS CAMPOS", "uf": "Sempre SP",
    "cod_municipio_ibge": "3549904 (IBGE 7 dígitos)",
    "cep": "CEP do estabelecimento (00000-000), validado para a faixa de SJC",
    "cnae_subclasse": "CNAE 2.0 subclasse (0000-0/00)",
    "cnae_subclasse_descricao": "Descrição oficial da subclasse (API IBGE)",
    "cnae_classe": "CNAE 2.0 classe (00.00-0)",
    "cnae_classe_descricao": "Descrição oficial da classe (API IBGE)",
    "cnae_divisao": "Divisão CNAE (2 dígitos)", "cnae_secao": "Seção CNAE (A a U)",
    "cnae_secao_descricao": "Descrição da seção CNAE",
    "setor_economico": "Agropecuária, Indústria, Construção, Comércio, Serviços, Adm. Pública",
    "ibge_subsetor_cod": "Código do subsetor IBGE (1 a 25)", "ibge_subsetor": "Subsetor IBGE",
    "cadeia_produtiva_sjc": "Cadeias relevantes para SJC (aeroespacial, automotiva, TI...)",
    "qtd_vinculos_ativos": "Vínculos ativos em 31/12", "qtd_vinculos_clt": "Vínculos CLT",
    "qtd_vinculos_estatutarios": "Vínculos estatutários",
    "tamanho_estab_faixa": "Faixa de tamanho informada pela RAIS",
    "porte_sebrae": "Porte pelo critério SEBRAE (empregados x setor)",
    "natureza_juridica": "Código da natureza jurídica (000-0)",
    "natureza_juridica_grupo": "Adm. Pública, Empresarial, Sem fins lucrativos, Pessoa física...",
    "tipo_estab": "CNPJ, CAEPF ou CNO", "tipo_estab_desc": "Descrição do tipo de estabelecimento",
    "optante_simples": "Optante pelo Simples Nacional", "status_atividade": "Teve atividade no ano-base",
    "ind_atividade_ano": "Indicador de atividade no ano", "ind_rais_negativa": "Declarou RAIS negativa (sem empregados)",
    "ind_pat": "Participa do Programa de Alimentação do Trabalhador", "ind_cei_vinculado": "Possui CEI vinculado",
    "qualidade_registro_pct": "% de campos-chave preenchidos",
    "flag_cep_ausente": "Sim = CEP vazio ou inválido", "flag_cnae_inexistente": "Sim = CNAE não existe na tabela IBGE",
    "flag_vinculos_inconsistentes": "Sim = CLT + estatutários > ativos",
    "flag_tamanho_divergente": "Sim = faixa de tamanho não bate com os vínculos",
    "flag_rais_negativa_com_vinculo": "Sim = RAIS negativa com vínculos",
    "flag_possivel_duplicata": "Sim = linha idêntica a outra (pode ser outro estabelecimento igual; RAIS pública não tem CNPJ)",
    "fonte_dados": "Fonte pública de origem", "url_fonte": "Endereço da fonte",
    "arquivo_origem": "Arquivo lido", "linha_origem": "Linha no arquivo original (rastreabilidade)",
    "data_tratamento": "Data de geração da base",
}
SPRINT = [
    ("S1", "Selecionar as fontes públicas", "RAIS Estabelecimentos (MTE) + tabela CNAE (IBGE); documentar ano-base e link",
     "Aba 'Fontes' preenchida", "Alta", 3),
    ("S2", "Filtrar São José dos Campos", "Filtrar município IBGE 354990 / 3549904",
     "100% dos registros = SAO JOSE DOS CAMPOS", "Alta", 2),
    ("S3", "Corrigir inconsistências", "Nulos ({ñ class}, -1), CEP, CNAE, vínculos, faixa de tamanho, RAIS negativa",
     "Log de qualidade gerado e flags revisadas", "Alta", 5),
    ("S4", "Eliminar duplicidades", "Sinalizar linhas idênticas e decidir a remoção (RAIS pública não tem CNPJ)",
     "Duplicatas revisadas e regra documentada", "Alta", 2),
    ("S5", "Padronizar os campos", "Nomes de colunas, formatos CNAE/CEP/natureza, códigos em texto, Sim/Não",
     "Dicionário de dados aprovado", "Média", 3),
    ("S6", "Classificar as empresas", "Setor, seção CNAE, subsetor IBGE, cadeia SJC, porte SEBRAE, natureza jurídica",
     "Todos os registros classificados", "Média", 3),
    ("S7", "Registrar a origem dos dados", "Fonte, URL, arquivo, linha de origem, ano-base e data de tratamento",
     "Colunas de origem 100% preenchidas", "Média", 1),
    ("S8", "Validar e entregar para o painel", "Conferir amostra, publicar CSV/Excel e conectar ao painel",
     "Painel lendo a base sem erros", "Alta", 2),
]


def monta_resumo(df):
    blocos = []
    def tab(col, titulo):
        if col not in df.columns:
            return
        g = df.groupby(df[col].fillna("Não informado"))
        t = pd.DataFrame({"Estabelecimentos": g.size()})
        if "qtd_vinculos_ativos" in df.columns:
            t["Vínculos ativos"] = g["qtd_vinculos_ativos"].sum()
        t = t.sort_values("Estabelecimentos", ascending=False).rename_axis(titulo).reset_index()
        t["% estab."] = (t["Estabelecimentos"] / t["Estabelecimentos"].sum()).round(4)
        blocos.append((titulo, t))
    for col, tit in [("setor_economico", "Setor econômico"), ("ibge_subsetor", "Subsetor IBGE"),
                     ("cadeia_produtiva_sjc", "Cadeia produtiva SJC"), ("porte_sebrae", "Porte SEBRAE"),
                     ("tamanho_estab_faixa", "Faixa de tamanho RAIS"),
                     ("natureza_juridica_grupo", "Natureza jurídica"), ("status_atividade", "Atividade no ano"),
                     ("optante_simples", "Simples Nacional")]:
        tab(col, tit)
    return blocos


def exportar(df, log, fontes, pasta):
    os.makedirs(pasta, exist_ok=True)
    csv_p = os.path.join(pasta, "base_rais_sjc.csv")
    xls_p = os.path.join(pasta, "base_rais_sjc.xlsx")
    df.to_csv(csv_p, sep=";", index=False, encoding="utf-8-sig", date_format="%Y-%m-%d")

    with pd.ExcelWriter(xls_p, engine="xlsxwriter", date_format="dd/mm/yyyy",
                        datetime_format="dd/mm/yyyy") as xw:
        wb = xw.book
        f_tit = wb.add_format({"bold": True, "font_size": 14, "font_color": "#1F3864"})
        f_sub = wb.add_format({"italic": True, "font_color": "#595959"})
        f_b = wb.add_format({"bold": True})
        f_pct = wb.add_format({"num_format": "0.0%"})
        f_int = wb.add_format({"num_format": "#,##0"})
        f_wrap = wb.add_format({"text_wrap": True, "valign": "top"})
        f_dt = wb.add_format({"num_format": "dd/mm/yyyy"})

        # Base tratada (tabela Excel com filtros)
        df.to_excel(xw, sheet_name="Base_Tratada", index=False, startrow=1, header=False)
        ws = xw.sheets["Base_Tratada"]
        ws.add_table(0, 0, max(len(df), 1), len(df.columns) - 1,
                     {"name": "BaseRAIS_SJC", "style": "Table Style Medium 2",
                      "columns": [{"header": c} for c in df.columns]})
        ws.freeze_panes(1, 1)
        for j, c in enumerate(df.columns):
            am = df[c].dropna().astype(str).str.len().head(3000)
            larg = min(max(len(c), int(am.quantile(0.9)) if len(am) else 10) + 2, 55)
            fmt = f_dt if c == "data_tratamento" else f_int if c.startswith("qtd_") else None
            ws.set_column(j, j, larg, fmt)

        # Resumo
        ws = wb.add_worksheet("Resumo")
        ws.write(0, 0, "Estabelecimentos de São José dos Campos (RAIS) - Resumo", f_tit)
        tot_v = int(df["qtd_vinculos_ativos"].sum()) if "qtd_vinculos_ativos" in df.columns else 0
        ws.write(1, 0, f"Gerado em {datetime.now():%d/%m/%Y %H:%M} | Estabelecimentos: {len(df):,} | "
                       f"Vínculos ativos: {tot_v:,}".replace(",", "."), f_sub)
        col = 0
        for tit, t in monta_resumo(df):
            ws.write(3, col, tit, f_b)
            t.to_excel(xw, sheet_name="Resumo", startrow=4, startcol=col, index=False)
            ws.set_column(col, col, 40)
            ws.set_column(col + 1, col + t.shape[1] - 2, 14, f_int)
            ws.set_column(col + t.shape[1] - 1, col + t.shape[1] - 1, 9, f_pct)
            col += t.shape[1] + 1

        # Log de qualidade
        lg = pd.DataFrame(log, columns=["Etapa", "Verificação / correção", "Registros afetados"])
        lg.to_excel(xw, sheet_name="Log_Qualidade", index=False)
        ws = xw.sheets["Log_Qualidade"]
        ws.set_column(0, 0, 16); ws.set_column(1, 1, 85); ws.set_column(2, 2, 18, f_int)
        ws.autofilter(0, 0, len(lg), 2)

        # Dicionário
        dic = pd.DataFrame({"Campo": df.columns,
                            "Descrição": [DESCRICOES.get(c, "") for c in df.columns],
                            "Preenchimento (%)": [round(df[c].notna().mean(), 4) for c in df.columns],
                            "Exemplo": [str(df[c].dropna().iloc[0]) if df[c].notna().any() else "" for c in df.columns]})
        dic.to_excel(xw, sheet_name="Dicionario_Dados", index=False)
        ws = xw.sheets["Dicionario_Dados"]
        ws.set_column(0, 0, 30); ws.set_column(1, 1, 70); ws.set_column(2, 2, 18, f_pct); ws.set_column(3, 3, 45)
        ws.autofilter(0, 0, len(dic), 3)

        # Fontes
        fontes.to_excel(xw, sheet_name="Fontes", index=False)
        ws = xw.sheets["Fontes"]
        for j, w in enumerate([45, 60, 55, 14, 30, 16, 30]):
            ws.set_column(j, j, w, f_wrap)

        # Sprint
        sp = pd.DataFrame(SPRINT, columns=["ID", "Tarefa", "Descrição", "Critério de aceite",
                                           "Prioridade", "Estimativa (pontos)"])
        sp["Responsável"], sp["Status"], sp["Início"], sp["Fim previsto"], sp["Observações"] = "", "A fazer", None, None, ""
        sp.to_excel(xw, sheet_name="Sprint", index=False)
        ws = xw.sheets["Sprint"]
        for j, w in enumerate([6, 34, 60, 40, 11, 12, 20, 14, 12, 13, 40]):
            ws.set_column(j, j, w, f_wrap)
        ws.set_column(8, 9, 13, f_dt)
        n = len(sp)
        ws.data_validation(1, 7, n, 7, {"validate": "list",
                           "source": ["A fazer", "Em andamento", "Em revisão", "Concluído", "Bloqueado"]})
        ws.data_validation(1, 4, n, 4, {"validate": "list", "source": ["Alta", "Média", "Baixa"]})
        for val, cor in [("Concluído", "#C6EFCE"), ("Bloqueado", "#FFC7CE"), ("Em andamento", "#FFEB9C")]:
            ws.conditional_format(1, 7, n, 7, {"type": "cell", "criteria": "==", "value": f'"{val}"',
                                               "format": wb.add_format({"bg_color": cor})})
        ws.autofilter(0, 0, n, 10)
        ws.freeze_panes(1, 2)
        ws.write(n + 2, 1, "Total de pontos", f_b)
        ws.write_formula(n + 2, 5, f"=SUM(F2:F{n+1})")
        ws.write(n + 3, 1, "Concluídas (%)", f_b)
        ws.write_formula(n + 3, 5, f'=COUNTIF(H2:H{n+1},"Concluído")/COUNTA(A2:A{n+1})', f_pct)
    return xls_p, csv_p

print("Funções carregadas.")

# %% [markdown]
# ## 5. Executar o tratamento
# Lê as ~3 GB em blocos e mantém só São José dos Campos. Leva de 3 a 8 minutos.

# %%
!pip -q install xlsxwriter

t0 = time.time()
log = []
print("[1/4] Lendo e filtrando São José dos Campos...")
bruto, total_linhas = ler_rais_sjc(ARQUIVO_LOCAL, SEPARADOR, ENCODING)
log.append(("Leitura", "Linhas lidas no arquivo RAIS (Brasil todo)", total_linhas))
if bruto.empty:
    raise SystemExit("Nenhum registro de São José dos Campos encontrado. Confira a célula 3.")

print("[2/4] Consultando a tabela CNAE do IBGE...")
cnae_sub, cnae_cla = carrega_cnae_ibge()

print("[3/4] Tratando...")
base = tratar_rais(bruto, log, cnae_sub, cnae_cla, ANO_BASE, os.path.basename(ARQUIVO_LOCAL))

hoje = date.today().strftime("%d/%m/%Y")
fontes = pd.DataFrame([
    {"Fonte": "RAIS - Relação Anual de Informações Sociais (Ministério do Trabalho e Emprego)",
     "Descrição / uso": "Microdados de estabelecimentos: CNAE, vínculos, tamanho, natureza jurídica, CEP",
     "URL": URL_PDET, "Ano-base": ANO_BASE or "Não informado",
     "Arquivo utilizado": os.path.basename(ARQUIVO_LOCAL), "Data de extração": hoje,
     "Obtido de": f"Google Drive de {DONO_ARQUIVO}"},
    {"Fonte": "IBGE - CONCLA / API de CNAE 2.0",
     "Descrição / uso": "Descrição oficial das subclasses e classes CNAE" if cnae_sub else "Não consultada (sem conexão)",
     "URL": URL_CNAE_API, "Ano-base": "Versão vigente", "Arquivo utilizado": "API", "Data de extração": hoje,
     "Obtido de": "servicodados.ibge.gov.br"},
    {"Fonte": "IBGE - Classificação CNAE 2.0 (seções) e SEBRAE (porte por nº de empregados)",
     "Descrição / uso": "Setor econômico, seção CNAE e porte",
     "URL": URL_CNAE, "Ano-base": "-", "Arquivo utilizado": "Tabelas internas do notebook",
     "Data de extração": hoje, "Obtido de": "-"},
])

print("[4/4] Gerando Excel e CSV no seu Drive...")
xls_p, csv_p = exportar(base, log, fontes, PASTA_SAIDA)
print(f"\nConcluído em {time.time()-t0:,.0f}s | {len(base):,} estabelecimentos em SJC")
print(f"Excel: {xls_p}\nCSV (painel): {csv_p}")

# %% [markdown]
# ## 6. Conferir o resultado

# %%
display(pd.DataFrame(log, columns=["Etapa", "Verificação / correção", "Registros afetados"]))
display(base.head(10))

# %%
# (opcional) baixar o Excel para o computador
from google.colab import files
files.download(xls_p)
