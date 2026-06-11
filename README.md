# Bloqueador de Internet — Praxedes

Ferramenta com interface gráfica para bloquear o acesso à internet de executáveis via Windows Firewall.

## Funcionalidades

- Busca todos os executáveis em uma pasta e subpastas
- Bloqueia saída (Outbound) e opcionalmente entrada (Inbound) de internet via regras de Firewall
- Prévia do script PowerShell antes de executar
- Aba de gerenciamento para visualizar e remover bloqueios ativos, agrupados por pasta

## Como usar

1. Abra o `BloqueadorPraxedes.exe`
2. Selecione a pasta que contém os programas
3. Clique em **Procurar**
4. (Opcional) Marque **Bloquear também a entrada de internet**
5. Clique em **Bloquear Internet (Firewall)**, revise o script e confirme
6. Para desbloquear, acesse a aba **Gerenciar Bloqueios**

> Requer permissão de **Administrador** para criar/remover regras de firewall.

## Build

```bash
build.bat
```

Requer Python 3.x com `pip`. O script instala as dependências automaticamente.

---

Desenvolvido por **Praxedes**
