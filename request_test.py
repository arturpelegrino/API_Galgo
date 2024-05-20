# Carregar bibliotecas:

import requests
import xml.etree.ElementTree as ET
import lxml.etree as etree

# Definir parametros:

rota = 'https://www.w3schools.com/xml/tempconvert.asmx?WSDL'

# SOAPEnvelope = """<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
#   <soap:Body>
#     <CelsiusToFahrenheit xmlns="https://www.w3schools.com/xml/">
#       <Celsius>30</Celsius>
#     </CelsiusToFahrenheit>
#   </soap:Body>
# </soap:Envelope>"""

SOAPEnvelope = etree.tostring(etree.parse(r"C:\Users\artur\OneDrive\Área de Trabalho\Codes\PythonCodes\Robô galgo\CelsiusToFahrenheitSOAP.xml"), pretty_print=True)

opcoes = {"Content-Type": "text/xml; charset=utf-8"}

# Obter resultado:

reposta = requests.post(url=rota, data= SOAPEnvelope, headers=opcoes)

root = ET.fromstring(reposta.text)

for i in root.iter('{https://www.w3schools.com/xml/}CelsiusToFahrenheitResult'):
    
    print(i.text)