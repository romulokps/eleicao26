"""Decodificador mínimo do Boletim de Urna (.bu / -bu.dat) do TSE.

O arquivo é DER (ASN.1). Estrutura conforme bu.asn1 da "Documentação técnica do
software da urna eletrônica" (2022, conferida campo a campo em BUs reais de 2026):

EntidadeEnvelopeGenerico ::= SEQUENCE {
    cabecalho, fase, identificacao, tipoEnvelope,
    conteudo OCTET STRING  -- DER de EntidadeBoletimUrna
}
EntidadeBoletimUrna ::= SEQUENCE {
    cabecalho            SEQUENCE { dataGeracao, idEleitoral [2] pleito },
    fase                 ENUMERATED,
    urna                 SEQUENCE { tipoUrna ENUM, versaoVotacao, correspondenciaResultado,
                                    tipoArquivo ENUM, numeroSerieFV, ... },
    identificacaoSecao   SEQUENCE { municipioZona SEQ{mun, zona}, local, secao },
    dataHoraEmissao      GeneralString "AAAAMMDDTHHMMSS",
    dadosSecaoSA         CHOICE { dadosSecao [0] SEQ { dataHoraAbertura, dataHoraEncerramento, ... },
                                  dadosSA [1] ... } OPTIONAL,
    qtdEleitoresLibCodigo INTEGER OPTIONAL,
    qtdEleitoresCompBiometrico [1] ... OPTIONAL,
    resultadosVotacaoPorEleicao SEQUENCE OF SEQUENCE {
        idEleicao, qtdEleitoresAptos, ...,
        resultadosVotacao SEQUENCE OF SEQUENCE {
            tipoCargo ENUM, qtdComparecimento INTEGER,
            totaisVotosCargo SEQUENCE OF SEQUENCE {
                codigoCargo [1], ordemImpressao,
                votosVotaveis SEQUENCE OF SEQUENCE {
                    tipoVoto [1] (1 nominal, 2 branco, 3 nulo, 4 legenda, ...),
                    quantidadeVotos [2], identificacaoVotavel [3] SEQ{partido, codigo} OPTIONAL,
                    ordemGeracaoHash, hash } } } },
    ...
}
Os horários gravados pela urna são de relógio LOCAL (ver normalização em coleta.py).
"""
from dataclasses import dataclass, field

UNIV, CTX = 0, 2
T_INT, T_OCT, T_ENUM, T_SEQ, T_GSTR = 2, 4, 10, 16, 27


class Node:
    __slots__ = ("cls", "cons", "tag", "val", "kids")

    def __init__(self, cls, cons, tag, val, kids):
        self.cls, self.cons, self.tag, self.val, self.kids = cls, cons, tag, val, kids

    @property
    def int(self):
        return int.from_bytes(self.val, "big", signed=True)

    @property
    def str(self):
        return self.val.decode("latin1")

    def is_(self, cls, tag):
        return self.cls == cls and self.tag == tag


def parse(b, pos=0, end=None):
    end = len(b) if end is None else end
    out = []
    while pos < end:
        t0 = b[pos]; pos += 1
        cls, cons, tag = t0 >> 6, bool(t0 & 0x20), t0 & 0x1F
        if tag == 0x1F:
            tag = 0
            while True:
                x = b[pos]; pos += 1
                tag = (tag << 7) | (x & 0x7F)
                if not x & 0x80:
                    break
        L = b[pos]; pos += 1
        if L & 0x80:
            n = L & 0x7F
            L = int.from_bytes(b[pos:pos + n], "big"); pos += n
        if pos + L > end:
            raise ValueError("DER truncado")
        v = b[pos:pos + L]
        kids = parse(b, pos, pos + L) if cons else None
        out.append(Node(cls, cons, tag, v, kids))
        pos += L
    return out


def hm_to_min(s):
    """'20261025T161247' -> (data 'AAAAMMDD', minutos desde 00:00, segundos)."""
    return s[:8], int(s[9:11]) * 60 + int(s[11:13]), int(s[13:15])


@dataclass
class BU:
    pleito: int
    fase: int
    tipo_urna: int
    tipo_arquivo: int
    mun: int
    zona: int
    secao: int
    emissao: str
    abertura: str | None
    encerramento: str | None
    eleicoes: dict = field(default_factory=dict)  # idEleicao -> {aptos, cargos:{cod:{comp, votos{(tipo,cod):n}}}}


def decode(raw: bytes) -> BU:
    env = parse(raw)[0]
    conteudo = [k for k in env.kids if k.is_(UNIV, T_OCT)][-1].val
    bu = parse(conteudo)[0].kids
    i = 0
    cab = bu[i]; i += 1
    pleito = [k for k in cab.kids if k.cls == CTX][0].int
    fase = bu[i].int; i += 1
    urna = bu[i]; i += 1
    enums = [k.int for k in urna.kids if k.is_(UNIV, T_ENUM)]
    tipo_urna, tipo_arquivo = enums[0], (enums[1] if len(enums) > 1 else -1)
    ident = bu[i]; i += 1
    mz = ident.kids[0].kids
    mun, zona = mz[0].int, mz[1].int
    secao = ident.kids[-1].int
    emissao = bu[i].str; i += 1
    abertura = encerramento = None
    eleicoes = {}
    for n in bu[i:]:
        if n.cls == CTX and n.tag == 0 and n.cons:          # dadosSecao
            strs = [k.str for k in n.kids if k.is_(UNIV, T_GSTR)]
            if len(strs) >= 2:
                abertura, encerramento = strs[0], strs[1]
        elif n.is_(UNIV, T_SEQ) and n.kids and n.kids[0].is_(UNIV, T_SEQ) \
                and n.kids[0].kids and n.kids[0].kids[0].is_(UNIV, T_INT) and not eleicoes:
            for rel in n.kids:                               # ResultadoVotacaoPorEleicao
                ints = [k.int for k in rel.kids if k.is_(UNIV, T_INT)]
                id_ele, aptos = ints[0], ints[1]
                cargos = {}
                for rv_list in (k for k in rel.kids if k.is_(UNIV, T_SEQ)):
                    for rv in rv_list.kids:                  # ResultadoVotacao
                        comp = [k.int for k in rv.kids if k.is_(UNIV, T_INT)][0]
                        for tvc_list in (k for k in rv.kids if k.is_(UNIV, T_SEQ)):
                            for tvc in tvc_list.kids:        # TotalVotosCargo
                                cod = [k.int for k in tvc.kids if k.cls == CTX][0]
                                votos = {}
                                for vv_list in (k for k in tvc.kids if k.is_(UNIV, T_SEQ)):
                                    for vv in vv_list.kids:  # TotalVotosVotavel
                                        tipo = qtd = None; cand = 0
                                        for k in vv.kids:
                                            if k.cls == CTX and k.tag == 1: tipo = k.int
                                            elif k.cls == CTX and k.tag == 2: qtd = k.int
                                            elif k.cls == CTX and k.tag == 3 and k.kids:
                                                cand = k.kids[-1].int
                                        votos[(tipo, cand)] = votos.get((tipo, cand), 0) + qtd
                                cargos[cod] = {"comp": comp, "votos": votos}
                eleicoes[id_ele] = {"aptos": aptos, "cargos": cargos}
    return BU(pleito, fase, tipo_urna, tipo_arquivo, mun, zona, secao, emissao,
              abertura, encerramento, eleicoes)
