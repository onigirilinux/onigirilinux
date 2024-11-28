# OnigiriLinux

Un sistema operativo basato su Arch Linux con GNOME, caratterizzato da un gestore di plugin personalizzato e un sistema di aggiornamenti integrato.

## Caratteristiche principali

- Sistema base: Arch Linux con GNOME
- Plugin Manager personalizzato (comando: `bar get [plugin_name]`)
- Sistema di aggiornamenti con interfaccia grafica in stile GNOME
- Repository Arch personalizzata
- Integrazione automatica con GitHub per aggiornamenti e plugin

## Struttura del progetto

```
onigirilinux/
├── archiso/           # Configurazione archiso
├── repo/              # Repository personalizzata
├── apps/             
│   ├── plugin-manager/    # Gestore plugin
│   └── update-manager/    # Gestore aggiornamenti
└── tools/             # Script di utilità
```
