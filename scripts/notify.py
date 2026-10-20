import json
import os
import smtplib
import ssl
import time
from email.message import EmailMessage
from pathlib import Path

EVE = Path("/var/log/suricata/eve.json")
STATE = Path("/var/lib/suricata-notify/state.json")
SIDS = {1000001, 1000002, 1000003, 1000004, 1000005}

config = {}
for line in Path("/etc/suricata-notify/smtp.env").read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#"):
        key, value = line.split("=", 1)
        config[key.strip()] = value.strip()

if STATE.exists():
    state = json.loads(STATE.read_text())
else:
    state = {
        "file": None,
        "offset": 0,
        "last_sent": {},
        "pending": {}
    }


def save():
    temporary = STATE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state))
    temporary.chmod(0o600)
    os.replace(temporary, STATE)


def send(event):
    alert = event["alert"]
    message = EmailMessage()
    message["From"] = config["SMTP_USER"]
    message["To"] = config["MAIL_TO"]
    message["Subject"] = (
        f"[Suricata Lab] Detection SID {alert['signature_id']}"
    )
    message.set_content(
        "Detection de laboratoire - a analyser.\n"
        "Cette alerte ne prouve pas une compromission.\n\n"
        f"Heure : {event.get('timestamp')}\n"
        f"SID : {alert['signature_id']}\n"
        f"Signature : {alert.get('signature')}\n"
        f"Source : {event.get('src_ip')}\n"
        f"Destination : {event.get('dest_ip')}\n"
        f"Port destination : {event.get('dest_port')}\n"
        f"Severite Suricata : {alert.get('severity')}\n"
        "Action suggeree : verifier les journaux et "
        "correler avec le test et Kibana.\n"
    )
    with smtplib.SMTP(
        config["SMTP_HOST"], int(config["SMTP_PORT"]), timeout=30
    ) as smtp:
        smtp.ehlo()
        smtp.starttls(context=ssl.create_default_context())
        smtp.ehlo()
        smtp.login(config["SMTP_USER"], config["SMTP_PASSWORD"])
        smtp.send_message(message)


handle = None
retry_at = 0
print("Surveillance EVE active", flush=True)

while True:
    try:
        if handle is None:
            handle = EVE.open("rb")
            info = os.fstat(handle.fileno())
            identity = f"{info.st_dev}:{info.st_ino}"

            if state["file"] is None:
                # Premier lancement : ignorer les anciens evenements.
                handle.seek(0, 2)
            elif state["file"] == identity:
                if state["offset"] <= info.st_size:
                    handle.seek(state["offset"])

            state["file"] = identity
            state["offset"] = handle.tell()
            save()

        if os.fstat(handle.fileno()).st_size < handle.tell():
            handle.seek(0)

        start = handle.tell()
        line = handle.readline()

        if line and line.endswith(b"\n"):
            try:
                event = json.loads(line)
            except (ValueError, UnicodeDecodeError):
                event = {}

            alert = event.get("alert", {})
            sid = alert.get("signature_id")
            if event.get("event_type") == "alert" and sid in SIDS:
                key = f"{sid}|{event.get('src_ip')}"
                last = state["last_sent"].get(key, 0)
                if time.time() - last >= 300:
                    state["pending"].setdefault(key, event)

            state["offset"] = handle.tell()
            save()
        else:
            # Attendre une ligne complete ; vider l'ancien fichier
            # avant d'ouvrir le nouveau lors d'une rotation.
            handle.seek(start)
            current = EVE.stat()
            opened = os.fstat(handle.fileno())
            if not line and (
                current.st_dev, current.st_ino
            ) != (opened.st_dev, opened.st_ino):
                handle.close()
                handle = None

        if time.time() >= retry_at:
            for key, event in list(state["pending"].items()):
                try:
                    send(event)
                except Exception as error:
                    print(
                        "Envoi reporte :", type(error).__name__,
                        flush=True
                    )
                    retry_at = time.time() + 60
                    break
                else:
                    state["last_sent"][key] = time.time()
                    del state["pending"][key]
                    save()
                    print("Courriel envoye :", key, flush=True)

        if not line or not line.endswith(b"\n"):
            time.sleep(1)

    except OSError as error:
        print("Acces fichier :", type(error).__name__, flush=True)
        if handle is not None:
            handle.close()
            handle = None
        time.sleep(5)
