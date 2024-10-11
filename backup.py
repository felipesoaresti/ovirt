import ovirtsdk4 as sdk
import ovirtsdk4.types as types
from datetime import datetime

# Conectar ao servidor oVirt
connection = sdk.Connection(
    url='https://SEU_OVIRT_ENGINE_URL/ovirt-engine/api',
    username='USUARIO',
    password='SENHA',
    ca_file='CAMINHO_DO_CERTIFICADO_CA',  # caminho do certificado CA
)

# Lista de nomes ou IDs das VMs
vm_names = ['CDGESTIC065','CDGESTIC066', 'CDGESTIC067','CDGESTIC068','CDGESTIC069','CDGESTIC070','CDGESTIC076','CDGESTIC077','CDGESTIC078','CDGESTIC079' ]  # Adicione o nome ou IDs das VMs aqui

# Nome do domínio de exportação (onde será salvo o backup)
export_domain_name = 'EXPORT_DOMAIN'

# Obtém a data atual (dia, mês e ano)
current_date = datetime.now().strftime('%Y-%m-%d')  # Formato: YYYY-MM-DD

# Definir o número máximo de backups por VM
MAX_BACKUPS = 5

try:
    # Serviço de VMs e domínios de exportação
    vms_service = connection.system_service().vms_service()
    storage_domains_service = connection.system_service().storage_domains_service()

    # Localiza o domínio de exportação
    export_domain = storage_domains_service.list(search=f'name={export_domain_name}')[0]
    export_domain_service = storage_domains_service.storage_domain_service(export_domain.id)

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

            # Exporta o snapshot para o domínio de exportação
            vm_service.export(
                storage_domain=types.StorageDomain(id=export_domain.id),
                exclusive=True,  # Impede que a VM seja modificada durante o backup
                discard_snapshots=True  # Discard snapshots após exportar
            )

            print(f'Backup da VM "{vm.name}" exportado com sucesso para o domínio "{export_domain_name}".')

            # Listar backups/exportações anteriores dessa VM
            exports_service = export_domain_service.vms_service()
            exports = exports_service.list(search=f'name={vm_name}')

            # Verificar quantos backups já existem e remover os mais antigos, mantendo até MAX_BACKUPS
            if len(exports) > MAX_BACKUPS:
                # Ordena os backups por data de criação
                sorted_exports = sorted(exports, key=lambda x: x.creation_time)

                # Excluir os backups mais antigos até restarem 5
                for old_export in sorted_exports[:-MAX_BACKUPS]:
                    export_vm_service = exports_service.vm_service(old_export.id)
                    export_vm_service.remove()
                    print(f'Backup antigo "{old_export.name}" removido.')

        except IndexError:
            print(f"VM '{vm_name}' não encontrada.")
        except Exception as e:
            print(f"Erro ao processar a VM '{vm_name}': {e}")

except Exception as e:
    print(f"Erro ao conectar no oVirt: {e}")

finally:
    # Fecha a conexão
    connection.close()
