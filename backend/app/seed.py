from app.database import SessionLocal
from app.models import Colaborador, ContaBancaria, Fornecedor, MovimentoConta


def _seed_contas(db):
    if db.query(ContaBancaria).count() > 0:
        return
    contas = [
        ContaBancaria(
            nome="Conta Operacional Principal",
            banco="341",
            agencia="1001",
            conta="50001-0",
            saldo=1_250_000.0,
        ),
        ContaBancaria(
            nome="Conta Folha de Pagamento",
            banco="001",
            agencia="2002",
            conta="30002-1",
            saldo=380_000.0,
        ),
        ContaBancaria(
            nome="Conta Fornecedores",
            banco="237",
            agencia="3300",
            conta="88001-5",
            saldo=620_000.0,
        ),
    ]
    db.add_all(contas)
    db.commit()
    for c in contas:
        db.refresh(c)
        db.add(
            MovimentoConta(
                conta_id=c.id,
                tipo="receita",
                valor=c.saldo,
                saldo_apos=c.saldo,
                descricao="Saldo inicial — demonstração MBA",
            )
        )
    db.commit()


def _seed_fornecedores(db):
    lista = [
        ("12.345.678/0001-90", "Tech Solutions Ltda", "341", "1234", "56789-0", "ativo"),
        ("98.765.432/0001-10", "Logística Brasil S.A.", "001", "4321", "98765-4", "ativo"),
        ("45.678.901/0001-23", "Papelaria Corporativa ME", "104", "5500", "11223-4", "ativo"),
        ("33.444.555/0001-66", "Consultoria Estratégica Ltda", "341", "7788", "99001-2", "ativo"),
        ("22.333.444/0001-55", "Energia Verde Comercial", "033", "2200", "44556-7", "ativo"),
        ("77.888.999/0001-11", "Manutenção Predial Express", "237", "1100", "33445-8", "ativo"),
        ("11.222.333/0001-44", "Fornecedor Novo Ltda", "237", "0001", "12345-6", "pendente"),
        ("55.666.777/0001-88", "Serviços Temporários Alfa", "341", "9090", "77665-1", "pendente"),
        ("66.777.888/0001-99", "Distribuidora Nacional de Insumos Ltda", "341", "4400", "66110-9", "ativo"),
        ("44.555.666/0001-77", "Software Enterprise Brasil S.A.", "001", "5100", "77220-3", "ativo"),
        ("88.999.000/0001-22", "Transportes Rápido Centro-Oeste Ltda", "237", "6600", "88330-7", "ativo"),
    ]
    for c, r, b, a, cc, s in lista:
        if db.query(Fornecedor).filter(Fornecedor.cnpj == c).first():
            continue
        db.add(Fornecedor(cnpj=c, razao_social=r, banco=b, agencia=a, conta=cc, status=s))
    db.commit()


def _seed_colaboradores(db):
    lista = [
        ("390.533.447-05", "Ana Paula Ferreira", "Analista Financeiro", "341", "1001", "10001-1", "ativo"),
        ("529.982.247-25", "Carlos Eduardo Lima", "Gerente de Projetos", "001", "2002", "20002-2", "ativo"),
        ("111.444.777-35", "Mariana Souza Costa", "Coordenadora RH", "237", "3300", "30003-3", "ativo"),
        ("277.427.570-31", "Roberto Alves Mendes", "Desenvolvedor Sênior", "104", "5500", "40004-4", "ativo"),
        ("153.253.460-56", "Juliana Martins Rocha", "Assistente Administrativo", "033", "2200", "50005-5", "ativo"),
        ("622.328.110-38", "Fernando Henrique Dias", "Contador", "341", "1200", "60006-6", "ativo"),
        ("714.287.938-60", "Patrícia Oliveira Nunes", "Analista de Compras", "001", "3100", "70007-7", "ativo"),
        ("453.178.287-91", "Ricardo Gomes Barbosa", "Supervisor de Operações", "237", "4100", "80008-8", "ativo"),
        ("861.352.290-91", "Camila Rodrigues Pinto", "Especialista em Compliance", "104", "5200", "90009-9", "ativo"),
        ("390.872.427-05", "Lucas Martins Teixeira", "Analista de TI", "033", "2300", "10010-0", "ativo"),
    ]
    for cpf, nome, cargo, b, ag, ct, st in lista:
        existente = db.query(Colaborador).filter(Colaborador.cpf == cpf).first()
        if existente:
            existente.status = st
            existente.nome_completo = nome
            existente.cargo = cargo
            continue
        db.add(
            Colaborador(
                cpf=cpf,
                nome_completo=nome,
                cargo=cargo,
                banco=b,
                agencia=ag,
                conta=ct,
                status=st,
            )
        )
    db.commit()


def seed_demo_data():
    db = SessionLocal()
    try:
        _seed_contas(db)
        _seed_fornecedores(db)
        _seed_colaboradores(db)
    finally:
        db.close()

    from app.seed_demo_historico import seed_historico_demo
    from app.seed_cenarios_fraude import seed_catalogo_fraude

    seed_historico_demo(force=False)
    seed_catalogo_fraude(force=False)
