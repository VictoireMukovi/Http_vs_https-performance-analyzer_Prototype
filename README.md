# 🌐 HTTP vs HTTPS Performance Analyzer

Une application interactive développée avec [Flet](https://flet.dev) qui permet de mesurer et comparer les performances des protocoles **HTTP** et **HTTPS** sur un site web donné.

Elle permet d’analyser :
- la **latence** (temps de réponse),
- la **taille totale** des données téléchargées (page et ressources),
- le **débit** moyen observé,
- et d’**exporter les résultats au format CSV**.

---

## 🚀 Fonctionnalités

✅ Interface graphique simple et intuitive  
✅ Saisie de l'URL à tester  
✅ Définition du nombre de requêtes à envoyer  
✅ Affichage des résultats dans deux tableaux (HTTP vs HTTPS)  
✅ Téléchargement et analyse des ressources (images, scripts, CSS...)  
✅ Export des résultats au format CSV

---

## 📸 Aperçu

![Aperçu de l'application](screenshot.png)

---

## 🛠️ Technologies utilisées

- [Flet](https://flet.dev) — pour la création d’une interface graphique moderne avec Python
- [Requests](https://docs.python-requests.org/en/latest/) — pour les requêtes HTTP/HTTPS
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) — pour l’analyse des ressources HTML
- CSV, time, urllib — bibliothèques standards de Python

---

## ⚙️ Installation

1. Clone ce dépôt :
```bash
git clone https://github.com/VictoireMukovi/Http_vs_https-performance-analyzer_Prototype.git
cd http-https-analyzer
