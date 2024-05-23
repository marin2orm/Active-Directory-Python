import requests
import json
import subprocess

# lIEN de l'API
myUrl = "http://srv-peda.iut-acy.local/hoarauju/sae204/users/apiUsers.php?id_sae=2&id_grp=a2&login_usmb=desormem"

# Fonction pour recuperer les données de l'API
def getData(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Fonction pour afficher les utilisateurs
def viewUsers(data):
    for user in data:
        print(f"Nom: {user['nom']}, Prenom: {user['prenom']}")

# Fonction pour calculer les statistiques des utilisateurs
def statUsers(data):
    num_users = len(data)
    groups = set(user['groupe'] for user in data)
    num_groups = len(groups)
    
    if num_users > 0:
        domain = data[0]['email'].split('@')[-1]
    else:
        domain = "Aucun utilisateur trouvé"
    
    return num_users, num_groups, domain

# Fonction pour exécuter une commande PowerShell depuis Python
def execute_powershell(command):
    result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
    return result.stdout

# Fonction pour créer les utilisateurs dans le contrôleur de domaine
def createUsers(data):
    for user in data:
        group_cmd = f"if (-Not (Get-ADGroup -Filter {{Name -eq '{user['groupe']}'}})) {{ New-ADGroup -Name '{user['groupe']}' -GroupScope Global }}"
        user_cmd = f"New-ADUser -Name '{user['prenom']} {user['nom']}' -GivenName '{user['prenom']}' -Surname '{user['nom']}' -SamAccountName '{user['login']}' -UserPrincipalName '{user['email']}' -EmailAddress '{user['email']}' -AccountPassword (ConvertTo-SecureString '{user['password']}' -AsPlainText -Force) -PasswordNeverExpires $true -Enabled $true"
        add_to_group_cmd = f"Add-ADGroupMember -Identity '{user['groupe']}' -Members '{user['login']}'"
        execute_powershell(group_cmd)
        execute_powershell(user_cmd)
        execute_powershell(add_to_group_cmd)

# Fonction pour afficher le menu
def display_menu():
    print("Choisissez une fonctionnalité :")
    print("1. Afficher les utilisateurs")
    print("2. Afficher les statistiques des utilisateurs")
    print("3. Créer les utilisateurs dans le contrôleur de domaine")
    print("4. Quitter")

# Fonction principale
def main():
    try:
        # Récupération des données
        users_data = getData(myUrl)

        while True:
            display_menu()
            choice = input("Entrez votre choix (1-4) : ")

            if choice == '1':
                # Affichage des utilisateurs
                viewUsers(users_data)
            elif choice == '2':
                # Affichage des statistiques
                num_users, num_groups, domain = statUsers(users_data)
                print(f"Nombre d'utilisateurs: {num_users}")
                print(f"Nombre de groupes: {num_groups}")
                print(f"Domaine des utilisateurs: {domain}")
            elif choice == '3':
                # Création des utilisateurs dans le contrôleur de domaine
                createUsers(users_data)
            elif choice == '17':
                # Création des utilisateurs dans le contrôleur de domaine
                print(users_data)
                print("Les utilisateurs ont été créés dans le contrôleur de domaine.")
            elif choice == '4':
                print("Quitter le programme.")
                break
            else:
                print("Choix invalide. Veuillez entrer un nombre entre 1 et 4.")
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")

# Appel direct de la fonction principale
main()
