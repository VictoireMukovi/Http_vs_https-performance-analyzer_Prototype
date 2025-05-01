import flet as ft
import requests
import time
import csv
import psutil

historique = []

def main(page: ft.Page):
    page.title = "Analyse HTTP/HTTPS - Victoire"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    url_field = ft.TextField(label="URL", expand=True)
    protocol_field = ft.Dropdown(
        label="Protocole", width=150,
        options=[ft.dropdown.Option("HTTP"), ft.dropdown.Option("HTTPS")],
        value="HTTP"
    )
    nb_field = ft.TextField(label="Nombre de requêtes", value="10", width=150)

    result_table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Requête")),
            ft.DataColumn(label=ft.Text("Latence (ms)")),
            ft.DataColumn(label=ft.Text("Taille (Ko)")),
            ft.DataColumn(label=ft.Text("Débit (Ko/s)")),
            ft.DataColumn(label=ft.Text("CPU (%)")),
        ],
        rows=[]
    )

    progress_ring = ft.ProgressRing(visible=False)

    # Dialog général
    alert_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("✅ Terminé", weight="bold"),
        content=ft.Text("Opération complétée avec succès !"),
        actions=[],
        actions_alignment="end",
    )

    # Fonctions utilitaires pour dialog
    def close_dialog(e=None):
        alert_dialog.open = False
        page.update()

    def show_dialog(msg: str):
        alert_dialog.content = ft.Text(msg)
        alert_dialog.actions = [
            ft.TextButton("OK", on_click=close_dialog)
        ]
        alert_dialog.open = True
        page.dialog = alert_dialog
        page.update()

    def lancer_test(e):
        if not url_field.value.strip():
            return  # Ne rien faire si URL vide

        try:
            nb = int(nb_field.value)
        except:
            return  # Ne rien faire si le nombre est invalide

        result_table.rows.clear()

        use_https = protocol_field.value == "HTTPS"
        url = url_field.value.strip()

        btn_test.disabled = True
        btn_csv.disabled = True
        progress_ring.visible = True
        page.update()

        resultats = mesurer_performance(url, use_https, nb)

        for r in resultats:
            result_table.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(r["requete"]))),
                ft.DataCell(ft.Text(f"{r['latence']*1000:.2f}")),
                ft.DataCell(ft.Text(f"{r['taille']/1024:.2f}")),
                ft.DataCell(ft.Text(f"{r['debit']/1024:.2f}")),
                ft.DataCell(ft.Text(f"{r['cpu']:.1f}"))
            ]))

        historique.clear()
        historique.extend(resultats)

        btn_test.disabled = False
        btn_csv.disabled = False
        progress_ring.visible = False
        show_dialog("Test terminé avec succès !")

    def exporter_csv(e):
        if not historique:
            return  # Ne rien faire si pas de données

        btn_test.disabled = True
        btn_csv.disabled = True
        progress_ring.visible = True
        page.update()

        with open("resultats_detail.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Requête", "Latence (s)", "Taille (octets)", "Débit (o/s)", "CPU (%)"])
            for r in historique:
                writer.writerow([r["requete"], r["latence"], r["taille"], r["debit"], r["cpu"]])

        btn_test.disabled = False
        btn_csv.disabled = False
        progress_ring.visible = False
        show_dialog("Fichier CSV exporté avec succès !")

    btn_test = ft.ElevatedButton("▶️ Lancer le test", on_click=lancer_test)
    btn_csv = ft.ElevatedButton("💾 Exporter CSV", on_click=exporter_csv)

    page.add(
        ft.Column([
            ft.Text("🧪 Analyse des performances HTTP vs HTTPS", size=22, weight="bold"),
            ft.Row([url_field]),
            ft.Row([protocol_field, nb_field]),
            ft.Row([btn_test, btn_csv, progress_ring]),
            ft.Divider(),
            result_table,
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

            response = requests.get(full_url)

            end_time = time.time()
            end_cpu = psutil.cpu_percent(interval=None)

            latence = end_time - start_time
            taille = len(response.content)
            cpu = (start_cpu + end_cpu) / 2
            debit = taille / latence if latence > 0 else 0

            results.append({
                "requete": i,
                "latence": latence,
                "taille": taille,
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

ft.app(target=main)
