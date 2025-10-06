import shutil
import os
import requests
import logging
import json
import subprocess

# Configuration logging
logging.basicConfig(filename='deploy.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def is_apache_installed():
    installed = shutil.which("apache2") or shutil.which("httpd")
    logging.info(f"Apache installé : {bool(installed)}")
    return bool(installed)


def is_apache_running():
    running = (os.system("systemctl is-active --quiet apache2") == 0 or
               os.system("systemctl is-active --quiet httpd") == 0)
    logging.info(f"Apache en cours d'exécution : {running}")
    return running


def start_apache():
    if shutil.which("apache2"):
        ret = os.system("sudo systemctl start apache2")
        if ret == 0:
            logging.info("Apache (apache2) démarré avec succès.")
            return True
        else:
            logging.error("Échec du démarrage d'Apache (apache2).")
            return False
    elif shutil.which("httpd"):
        ret = os.system("sudo systemctl start httpd")
        if ret == 0:
            logging.info("Apache (httpd) démarré avec succès.")
            return True
        else:
            logging.error("Échec du démarrage d'Apache (httpd).")
            return False
    else:
        logging.error("Apache n'est pas installé, impossible de démarrer.")
        return False


def create_virtual_host():
    site_name = "nexa.local"
    site_dir = f"/var/www/{site_name}"
    html_file = f"{site_dir}/index.html"
    conf_file = f"/etc/apache2/sites-available/{site_name}.conf"

    try:
        os.system(f"sudo mkdir -p {site_dir}")

        html_content = """<!DOCTYPE html>
<html>
<head><title>Hello Nexa Digital School</title></head>
<body><h1>Hello Nexa</h1></body>
</html>
"""
        with open("index.html", "w") as f:
            f.write(html_content)
        os.system(f"sudo mv index.html {html_file}")
        os.system(f"sudo chown -R www-data:www-data {site_dir}")

        vhost_config = f"""
<VirtualHost *:80>
    ServerName {site_name}
    DocumentRoot {site_dir}

    <Directory {site_dir}>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${{APACHE_LOG_DIR}}/{site_name}_error.log
    CustomLog ${{APACHE_LOG_DIR}}/{site_name}_access.log combined
</VirtualHost>
"""
        with open("nexa.conf", "w") as f:
            f.write(vhost_config.strip())
        os.system(f"sudo mv nexa.conf {conf_file}")

        os.system("sudo a2ensite nexa.local.conf")
        os.system("sudo a2enmod rewrite")
        os.system("sudo systemctl reload apache2")

        # Modifier /etc/hosts
        with open("/etc/hosts", "r") as f:
            hosts = f.read()
        if "nexa.local" not in hosts:
            os.system('echo "127.0.0.1 nexa.local" | sudo tee -a /etc/hosts > /dev/null')
            logging.info("nexa.local ajouté à /etc/hosts")
            hosts_added = True
        else:
            logging.info("nexa.local est déjà dans /etc/hosts")
            hosts_added = False

        logging.info("Virtual host nexa.local créé avec succès.")
        return True, hosts_added
    except Exception as e:
        logging.error(f"Erreur lors de la création du virtual host : {e}")
        return False, False


def check_nexa_local():
    try:
        response = requests.get("http://nexa.local", timeout=5)
        if response.status_code == 200:
            logging.info("Page http://nexa.local répond avec le code 200.")
            return True, response.status_code
        else:
            logging.warning(f"Page http://nexa.local a répondu avec le code {response.status_code}.")
            return False, response.status_code
    except Exception as e:
        logging.error(f"Erreur lors du test http://nexa.local : {e}")
        return False, None


def send_ntfy_notification(title, message, channel="apache_nexa"):
    url = f"https://ntfy.sh/{channel}"
    headers = {
        "Title": title,
        "Priority": "default"
    }
    try:
        response = requests.post(url, data=message.encode('utf-8'), headers=headers)
        if response.status_code == 200:
            logging.info("Notification ntfy envoyée avec succès via HTTP.")
            return True
        else:
            logging.error(f"Erreur lors de l'envoi de la notification ntfy : {response.status_code} {response.text}")
            return False
    except Exception as e:
        logging.error(f"Exception lors de l'envoi ntfy : {e}")
        return False




def main():
    report = {
        "apache_installed": False,
        "apache_running": False,
        "apache_started": False,
        "virtual_host_created": False,
        "hosts_file_updated": False,
        "nexa_local_responding": False,
        "http_status_code": None,
        "ntfy_notification_sent": False
    }

    report["apache_installed"] = is_apache_installed()

    if not report["apache_installed"]:
        print("Apache n'est pas installé. Fin du script.")
        return report

    report["apache_running"] = is_apache_running()

    if not report["apache_running"]:
        print("Apache n'est pas en cours d'exécution. Démarrage en cours...")
        report["apache_started"] = start_apache()
    else:
        print("Apache est déjà en cours d'exécution.")

    vhost_ok, hosts_added = create_virtual_host()
    report["virtual_host_created"] = vhost_ok
    report["hosts_file_updated"] = hosts_added

    check_ok, status_code = check_nexa_local()
    report["nexa_local_responding"] = check_ok
    report["http_status_code"] = status_code

    # Préparation du message ntfy
    if all([report["apache_installed"], report["apache_started"] or report["apache_running"], report["virtual_host_created"], report["nexa_local_responding"]]):
        ntfy_message = "Déploiement réussi : tout est OK 👍"
    else:
        ntfy_message = "Déploiement partiel/échec : vérifier les logs ⚠️"

    ntfy_sent = send_ntfy_notification("Déploiement Apache Nexa", ntfy_message)
    report["ntfy_notification_sent"] = ntfy_sent

    # Afficher le rapport final au format JSON
    print("\n--- Rapport final ---")
    print(json.dumps(report, indent=4))

    return report


if __name__ == "__main__":
    main()
