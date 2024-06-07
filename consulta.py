# Instalar a biblioteca zeep, crypto e pyOpenSSL
# USAR PYTHON 3.9 
# python -m pip install zeep
# python -m pip install crypto
# python -m pip install pyOpenSSL
# python -m pip install xmlsec
# python -m pip install requests

from datetime import timezone, datetime, timedelta
import os
from lxml import etree
from OpenSSL import crypto
from cryptography.hazmat.primitives.serialization import pkcs12
from zeep.wsse.signature import BinarySignature
from zeep.wsse.username import UsernameToken
from zeep.plugins import HistoryPlugin
from zeep.settings import Settings
from zeep.transports import Transport
from requests import Session
from zeep import Client

from zeep.wsse.utils import WSU

# Classes auxiliares
class TrocaLinhas(object):

    def __init__(self):
        pass

    def apply(self, envelope, headers):
         # Troca linhas (tags) BinarySecurityToken e Signature de posição no XML de requisição.
        linha_signature = envelope[0][0][0]
        linha_binary_security_token = envelope[0][0][1]
        linha_username_token = envelope[0][0][2]
        linha_timestamp = envelope[0][0][3]

        # Troca os valores timestamp <-> username_token
        # Troca os valores binary <-> signature

        envelope[0][0].clear()

        envelope[0][0].append(linha_binary_security_token)
        envelope[0][0].append(linha_signature)
        envelope[0][0].append(linha_timestamp)
        envelope[0][0].append(linha_username_token)

        return envelope, headers
    
    def verify(self, envelope):
        pass

class CustomSignature(object):
    """Sign given SOAP envelope with WSSE sig using given key and cert."""
    def __init__(self, wsse_list):
        self.wsse_list = wsse_list

    def apply(self, envelope, headers):
        for wsse in self.wsse_list:
            envelope, headers = wsse.apply(envelope, headers)

        return envelope, headers

    def verify(self, envelope):
        pass

    
def consulta(client, dict_xml):
    try:
        a = client.service.Consumir(dict_xml)
        return a
    
    except Exception as e:
        print(f'Erro ao realizar consulta : {e}')


def connectSG():

    # Diretorio de certificados
    diretorioData : str = 'C:\\TestePython\\Data'

    # Abrindo certificado (cadeia) e chave privada
    certificado_filename : str = os.path.join(diretorioData, 'stia1.cer')
    private_key_filename : str = os.path.join(diretorioData, 'private.key')

    # Os arquivos do certificado e chave privada precisam estar válidos.
    print(" Arquivo {0} - Válido?: {1} ".format(certificado_filename, os.path.isfile(certificado_filename)))
    print(" Arquivo {0} - Válido?: {1} ".format(private_key_filename, os.path.isfile(private_key_filename)))

    optional_password_cert : str = 'galgo123'

    signature = BinarySignature(private_key_filename, certificado_filename, optional_password_cert)
    print(signature)

    #timestamp_token
    timestamp_token = WSU.Timestamp()
    today_datetime = datetime.now(timezone.utc) # Timezone UTC obrigatório
    expires_datetime = today_datetime + timedelta(minutes=60)
    timestamp_elements = [WSU.Created(today_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z")),
                          WSU.Expires(expires_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z"))]
    timestamp_token.extend(timestamp_elements)

    print(timestamp_token)

    # Usuario e senha para acessar webservice do Sistema Galgo.
    # IMPORTANTE - Entrar em contato com o suporte@galgosistemas.com.br para obter usuário e senha em homologação.
    username = 'USUARIO'
    psw = 'SENHA'

    # Tag UsernameToken
    user_name_token = UsernameToken(username, psw, timestamp_token=timestamp_token)
    print(user_name_token)

    #Instancia do client
    settings : Settings = Settings(strict = True, xml_huge_tree = True)
    settings.raw_response = True
    #plugin para ver xml gerado pelo python
    history : HistoryPlugin = HistoryPlugin()

    # Configurando a Sessão
    session = Session()

    # USAR PYTHON 3.9, caso contrário, essa desabilitação de verificação
    # de URL não funcionará e a conexão não será estabelecida, porque o
    # Sistema Galgo está na rede privada RTM e usa certificado autoassinado. 
    session.verify = False
    transport = Transport(session=session)

    # URL ao servidor de homologação do SG e serviço PL/Cota
    url = 'https://ws.producao.sistemagalgo:7843/ServiceFundoInvestimento?wsdl'

    # Classe responsavel por trocar linhas no WS-Security
    # Sem isso, a conexão com o SG não será bem sucedida.
    trocaLinhas = TrocaLinhas()

    client = Client(url, transport=transport, 
                    wsse=CustomSignature([user_name_token, signature, trocaLinhas]), 
                    plugins=[history], 
                    settings=settings)


    # Dicionário python que será mapeado como XML na requisição (internamente na biblioteca)
    dict_xml = {
        'idMsgSender':'PLCota_Python',
        'qtMaxElement':1, # Em produção pode aumentar essa quantidade até para 500 registros.
    }

    # Resposta da consulta ao realizar a requisição

    resposta = consulta(client, dict_xml)

    # Valores obtidos e enviados com a requisição

    xml_enviado = etree.tostring(history.last_sent["envelope"], encoding="unicode", pretty_print=True)
    xml_recebido = etree.tostring(history.last_received["envelope"], encoding="unicode", pretty_print=True)
    xml_resposta = etree.tostring(etree.XML(resposta.content), pretty_print=True).decode()
    status_resposta = resposta.status_code

    # Visualizar resultados:

    bold = '\033[1m'
    end = '\033[0m'

    print(f"""

\t {bold} ---------------------------------- XML Enviado ------------------------------------ {end}
          
{xml_enviado}

\t {bold} ---------------------------------- XML Recebido ------------------------------------ {end}

{xml_recebido}

\t {bold} ---------------------------------- XML Resposta ------------------------------------ {end}

{xml_resposta}

\t {bold} ---------------------------------- Status Resposta ------------------------------------ {end}

{status_resposta}

""")

if __name__ == "__main__":
    connectSG()
