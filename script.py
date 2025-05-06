# Importation des bibliothèques nécessaires
import flet as ft  # Flet est utilisé pour créer l'interface utilisateur graphique
import requests  # Pour effectuer des requêtes HTTP/HTTPS
import time  # Pour mesurer la latence (temps d'exécution)
import csv  # Pour l'exportation des résultats dans un fichier CSV
from urllib.parse import urljoin  # Pour construire des URLs absolues à partir de chemins relatifs
from bs4 import BeautifulSoup  # Pour analyser et extraire les ressources d'une page HTML

# Listes globales pour stocker les résultats des tests HTTP et HTTPS
historique_http = []
historique_https = []

# Fonction principale exécutée par Flet
def main(page: ft.Page):
    page.title = "Analyse HTTP/HTTPS - Victoire"  # Titre de la page
    page.scroll = ft.ScrollMode.AUTO  # Activation du défilement automatique
    page.padding = 20  # Espacement intérieur de la page

    # Champ de saisie pour l'URL à tester
    url_field = ft.TextField(label="URL", expand=True)
    # Champ de saisie pour définir le nombre de requêtes à effectuer
    nb_field = ft.TextField(label="Nombre de requêtes", value="10", width=150)

    # Tableau des résultats HTTP
    result_table_http = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Protocole")),
            ft.DataColumn(label=ft.Text("Latence (ms)")),
            ft.DataColumn(label=ft.Text("Taille (Ko)")),
            ft.DataColumn(label=ft.Text("Débit (Ko/s)")),
        ],
        rows=[]
    )

    # Tableau des résultats HTTPS
    result_table_https = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Protocole")),
            ft.DataColumn(label=ft.Text("Latence (ms)")),
            ft.DataColumn(label=ft.Text("Taille (Ko)")),
            ft.DataColumn(label=ft.Text("Débit (Ko/s)")),
        ],
        rows=[]
    )

    # Anneau de chargement (spinner) visible pendant l'exécution
    progress_ring = ft.ProgressRing(visible=False)

    # Boîte de dialogue pour afficher des messages (succès ou erreur)
    alert_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("✅ Terminé", weight="bold"),
        content=ft.Text("Opération complétée avec succès !"),
        actions=[],
        actions_alignment="end",
    )

    # Fonction pour afficher la boîte de dialogue avec un message
    def show_dialog(msg: str):
        alert_dialog.content = ft.Text(msg)
        alert_dialog.actions = [
            ft.TextButton("OK", on_click=lambda e: close_dialog())
        ]
        alert_dialog.open = True
        page.dialog = alert_dialog
        page.update()

    # Fonction pour fermer la boîte de dialogue
    def close_dialog():
        alert_dialog.open = False
        page.update()

    # Fonction pour lancer les tests de performance HTTP et HTTPS
    def lancer_test(e):
        if not url_field.value.strip():  # Vérifie si l'URL est vide
            return

        result_table_http.rows.clear()  # Vide le tableau HTTP
        result_table_https.rows.clear()  # Vide le tableau HTTPS

        try:
            nb = int(nb_field.value)  # Convertit le nombre de requêtes en entier
        except ValueError:
            show_dialog("❌ Veuillez entrer un nombre valide.")
            return

        url = url_field.value.strip()

        btn_test.disabled = True
        btn_csv.disabled = True
        progress_ring.visible = True
        page.update()

        # Lancer les mesures pour HTTP et HTTPS
        resultats_http = mesurer_performance(url, use_https=False, num_requetes=nb)
        resultats_https = mesurer_performance(url, use_https=True, num_requetes=nb)

        # Mise à jour de l'historique
        historique_http.clear()
        historique_https.clear()
        historique_http.extend(resultats_http)
        historique_https.extend(resultats_https)

        # Affichage des résultats HTTP
        for r in resultats_http:
            result_table_http.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text("HTTP")),
                ft.DataCell(ft.Text(f"{r['latence']*1000:.2f}")),
                ft.DataCell(ft.Text(f"{r['taille']/1024:.2f}")),
                ft.DataCell(ft.Text(f"{r['debit']/1024:.2f}")),
            ]))

        # Affichage des résultats HTTPS
        for r in resultats_https:
            result_table_https.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text("HTTPS")),
                ft.DataCell(ft.Text(f"{r['latence']*1000:.2f}")),
                ft.DataCell(ft.Text(f"{r['taille']/1024:.2f}")),
                ft.DataCell(ft.Text(f"{r['debit']/1024:.2f}")),
            ]))

        # Réactiver les boutons et cacher l'anneau de chargement
        btn_test.disabled = False
        btn_csv.disabled = False
        progress_ring.visible = False
        show_dialog("Test terminé avec succès !")

    # Fonction pour exporter les résultats en CSV
    def exporter_csv(e):
        if not historique_http and not historique_https:
            show_dialog("Aucun résultat à exporter.")
            return

        btn_test.disabled = True
        btn_csv.disabled = True
        progress_ring.visible = True
        page.update()

        # Création et écriture du fichier CSV
        with open("resultats_http_https.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Protocole", "Latence (s)", "Taille (octets)", "Débit (o/s)"])
            for r in historique_http:
                writer.writerow(["HTTP", r["latence"], r["taille"], r["debit"]])
            for r in historique_https:
                writer.writerow(["HTTPS", r["latence"], r["taille"], r["debit"]])

        btn_test.disabled = False
        btn_csv.disabled = False
        progress_ring.visible = False
        show_dialog("Fichier CSV exporté avec succès !")

    # Boutons pour lancer les tests et exporter les résultats
    btn_test = ft.ElevatedButton("▶️ Lancer le test", on_click=lancer_test)
    btn_csv = ft.ElevatedButton("💾 Exporter CSV", on_click=exporter_csv)

    # Ajouter tous les éléments dans la page
    page.add(
        ft.Column([
            ft.Text("🧪 Analyse comparative HTTP vs HTTPS", size=22, weight="bold"),
            ft.Row([url_field]),
            ft.Row([nb_field]),
            ft.Row([btn_test, btn_csv, progress_ring]),
            ft.Divider(),
            ft.Text("Résultats HTTP", weight="bold"),
            result_table_http,
            ft.Divider(),
            ft.Text("Résultats HTTPS", weight="bold"),
            result_table_https,
        ])
    )

# Fonction pour mesurer les performances (latence, taille, débit)
def mesurer_performance(url, use_https, num_requetes):
    protocol = "https" if use_https else "http"
    full_url = url.replace("http://", "").replace("https://", "")
    full_url = f"{protocol}://{full_url}"

    results = []
    for i in range(1, num_requetes + 1):
        try:
            start_time = time.time()
            response = requests.get(full_url, timeout=10)
            total_size = len(response.content)

            # Télécharger les ressources externes (images, scripts, etc.)
            resources = collect_resources(response.text, full_url)
            for resource_url in resources:
                try:
                    res = requests.get(resource_url, timeout=5)
                    total_size += len(res.content)
                except requests.RequestException:
                    pass  # Ignore les erreurs de téléchargement

            end_time = time.time()
            latence = end_time - start_time
            debit = total_size / latence if latence > 0 else 0

            results.append({
                "latence": latence,
                "taille": total_size,
                "debit": debit,
            })

        except requests.RequestException:
            # En cas d'erreur, renvoyer des valeurs nulles
            results.append({
                "latence": 0,
                "taille": 0,
                "debit": 0,
            })

    return results

# Fonction pour extraire les ressources (images, scripts, liens CSS)
def collect_resources(html_content, base_url):
    soup = BeautifulSoup(html_content, "html.parser")
    resources = []
    for tag in soup.find_all(["img", "script", "link"]):
        src = tag.get("src") or tag.get("href")
        if src:
            resource_url = urljoin(base_url, src)
            resources.append(resource_url)
    return resources

# Lancer l'application Flet
ft.app(target=main)
