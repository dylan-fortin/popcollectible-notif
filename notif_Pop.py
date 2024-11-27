import requests
import re
import time
from plyer import notification
from datetime import datetime

# URL principale du site
URL = "https://popcollectibles.ca"
DISCORD_WEBHOOK_URL = "token"

# Liste pour stocker les noms d'images déjà détectés
detected_images = set()
initialized = False   # Indique si le script a déjà fait une vérification complète

# Variable pour stocker la date de la dernière réinitialisation
last_reset_date = None

# Fonction pour récupérer les noms des images depuis le code source
def fetch_image_names():
    response = requests.get(URL)
    if response.status_code != 200:
        print("Erreur lors de la connexion au site.")
        return []
    # Recherche des URLs d'images dans le dossier cdn/shop/files
    image_urls = re.findall(r'cdn/shop/files/([\w\-]+)\.jpg', response.text)
    
    # Extraire uniquement la partie avant le premier underscore
    image_names = [name.split('_')[0] for name in image_urls]
    return image_names

# Fonction pour envoyer une notification sur Discord
def send_discord_notification(image_name):
    message = f"Nouveau Funko:\n{image_name}\n###################"
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    
    if response.status_code == 204:
        print("Notification envoyée sur Discord avec succès !")
    else:
        print(f"Erreur lors de l'envoi : {response.status_code}, {response.text}")

# Fonction pour réinitialiser le set à minuit chaque jour
def reset_set_at_midnight():
    global detected_images, last_reset_date
    current_time = datetime.now()
    current_date = current_time.date()  # Extraire la date (sans l'heure)
    
    # Vérifier si la date a changé, et si oui, réinitialiser le set
    if last_reset_date != current_date:
        detected_images = set()  # Réinitialiser le set des images détectées
        last_reset_date = current_date  # Mettre à jour la date de réinitialisation
        initialized = False  
        print(f"Set réinitialisé à minuit le {current_date}.")

# Boucle principale pour surveiller les nouvelles images
def monitor_images():
    global initialized
    print("Surveillance des nouveaux Funko Pops en cours...")
    while True:
        try:
            # Vérification pour réinitialiser le set à minuit
            reset_set_at_midnight()
            
            image_names = fetch_image_names()
            if image_names:
                # Filtrer les nouvelles images
                new_images = [name for name in image_names if name not in detected_images]
                
                # Ne pas envoyer de notification au premier passage
                if initialized and new_images:
                    print("Nouvelles images détectées :", new_images)
                    for image in new_images:
                        send_discord_notification(image)
                
                # Mettre à jour la liste des images détectées
                detected_images.update(image_names)
                initialized = True  # Marque le script comme initialisé après le premier passage
            
            time.sleep(300)  # Pause de 5 minutes entre les vérifications
        except Exception as e:
            print(f"Erreur : {e}")
            time.sleep(300)  # Attente de 5 minutes avant de réessayer

if __name__ == "__main__":
    monitor_images()
