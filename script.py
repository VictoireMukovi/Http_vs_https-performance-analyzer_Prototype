import flet as ft
import requests
import time
import csv
import psutil
from urllib.parse import urljoin
from bs4 import BeautifulSoup

historique_http = []
historique_https = []

def main(page: ft.Page):
    page.title = "Analyse HTTP/HTTPS - Victoire"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    url_field = ft.TextField(label="URL", expand=True)
    nb_field = ft.TextField(label="Nombre de requêtes", value="10", width=150)

    result_table_http = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Protocole")),
            ft.DataColumn(label=ft.Text("Requête")),
            ft.DataColumn(label=ft.Text("Latence (ms)")),
            ft.DataColumn(label=ft.Text("Taille (Ko)")),
            ft.DataColumn(label=ft.Text("Débit (Ko/s)")),
            ft.DataColumn(label=ft.Text("CPU (%)")),
        ],
        rows=[]
    )

    result_table_https = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Protocole")),
            ft.DataColumn(label=ft.Text("Requête")),
            ft.DataColumn(label=ft.Text("Latence (ms)")),
            ft.DataColumn(label=ft.Text("Taille (Ko)")),
            ft.DataColumn(label=ft.Text("Débit (Ko/s)")),
            ft.DataColumn(label=ft.Text("CPU (%)")),
        ],
        rows=[]
    )

    progress_ring = ft.ProgressRing(visible=False)

    alert_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("✅ Terminé", weight="bold"),
        content=ft.Text("Opération complétée avec succès !"),
        actions=[],
        actions_alignment="end",
    )

    def show_dialog(msg: str):
        alert_dialog.content = ft.Text(msg)
        alert_dialog.actions = [
            ft.TextButton("OK", on_click=lambda e: close_dialog())
        ]
        alert_dialog.open = True
        page.dialog = alert_dialog
        page.update()

    def close_dialog():
        alert_dialog.open = False
        page.update()

    def lancer_test(e):
        if not url_field.value.strip():
            return

        result_table_http.rows.clear()
        result_table_https.rows.clear()

        try:
            nb = int(nb_field.value)
        except:
            return

        url = url_field.value.strip()

        btn_test.disabled = True
        btn_csv.disabled = True
        progress_ring.visible = True
        page.update()

        resultats_http = mesurer_performance(url, use_https=False, num_requetes=nb)
        resultats_https = mesurer_performance(url, use_https=True, num_requetes=nb)

        historique_http.clear()
        historique_https.clear()
        historique_http.extend(resultats_http)
        historique_https.extend(resultats_https)

        for r in resultats_http:
            result_table_http.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text("HTTP")),
                ft.DataCell(ft.Text(str(r["requete"]))),
                ft.DataCell(ft.Text(f"{r['latence']*1000:.2f}")),
                ft.DataCell(ft.Text(f"{r['taille']/1024:.2f}")),
                ft.DataCell(ft.Text(f"{r['debit']/1024:.2f}")),
                ft.DataCell(ft.Text(f"{r['cpu']:.1f}"))
            ]))

        for r in resultats_https:
            result_table_https.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text("HTTPS")),
                ft.DataCell(ft.Text(str(r["requete"]))),
                ft.DataCell(ft.Text(f"{r['latence']*1000:.2f}")),
                ft.DataCell(ft.Text(f"{r['taille']/1024:.2f}")),
                ft.DataCell(ft.Text(f"{r['debit']/1024:.2f}")),
                ft.DataCell(ft.Text(f"{r['cpu']:.1f}"))
            ]))

        btn_test.disabled = False
        btn_csv.disabled = False
        progress_ring.visible = False
        show_dialog("Test terminé avec succès !")

    def exporter_csv(e):
        if not historique_http and not historique_https:
            return

        btn_test.disabled = True
        btn_csv.disabled = True
        progress_ring.visible = True
        page.update()

        with open("resultats_http_https.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Protocole", "Requête", "Latence (s)", "Taille (octets)", "Débit (o/s)", "CPU (%)"])
            for r in historique_http:
                writer.writerow(["HTTP", r["requete"], r["latence"], r["taille"], r["debit"], r["cpu"]])
            for r in historique_https:
                writer.writerow(["HTTPS", r["requete"], r["latence"], r["taille"], r["debit"], r["cpu"]])

        btn_test.disabled = False
        btn_csv.disabled = False
        progress_ring.visible = False
        show_dialog("Fichier CSV exporté avec succès !")

    btn_test = ft.ElevatedButton("▶️ Lancer le test", on_click=lancer_test)
    btn_csv = ft.ElevatedButton("💾 Exporter CSV", on_click=exporter_csv)

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

def mesurer_performance(url, use_https, num_requetes):
    protocol = "https" if use_https else "http"
    full_url = url.replace("http://", "").replace("https://", "")
    full_url = f"{protocol}://{full_url}"

    results = []
    for i in range(1, num_requetes + 1):
        try:
            start_cpu = psutil.cpu_percent(interval=None)
            start_time = time.time()

            # Effectuer la requête principale pour récupérer la page
            response = requests.get(full_url)

            # Récupérer les ressources liées (images, CSS, JS)
            resources = collect_resources(response.text, full_url)
            total_size = len(response.content)  # Taille de la page principale

            for resource_url in resources:
                try:
                    res = requests.get(resource_url)
                    total_size += len(res.content)  # Ajouter la taille de chaque ressource
                except Exception as e:
                    print(f"Erreur lors du chargement de la ressource {resource_url}: {e}")

            end_time = time.time()
            end_cpu = psutil.cpu_percent(interval=None)

            latence = end_time - start_time
            cpu = (start_cpu + end_cpu) / 2
            debit = total_size / latence if latence > 0 else 0

            results.append({
                "requete": i,
                "latence": latence,
                "taille": total_size,
                "debit": debit,
                "cpu": cpu
            })

        except Exception:
            results.append({
                "requete": i,
                "latence": 0,
                "taille": 0,
                "debit": 0,
                "cpu": 0
            })

    return results

def collect_resources(html_content, base_url):
    soup = BeautifulSoup(html_content, "html.parser")
    resources = []

    # Rechercher les liens vers les ressources dans le HTML
    for tag in soup.find_all(["img", "script", "link"]):
        src = tag.get("src") or tag.get("href")
        if src:
            resource_url = urljoin(base_url, src)
            resources.append(resource_url)

    return resources

ft.app(target=main)
