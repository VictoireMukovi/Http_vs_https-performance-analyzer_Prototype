import flet as ft
import requests
import time
import csv
import psutil

resultats = []

def mesurer_performance(url, use_https, num_requetes):
    protocol = "https" if use_https else "http"
    full_url = url.replace("http://", "").replace("https://", "")
    full_url = f"{protocol}://{full_url}"

    temps_total = 0
    taille_totale = 0
    start_cpu = psutil.cpu_percent(interval=None)

    for i in range(num_requetes):
        try:
            start_time = time.time()
            response = requests.get(full_url)
            end_time = time.time()
            latence = end_time - start_time
            taille = len(response.content)
            temps_total += latence
            taille_totale += taille
        except Exception as e:
            print(f"Erreur lors de la requête {i+1}: {e}")

    end_cpu = psutil.cpu_percent(interval=None)
    latence_moyenne = temps_total / num_requetes
    debit = taille_totale / temps_total
    cpu = (start_cpu + end_cpu) / 2

    return latence_moyenne, debit, taille_totale, cpu

def main(page: ft.Page):
    page.title = "Test HTTP/HTTPS - Victoire"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    url = ft.TextField(label="Entrez l'URL (ex: localhost/test.html)", expand=True)
    nb_requetes = ft.TextField(label="Nombre de requêtes", value="10", width=200)
    protocol = ft.Dropdown(
        label="Protocole",
        width=200,
        options=[
            ft.dropdown.Option("HTTP"),
            ft.dropdown.Option("HTTPS"),
        ],
        value="HTTP"
    )

    result_box = ft.Text("Résultats affichés ici", size=16)

    def lancer_test(e):
        try:
            nb = int(nb_requetes.value)
        except:
            result_box.value = "⚠️ Veuillez entrer un nombre valide de requêtes."
            page.update()
            return

        page.splash = ft.ProgressRing()
        page.update()

        latence, debit, taille, cpu = mesurer_performance(url.value, protocol.value == "HTTPS", nb)

        result_box.value = f"""
✅ Test terminé :
- Latence moyenne : {latence:.3f} s
- Débit : {debit/1024:.2f} Ko/s
- Taille totale : {taille} octets
- CPU : {cpu:.1f} %
"""
        result_box.color = ft.colors.GREEN
        resultats.clear()
        resultats.extend([
            ["Latence moyenne (s)", latence],
            ["Débit (Ko/s)", debit / 1024],
            ["Taille totale (octets)", taille],
            ["Utilisation CPU (%)", cpu]
        ])

        page.splash = None
        page.update()

    def exporter_csv(e):
        if not resultats:
            result_box.value = "⚠️ Aucun résultat à exporter."
            result_box.color = ft.colors.RED
            page.update()
            return

        with open("resultats_test.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Mesure", "Valeur"])
            writer.writerows(resultats)
        result_box.value = "📁 Résultats exportés dans 'resultats_test.csv'."
        result_box.color = ft.colors.BLUE
        page.update()

    page.add(
        ft.Column([
            ft.Text("📡 Testeur de performances HTTP vs HTTPS", size=22, weight="bold"),
            ft.Row([url]),
            ft.Row([protocol, nb_requetes]),
            ft.Row([
                ft.ElevatedButton("▶️ Lancer le test", on_click=lancer_test),
                ft.ElevatedButton("💾 Exporter CSV", on_click=exporter_csv, bgcolor=ft.colors.BLUE_200),
            ]),
            ft.Divider(),
            result_box,
        ], spacing=20)
    )

ft.app(target=main)
