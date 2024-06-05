import telebot
import os

# Token de votre bot
TOKEN = '6665713484:AAGpxZHYArpBAT7o9aLvjjcHyrlozNpsuRU'
CHANNEL_ID = '-1002155850946'
DATA_FILE = 'invitation_links.txt'

# Initialiser le bot
bot = telebot.TeleBot(TOKEN)


def save_link(user_id, invite_link):
    with open(DATA_FILE, 'a') as f:
        f.write(f'{user_id},{invite_link},0\n')


def load_links():
    links = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            for line in f:
                user_id, link, count = line.strip().split(',')
                links[link] = {'user_id': user_id, 'count': int(count)}
    return links


def update_link_count(link):
    links = load_links()
    if link in links:
        links[link]['count'] += 1
        with open(DATA_FILE, 'w') as f:
            for link, data in links.items():
                f.write(f"{data['user_id']},{link},{data['count']}\n")


def get_user_invites(user_id):
    links = load_links()
    count = sum(data['count'] for link, data in links.items() if data['user_id'] == str(user_id))
    return count


def generate_link(message):
    try:
        user_id = message.from_user.id
        has_link = False
        links = load_links()
        for link, data in links.items():
            if data['user_id'] == str(user_id):
                has_link = True
                bot.reply_to(message, f"Your invite link is {link}")
                break
        if not has_link:
            invite_link = bot.export_chat_invite_link(CHANNEL_ID)
            save_link(user_id, invite_link)
            bot.reply_to(message, f"The invite link for the channel is {invite_link}")

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")


# Fonction de démarrage
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hello! I am a bot to help you get the invite link for the channel. Also, I can tell you how "
                          "many people you have invited to the channel. Just type /link to get the invite link and "
                          "/count to get the number of people you invited to the channel.")


# Gestionnaire de commande pour obtenir le lien
@bot.message_handler(commands=['link'])
def send_link(message):
    generate_link(message)


# Gestionnaire de commande pour obtenir le nombre d'utilisations du lien
@bot.message_handler(commands=['count'])
def send_count(message):
    user_id = message.from_user.id
    count = get_user_invites(user_id)
    bot.reply_to(message, f"You have invited {count} people to the channel with your link.")


# Gestionnaire pour détecter quand quelqu'un rejoint le groupe
@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    for new_member in message.new_chat_members:
        invite_link = message.invite_link
        if invite_link:
            update_link_count(invite_link)


# Fonction principale pour démarrer le bot
def main() -> None:
    bot.polling()


if __name__ == '__main__':
    main()
