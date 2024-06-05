import telebot
import os

# Token de votre bot
TOKEN = '7430083181:AAEyb-dauAs2B3vq-tFDXbFyVj9FGwVZ58A'
CHANNEL_ID = "-1002155850946"
DATA_FILE = 'invitation_links.txt'

# Initialiser le bot
bot = telebot.TeleBot(TOKEN)

already_invited = set()
def generate_link(message, username):
    invitor = message.from_user.username
    key = f"{invitor}:{username}"
    if key in already_invited:
        bot.reply_to(message, "Don't be greedy! You have already got the invite link from this user.")
        return

    with open(DATA_FILE, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if username in line:
                username, count = line.strip().split()
                count = int(count) + 1
                lines[i] = f"{username} {count}\n"
                break
        else:
            lines.append(f"{username} 1\n")

    with open(DATA_FILE, 'w') as file:
        file.writelines(lines)

    # Envoyer le lien d'invitation
    link = bot.export_chat_invite_link(CHANNEL_ID)
    bot.reply_to(message, f"Here is the invite link for the channel: {link}")

    # Ajouter le nom d'utilisateur à l'ensemble des utilisateurs qui ont déjà invité quelqu'un
    already_invited.add(key)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
                 "Hello! I am a bot to help you get the invite link for the channel.\n\n Also, I can tell you how "
                 "many people you have invited to the channel.\n\n Just type /link to get the invite link and "
                 "/count to get the number of people you invited to the channel.")


# Gestionnaire de commande pour obtenir le lien
@bot.message_handler(commands=['link'])
def ask_for_username(message):
    msg = bot.send_message(message.chat.id, "Please enter the username of the person who invited you to the channel with @")
    bot.register_next_step_handler(msg, process_username)


def process_username(message):
    invitor = message.text
    username = message.from_user.username

    if invitor == "@" + username:
        bot.reply_to(message, "You cannot invite yourself to the channel.")
    elif invitor.startswith('@'):
        generate_link(message, invitor)
    else:
        bot.reply_to(message, "Please enter a valid username starting with @")


# Gestionnaire de commande pour obtenir le nombre d'utilisations du lien
@bot.message_handler(commands=['count'])
def send_count(message):
    with open(DATA_FILE, 'r') as file:
        lines = file.readlines()
        for line in lines:
            username, count = line.strip().split()
            if username == "@" + message.from_user.username:
                bot.reply_to(message, f"You have invited {count} people to the channel.")
                break
        else:
            bot.reply_to(message, "You have not invited anyone to the channel yet.")


# Fonction principale pour démarrer le bot
def main() -> None:
    bot.polling()


if __name__ == '__main__':
    main()
