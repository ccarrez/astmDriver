# ASTM driver

## Context

This program allows you to get results from ASTM analyzers
It handles basic ASTM communication and make a file for each message
The files are stored locally and temporary, so another program, such as Mirth, can access it and re-process it to your LIS (Laboratory Information System)

## Technical informations

The Python script is executed as a service using systemd
Configuration file is located at /etc/systemd/system/astm-driver.service

If you edit the configuration, remember to reload systemctl:

```bash
sudo systemctl daemon-reload
```

Basic restart can be performed with:

```bash
sudo systemctl restart astm-driver.service
```
