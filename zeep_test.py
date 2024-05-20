# Carregar bibliotecas:

from zeep import Client

# Carregar cliente:

cliente = Client('https://www.w3schools.com/xml/tempconvert.asmx?WSDL')

# Fazer conversão:

# Carregar serviços -> python -mzeep https://www.w3schools.com/xml/tempconvert.asmx?WSDL

cliente.service.CelsiusToFahrenheit(30)