from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pickle
from dotenv import load_dotenv
load_dotenv()
# Scopes nécessaires pour Gmail
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose'
]

def get_gmail_service():
    """Authentification et création du service Gmail."""
    creds = None
    
    # Le fichier token.pickle stocke les tokens d'accès et de rafraîchissement
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Si pas de credentials valides, demander à l'utilisateur de se connecter
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Sauvegarder les credentials pour la prochaine fois
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

@tool
def read_emails(max_results: int = 10, query: str = "") -> str:
    """
    Lire les emails de la boîte de réception.
    
    Args:
        max_results: Nombre maximum d'emails à récupérer (default: 10)
        query: Requête de recherche Gmail (ex: "from:example@gmail.com", "is:unread", "subject:meeting")
    
    Returns:
        Liste des emails avec sujet, expéditeur et extrait du contenu
    """
    try:
        service = get_gmail_service()
        
        # Récupérer les messages
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=query
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            return "Aucun email trouvé."
        
        emails_info = []
        for msg in messages:
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Pas de sujet')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Inconnu')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Date inconnue')
            
            # Extraire le corps du message
            if 'parts' in message['payload']:
                parts = message['payload']['parts']
                data = parts[0]['body'].get('data', '')
            else:
                data = message['payload']['body'].get('data', '')
            
            if data:
                text = base64.urlsafe_b64decode(data).decode('utf-8')
                snippet = text[:200] + "..." if len(text) > 200 else text
            else:
                snippet = message.get('snippet', 'Pas de contenu')
            
            emails_info.append(f"""
📧 Email ID: {msg['id']}
De: {sender}
Sujet: {subject}
Date: {date}
Extrait: {snippet}
{"=" * 50}
""")
        
        return "\n".join(emails_info)
    
    except HttpError as error:
        return f"Erreur lors de la lecture des emails: {error}"

@tool
def send_email(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
    """
    Envoyer un email.
    
    Args:
        to: Adresse email du destinataire
        subject: Sujet de l'email
        body: Corps du message
        cc: Adresses en copie (optionnel, séparées par des virgules)
        bcc: Adresses en copie cachée (optionnel, séparées par des virgules)
    
    Returns:
        Confirmation de l'envoi
    """
    try:
        service = get_gmail_service()
        
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        
        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc
        
        message.attach(MIMEText(body, 'plain'))
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        send_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return f"✅ Email envoyé avec succès! ID: {send_message['id']}"
    
    except HttpError as error:
        return f"❌ Erreur lors de l'envoi de l'email: {error}"

@tool
def search_emails(query: str, max_results: int = 10) -> str:
    """
    Rechercher des emails avec des critères spécifiques.
    
    Args:
        query: Requête de recherche Gmail (ex: "from:example@gmail.com is:unread", "subject:meeting after:2024/01/01")
        max_results: Nombre maximum de résultats (default: 10)
    
    Returns:
        Liste des emails correspondants
    """
    return read_emails(max_results=max_results, query=query)

@tool
def mark_as_read(email_id: str) -> str:
    """
    Marquer un email comme lu.
    
    Args:
        email_id: ID de l'email à marquer comme lu
    
    Returns:
        Confirmation
    """
    try:
        service = get_gmail_service()
        
        service.users().messages().modify(
            userId='me',
            id=email_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        
        return f"✅ Email {email_id} marqué comme lu"
    
    except HttpError as error:
        return f"❌ Erreur: {error}"

@tool
def mark_as_unread(email_id: str) -> str:
    """
    Marquer un email comme non lu.
    
    Args:
        email_id: ID de l'email à marquer comme non lu
    
    Returns:
        Confirmation
    """
    try:
        service = get_gmail_service()
        
        service.users().messages().modify(
            userId='me',
            id=email_id,
            body={'addLabelIds': ['UNREAD']}
        ).execute()
        
        return f"✅ Email {email_id} marqué comme non lu"
    
    except HttpError as error:
        return f"❌ Erreur: {error}"

@tool
def delete_email(email_id: str) -> str:
    """
    Supprimer un email (le mettre à la corbeille).
    
    Args:
        email_id: ID de l'email à supprimer
    
    Returns:
        Confirmation
    """
    try:
        service = get_gmail_service()
        
        service.users().messages().trash(
            userId='me',
            id=email_id
        ).execute()
        
        return f"🗑️ Email {email_id} déplacé vers la corbeille"
    
    except HttpError as error:
        return f"❌ Erreur: {error}"

@tool
def get_unread_count() -> str:
    """
    Obtenir le nombre d'emails non lus.
    
    Returns:
        Nombre d'emails non lus
    """
    try:
        service = get_gmail_service()
        
        results = service.users().messages().list(
            userId='me',
            q='is:unread'
        ).execute()
        
        count = results.get('resultSizeEstimate', 0)
        
        return f"📬 Vous avez {count} email(s) non lu(s)"
    
    except HttpError as error:
        return f"❌ Erreur: {error}"

@tool
def reply_to_email(email_id: str, body: str) -> str:
    """
    Répondre à un email.
    
    Args:
        email_id: ID de l'email auquel répondre
        body: Corps de la réponse
    
    Returns:
        Confirmation
    """
    try:
        service = get_gmail_service()
        
        # Récupérer l'email original
        original = service.users().messages().get(
            userId='me',
            id=email_id,
            format='full'
        ).execute()
        
        headers = original['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        to = next((h['value'] for h in headers if h['name'] == 'From'), '')
        
        # Créer la réponse
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = f"Re: {subject}" if not subject.startswith('Re:') else subject
        message['In-Reply-To'] = email_id
        message['References'] = email_id
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        send_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message, 'threadId': original['threadId']}
        ).execute()
        
        return f"✅ Réponse envoyée avec succès! ID: {send_message['id']}"
    
    except HttpError as error:
        return f"❌ Erreur: {error}"

# Créer l'agent Gmail
def create_gmail_agent():
    """Créer un agent pour gérer Gmail."""
    
    llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    
    tools = [
        read_emails,
        send_email,
        search_emails,
        mark_as_read,
        mark_as_unread,
        delete_email,
        get_unread_count,
        reply_to_email
    ]
    
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt="""You are a Gmail management assistant. You can:
        - Read and search emails
        - Send emails and reply to messages
        - Mark emails as read/unread
        - Delete emails
        - Get unread email count
        - Resume emails
        
        Always be helpful and confirm actions before executing them if they're destructive (like deleting emails).
        When searching, use Gmail search operators like:
        - 'from:email@example.com' to search by sender
        - 'subject:meeting' to search by subject
        - 'is:unread' for unread emails
        - 'after:2024/01/01' for emails after a date
        """
    )
    
    return agent

# Utilisation
if __name__ == "__main__":
    agent = create_gmail_agent()
    
    # Exemples d'utilisation
    examples = [
        "Combien d'emails non lus j'ai aujourd'hui ?",
        "Résume mes 5 derniers emails",
        "Recherche les emails de no-reply@doctolib.fr",
        "Envoie un email à leonard.agbedjinou@gmail.com avec le sujet 'Réunion' et le message 'Bonjour, confirmes-tu pour demain ?'",
    ]
    
    # Test
    for prompt in examples:
        result = agent.invoke({
            "messages": [("user", prompt)]
        })
        
        print(result["messages"][-1].content)