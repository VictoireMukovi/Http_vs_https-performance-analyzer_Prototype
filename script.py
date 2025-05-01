import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import time
import csv
import psutil

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
    debit = taille_totale / temps_total  # en octets/sec
    cpu = (start_cpu + end_cpu) / 2

    return latence_moyenne, debit, taille_totale, cpu

def lancer_test():
    url = url_entry.get()
    use_https = protocol_var.get() == "HTTPS"
    try:
        num = int(nb_requetes_entry.get())
    except:
        messagebox.showerror("Erreur", "Nombre de requêtes invalide.")
        return

    latence, debit, taille, cpu = mesurer_performance(url, use_https, num)

    result_label.config(text=f"Latence moyenne : {latence:.3f} s\nDébit : {debit/1024:.2f} Ko/s\nTaille totale : {taille} octets\nCPU : {cpu:.1f} %")
    save_button.config(state=tk.NORMAL)
    result_data.clear()
    result_data.extend([["Latence moyenne (s)", latence],
                        ["Débit (Ko/s)", debit / 1024],
                        ["Taille totale (octets)", taille],
                        ["Utilisation CPU (%)", cpu]])

def exporter_csv():
    fichier = filedialog.asksaveasfilename(defaultextension=".csv")
    if fichier:
        with open(fichier, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Mesure", "Valeur"])
            writer.writerows(result_data)
        messagebox.showinfo("Exporté", "Résultats exportés avec succès.")

# Interface graphique
fenetre = tk.Tk()
fenetre.title("Test HTTP/HTTPS")

tk.Label(fenetre, text="URL :").grid(row=0, column=0)
url_entry = tk.Entry(fenetre, width=40)
url_entry.grid(row=0, column=1, columnspan=2)

tk.Label(fenetre, text="Protocole :").grid(row=1, column=0)
protocol_var = tk.StringVar(value="HTTP")
ttk.OptionMenu(fenetre, protocol_var, "HTTP", "HTTP", "HTTPS").grid(row=1, column=1)

tk.Label(fenetre, text="Nb de requêtes :").grid(row=2, column=0)
nb_requetes_entry = tk.Entry(fenetre)
nb_requetes_entry.insert(0, "10")
nb_requetes_entry.grid(row=2, column=1)

tk.Button(fenetre, text="Lancer le test", command=lancer_test).grid(row=3, column=0, columnspan=3, pady=10)

result_label = tk.Label(fenetre, text="Résultats affichés ici")
result_label.grid(row=4, column=0, columnspan=3)

save_button = tk.Button(fenetre, text="Exporter en CSV", command=exporter_csv, state=tk.DISABLED)
save_button.grid(row=5, column=0, columnspan=3, pady=10)

result_data = []

fenetre.mainloop()
