import requests_pkcs12
import time
import xml.etree.ElementTree as ET
import os
import tkinter as tk
from tkinter import messagebox
import xml.dom.minidom

def post_request_with_pfx(url, xml_body, username, password, pfx_file_path, pfx_password):
    """
    Realiza una solicitud POST a una URL usando autenticación y certificado.

    Args:
        url (str): La URL del endpoint.
        xml_body (str): El contenido XML del body de la solicitud.
        username (str): El nombre de usuario para la autenticación.
        password (str): La contraseña para la autenticación.
        pfx_file_path (str): Ruta al archivo del certificado (.p12).
        pfx_password (str): Contraseña del certificado.

    Returns:
        requests.Response: El objeto de respuesta de la solicitud.
    """

    headers = {
        "Content-Type": "text/xml",
        "SOAPAction": ""
    }

    response = requests_pkcs12.post(
        url, 
        headers=headers, 
        data=xml_body, 
        auth=(username, password), 
        pkcs12_filename=pfx_file_path,
        pkcs12_password=pfx_password,
        verify=True  # A veces es necesario deshabilitar la verificación, pero no es lo más seguro
    )

    return response

def process_request(url, term_url, notification_url, monto, num_tarjeta, expiracion, cvv, use_3ds):
    soap_xml = f'''   
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ipg="http://ipg-online.com/ipgapi/schemas/ipgapi" xmlns:v1="http://ipg-online.com/ipgapi/schemas/v1" xmlns:ns2="http://ipg-online.com/ipgapi/schemas/ipgapi">
        <soapenv:Header/>
        <soapenv:Body>
            <ipg:IPGApiOrderRequest>
                <v1:Transaction>
                    <v1:CreditCardTxType>
                        <v1:StoreId>62666666</v1:StoreId>
                        <v1:Type>sale</v1:Type>
                    </v1:CreditCardTxType>
                    <v1:CreditCardData>
                        <v1:CardNumber>{num_tarjeta}</v1:CardNumber>
                        <v1:ExpMonth>{expiracion.split('/')[0]}</v1:ExpMonth>
                        <v1:ExpYear>{expiracion.split('/')[1]}</v1:ExpYear>
                        <v1:CardCodeValue>{cvv}</v1:CardCodeValue>
                    </v1:CreditCardData>
                    {'<v1:CreditCard3DSecure>'
                    '<v1:AuthenticateTransaction>true</v1:AuthenticateTransaction>'
                    f'<v1:TermUrl>{term_url}</v1:TermUrl>'
                    f'<v1:ThreeDSMethodNotificationURL>{notification_url}</v1:ThreeDSMethodNotificationURL>'
                    '<v1:ThreeDSRequestorChallengeIndicator>01</v1:ThreeDSRequestorChallengeIndicator>'
                    '<v1:ThreeDSRequestorChallengeWindowSize>01</v1:ThreeDSRequestorChallengeWindowSize>'
                    '</v1:CreditCard3DSecure>' if use_3ds else ''}
                    <v1:Payment>
                        <v1:ChargeTotal>{monto}</v1:ChargeTotal>
                        <v1:Currency>484</v1:Currency>
                    </v1:Payment>
                </v1:Transaction>
            </ipg:IPGApiOrderRequest>
        </soapenv:Body>
    </soapenv:Envelope>
    '''
    inicio = time.time()  # Iniciar el cronómetro
    resp = post_request_with_pfx(url, soap_xml, apiUser, apiPassword, p12path, CertPwd)
    tiempo_ejecucion = time.time() - inicio  # Calcular el tiempo de ejecución
    
    # Imprimir la respuesta XML identada y fácil de leer
    xml_response = xml.dom.minidom.parseString(resp.text)
    print(xml_response.toprettyxml())
    
    # Obtener el valor de ApprovalCode y OrderId de la respuesta SOAP
    root = ET.fromstring(resp.text)
    approval_code = root.find('.//{http://ipg-online.com/ipgapi/schemas/ipgapi}ApprovalCode').text
    order_id = root.find('.//{http://ipg-online.com/ipgapi/schemas/ipgapi}OrderId').text
    acs_url = root.find('.//{http://ipg-online.com/ipgapi/schemas/ipgapi}AcsURL')
    creq = root.find('.//{http://ipg-online.com/ipgapi/schemas/ipgapi}CReq')
    
    return tiempo_ejecucion, approval_code, order_id, acs_url.text if acs_url is not None else None, creq.text if creq is not None else None

# Función para procesar la solicitud
def procesar_peticion():
    url = entrada_url.get()
    term_url = entrada_term_url.get()
    notification_url = entrada_notification_url.get()
    monto = entrada_monto.get()
    num_tarjeta = entrada_num_tarjeta.get()
    expiracion = entrada_expiracion.get()
    cvv = entrada_cvv.get()
    use_3ds = var_3ds.get()  # Obtener el estado del checkbox 3DS
    try:
        monto_float = float(monto)
        tiempo_ejecucion, approval_code, order_id, acs_url, creq = process_request(url, term_url, notification_url, monto, num_tarjeta, expiracion, cvv, use_3ds)
        respuesta = f"Tiempo de ejecución de la solicitud: {tiempo_ejecucion:.4f} segundos\n"
        respuesta += f"Approval Code: {approval_code}\n"
        respuesta += f"Order ID: {order_id}\n"
        if acs_url:
            respuesta += f"AcsURL: {acs_url}\n"
        if creq:
            respuesta += f"CReq: {creq}\n"
        cuadro_respuesta.delete(1.0, tk.END)
        cuadro_respuesta.insert(tk.END, respuesta)
    except ValueError:
        messagebox.showerror("Error", "Ingresa un monto válido para la petición.")

# Configuración de la autenticación y la URL base
username = os.getlogin()
apiPassword = "Password123$"
apiUser = "WS62666666._.5"
CertPwd = 'Password123$'
p12path = fr'C:\Users\{username}\Documents\SOAP_cert\joskua_test.p12'

# Crear la ventana Tkinter con un tamaño personalizado
ventana = tk.Tk()
ventana.title("Programa con Interfaz")
ventana.geometry("600x500")  # Ancho x Alto

# Definir fuente
fuente = ("Arial", 10)

# Etiqueta y campo de entrada para la URL
etiqueta_url = tk.Label(ventana, text="URL:", font=fuente)
etiqueta_url.grid(row=0, column=0, sticky='w', padx=5, pady=5)
entrada_url = tk.Entry(ventana, font=fuente, width=30)
entrada_url.grid(row=0, column=1, padx=5, pady=5)
entrada_url.insert(0, 'https://test.ipg-online.com/ipgapi/services')  # Valor predeterminado de la URL

# Etiqueta y campo de entrada para TermUrl
etiqueta_term_url = tk.Label(ventana, text="TermUrl:", font=fuente)
etiqueta_term_url.grid(row=1, column=0, sticky='w', padx=5, pady=5)
entrada_term_url = tk.Entry(ventana, font=fuente, width=30)
entrada_term_url.grid(row=1, column=1, padx=5, pady=5)
entrada_term_url.insert(0, 'https://webhook.site/f68050a8-54eb-4e69-9177-85d7089562bb')  # Valor predeterminado de TermUrl

# Etiqueta y campo de entrada para ThreeDSMethodNotificationURL
etiqueta_notification_url = tk.Label(ventana, text="ThreeDSMethodNotificationURL:", font=fuente)
etiqueta_notification_url.grid(row=2, column=0, sticky='w', padx=5, pady=5)
entrada_notification_url = tk.Entry(ventana, font=fuente, width=30)
entrada_notification_url.grid(row=2, column=1, padx=5, pady=5)
entrada_notification_url.insert(0, 'https://webhook.site/f68050a8-54eb-4e69-9177-85d7089562bb')  # Valor predeterminado de ThreeDSMethodNotificationURL

# Etiqueta y campo de entrada para el monto
etiqueta_monto = tk.Label(ventana, text="Monto:", font=fuente)
etiqueta_monto.grid(row=3, column=0, sticky='w', padx=5, pady=5)
entrada_monto = tk.Entry(ventana, font=fuente, width=30)
entrada_monto.grid(row=3, column=1, padx=5, pady=5)
entrada_monto.insert(0, "10")  # Valor predeterminado del monto

# Etiqueta y campo de entrada para el número de tarjeta
etiqueta_num_tarjeta = tk.Label(ventana, text="Número de Tarjeta:", font=fuente)
etiqueta_num_tarjeta.grid(row=4, column=0, sticky='w', padx=5, pady=5)
entrada_num_tarjeta = tk.Entry(ventana, font=fuente, width=30)
entrada_num_tarjeta.grid(row=4, column=1, padx=5, pady=5)
entrada_num_tarjeta.insert(0, "4147463011110059")  # Valor predeterminado del número de tarjeta

# Etiqueta y campo de entrada para la fecha de expiración
etiqueta_expiracion = tk.Label(ventana, text="Fecha de Expiración (MM/YY):", font=fuente)
etiqueta_expiracion.grid(row=5, column=0, sticky='w', padx=5, pady=5)
entrada_expiracion = tk.Entry(ventana, font=fuente, width=30)
entrada_expiracion.grid(row=5, column=1, padx=5, pady=5)
entrada_expiracion.insert(0, "11/25")  # Valor predeterminado de la fecha de expiración

# Etiqueta y campo de entrada para el CVV
etiqueta_cvv = tk.Label(ventana, text="CVV:", font=fuente)
etiqueta_cvv.grid(row=6, column=0, sticky='w', padx=5, pady=5)
entrada_cvv = tk.Entry(ventana, font=fuente, width=30)
entrada_cvv.grid(row=6, column=1, padx=5, pady=5)
entrada_cvv.insert(0, "123")  # Valor predeterminado del CVV

# Checkbox para 3DS
var_3ds = tk.BooleanVar()
check_3ds = tk.Checkbutton(ventana, text="3DS", variable=var_3ds, font=fuente)
check_3ds.grid(row=7, column=0, columnspan=2, pady=5)

# Botón para enviar la petición
boton_ejecutar = tk.Button(ventana, text="Enviar Request", command=procesar_peticion, font=fuente)
boton_ejecutar.grid(row=8, column=0, columnspan=2, pady=5)

# Cuadro de respuesta de la solicitud
cuadro_respuesta = tk.Text(ventana, wrap=tk.WORD, font=fuente)
cuadro_respuesta.grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

# Barra de desplazamiento para el cuadro de respuesta
scrollbar_respuesta = tk.Scrollbar(ventana, command=cuadro_respuesta.yview)
scrollbar_respuesta.grid(row=9, column=2, sticky='ns')
cuadro_respuesta.config(yscrollcommand=scrollbar_respuesta.set)

# Iniciar el bucle principal de Tkinter
ventana.mainloop()
