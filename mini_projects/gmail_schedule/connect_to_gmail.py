import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Définir les scopes (permissions)
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

def authenticate_gmail():
    """
    Authentifier et créer le service Gmail.
    """
    creds = None
    
    # Le fichier token.pickle stocke les tokens d'accès
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Si pas de credentials valides, demander à l'utilisateur de se connecter
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Rafraîchissement du token...")
            creds.refresh(Request())
        else:
            print("🔐 Première connexion - Un navigateur va s'ouvrir...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Sauvegarder les credentials pour la prochaine fois
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print("✅ Authentification réussie!")
    
    return build('gmail', 'v1', credentials=creds)

def test_gmail_api():
    """
    Tester l'API Gmail en listant les 5 derniers emails.
    """
    try:
        service = authenticate_gmail()
        
        print("\n📧 Récupération des 5 derniers emails...\n")
        
        # Liste les messages
        results = service.users().messages().list(
            userId='me',
            maxResults=5
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("📭 Aucun message trouvé.")
            return
        
        print(f"✅ {len(messages)} messages trouvés:\n")
        
        for msg in messages:
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            
            headers = message['payload']['headers']
            
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Pas de sujet')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Inconnu')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Date inconnue')
            
            print(f"📨 De: {sender}")
            print(f"   Sujet: {subject}")
            print(f"   Date: {date}")
            print("-" * 80)
        
        print("\n🎉 L'API Gmail fonctionne parfaitement!")
        
    except HttpError as error:
        print(f"❌ Erreur: {error}")

if __name__ == "__main__":
    test_gmail_api()