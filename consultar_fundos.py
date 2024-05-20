# Carregar bibliotecas:

from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport

# Fazer conexão:

usuario = ''
senha = ''
rota_wsdl = 'http://www.stianbid.com.br/ServiceFundoInvestimento/ServiceFundoInvestimento.wsdl'

sessao = Session()
sessao.auth = HTTPBasicAuth(usuario, senha)
cliente = Client(rota_wsdl, transport=Transport(session=sessao))

# Consultar fundo:

cliente.service.Consumir(cnpj='')