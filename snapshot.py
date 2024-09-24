""" 
Felipe Soares
Script snapshot ovirt
data:20/09/2024
Versão 1.2
dnf install python3-ovirt-engine-sdk4
https://github.com/oVirt/ovirt-engine-sdk/tree/master/sdk

"""


import ovirtsdk4 as sdk
import ovirtsdk4.types as types
from datetime import datetime

# Conectar ao servidor oVirt
connection = sdk.Connection(
    url='https://minha maquina/ovirt-engine/api',
    username='user',
    password='senha',
    ca_file='/etc/pki/ca-trust/source/anchors/ac-raiz.pem',  # caminho do certificado CA
)

# Lista de nomes ou IDs das VMs
vm_names = ['cdgestic065','CDGESTIC066', 'CDGESTIC067','CDGESTIC068','CDGESTIC069','CDGESTIC070','CDGESTIC076','CDGESTIC077','CDGESTIC078','CDGESTIC079' ]  # Adicione o nome ou IDs das VMs aqui

# Obtém a data atual (dia e mês)
current_date = datetime.now().strftime('%d-%m')  # Formato: DD-MM

try:
    # Serviço de VMs
    vms_service = connection.system_service().vms_service()

    for vm_name in vm_names:
        try:
            # Localiza a VM pelo nome
            vm = vms_service.list(search=f'name={vm_name}')[0]
            vm_service = vms_service.vm_service(vm.id)

            # Cria um novo snapshot com a data no nome
            snapshot_name = f'Snapshot_{vm_name}_{current_date}'
            snapshots_service = vm_service.snapshots_service()
            snapshot = snapshots_service.add(
                types.Snapshot(
                    description=snapshot_name,
                    persist_memorystate=False  # Se deseja capturar o estado da memória, ajuste para True
                )
            )

            print(f'Snapshot "{snapshot_name}" criado com sucesso para a VM "{vm.name}"')

        except IndexError:
            print(f"VM '{vm_name}' não encontrada.")
        except Exception as e:
            print(f"Erro ao criar o snapshot para a VM '{vm_name}': {e}")

except Exception as e:
    print(f"Erro ao conectar no oVirt: {e}")

finally:
    # Fecha a conexão
    connection.close()