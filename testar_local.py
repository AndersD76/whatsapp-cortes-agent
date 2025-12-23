"""
Script para testar os comandos localmente sem WhatsApp.
Execute: python testar_local.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app.commands import processar_comando

def main():
    print("=" * 50)
    print("TESTE LOCAL - Agente de Cortes")
    print("=" * 50)
    print("Digite comandos para testar (ou 'sair' para encerrar)")
    print("Comandos: status, pendentes, concluidos, concluir <codigo>, ajuda")
    print("=" * 50)
    print()

    while True:
        try:
            comando = input(">> ").strip()
            if comando.lower() in ["sair", "exit", "quit"]:
                print("Encerrando...")
                break

            if not comando:
                continue

            resposta = processar_comando(comando)
            print()
            print(resposta)
            print()
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()
