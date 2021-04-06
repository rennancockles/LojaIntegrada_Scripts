Loja Integrada Scripts
============

Scripts de Relatório para Loja Integrada.


Development
-----------

```console
git clone https://github.com/rennancockles/LojaIntegrada_Scripts.git
cd LojaIntegrada_Scripts
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Usage
-----

```console
python lojaintegrada_scripts --script SCRIPT [--data DATA] [--range RANGE RANGE] 
                             [--mail_to MAIL_TO [MAIL_TO ...]]
                             [--log {debug,info,warning,error,critical}]
```
