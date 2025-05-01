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

    def lancer_test(e):
        result_table.rows.clear()
        try:
            nb = int(nb_field.value)
        except:
            page.dialog = ft.AlertDialog(title=ft.Text("⚠️ Erreur"), content=ft.Text("Nombre invalide"))
            page.dialog.open = True
            page.update()
            return

        use_https = protocol_field.value == "HTTPS"
        url = url_field.value.strip()

        page.splash = ft.ProgressRing()
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
        page.splash = None
        page.update()

    def exporter_csv(e):
        if not historique:
            return
        with open("resultats_detail.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Requête", "Latence (s)", "Taille (octets)", "Débit (o/s)", "CPU (%)"])
            for r in historique:
                writer.writerow([r["requete"], r["latence"], r["taille"], r["debit"], r["cpu"]])

    page.add(
        ft.Column([
            ft.Text("🧪 Analyse des performances HTTP vs HTTPS", size=22, weight="bold"),
            ft.Row([url_field]),
            ft.Row([protocol_field, nb_field]),
            ft.Row([
                ft.ElevatedButton("▶️ Lancer le test", on_click=lancer_test),
                ft.ElevatedButton("💾 Exporter CSV", on_click=exporter_csv),
            ]),
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
