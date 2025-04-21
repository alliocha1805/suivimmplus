import os
import json
import discord
import requests
from unidecode import unidecode

with open("debut.txt") as debut:
  baseHTMLraw = debut.readlines()
  baseHTML = ''.join(baseHTMLraw)

with open("fin.txt") as fin:
  finHTMLraw = fin.readlines()
  finHTML = ''.join(finHTMLraw)

with open('roster.json', encoding='utf-8') as f:
  data = json.load(f)
  roster = data["roster"]


def deleteRoster(membre):
  print("ten_tative suppresion---" + membre + "---")
  try:
    roster.remove(str(membre).strip())
    data["roster"] = roster
    with open('roster.json', 'w') as f:
      json.dump(data, f)
    return ("membre supprimé")
  except:
    return (
      "membre non trouvé dans le roster, veuillez verifier l'orthographe du pseudo avec la commande /suivimm+ liste"
    )


def addRoster(membre):
  print("tentative ajout---" + membre + "---")
  print(roster)
  try:
    roster.append(str(membre).strip())
    data["roster"] = roster
    print(data)
    with open('roster.json', 'w') as f:
      json.dump(data, f)
    return ("membre ajouté")
  except:
    print("nouveau roster", roster)
    return ("Erreur lors de l'ajout du membre " + membre)


def sortRoster(roster):
  roster = sorted(roster)
  data["roster"] = roster
  with open('roster.json', 'w') as f:
    json.dump(data, f)
  return ("Liste triée")


def getMMplusData(roster):
  tableau = ""
  sortie = []
  for elt in roster:
    endpoint = "https://raider.io/api/v1/characters/profile?region=eu&realm=Hyjal&name=" + elt + "&fields=mythic_plus_weekly_highest_level_runs,gear"
    print(endpoint)
    data_raw = requests.get(endpoint).content
    data = json.loads(data_raw)
    runs = data['mythic_plus_weekly_highest_level_runs']
    ilevel = data['gear']['item_level_equipped']
    nb_runs = len(runs)
    coffre1 = 0
    coffre2 = 0
    coffre3 = 0

    if nb_runs > 7:
      coffre1 = runs[0]["mythic_level"]
      coffre2 = runs[3]["mythic_level"]
      coffre3 = runs[7]["mythic_level"]
    elif nb_runs > 3:
      coffre1 = runs[0]["mythic_level"]
      coffre2 = runs[3]["mythic_level"]
    elif nb_runs > 0:
      coffre1 = runs[0]["mythic_level"]

    tupleS1 = previousWeekSecondChest(elt)
    secondChestS1 = tupleS1[0]
    nbRunS1 = tupleS1[1]
    datajoueur = {}
    datajoueur[elt] = [
      coffre1, coffre2, coffre3, ilevel, secondChestS1, nbRunS1
    ]
    sortie.append(datajoueur)
    tableau = tableau + "<tr><td>" + unidecode(elt) + "</td><td>" + str(
      coffre1) + "</td><td>" + str(coffre2) + "</td><td>" + str(
        coffre3) + "</td><td>" + str(ilevel) + "</td><td>" + str(
          secondChestS1) + "</td><td>" + str(nbRunS1) + "</td></tr>"
  htmlComplet = baseHTML + tableau + finHTML
  hs = open("sortiepropre.html", 'w')
  hs.write(htmlComplet)
  hs.close()
  return (sortie)


def getSlacker(roster):
  listeSlacker = []
  dataTemp = getMMplusData(roster)
  for elt in dataTemp:
    for clé in elt.keys():
      coffres = elt.get(clé)
      if coffres[0] >= 4 and coffres[1] >= 4:
        pass
      else:
        listeSlacker.append(clé)
  return (listeSlacker)


def previousWeekSecondChest(joueur):
  endpoint = "https://raider.io/api/v1/characters/profile?region=eu&realm=Hyjal&name=" + joueur + "&fields=mythic_plus_previous_weekly_highest_level_runs"
  print(endpoint)
  data_raw = requests.get(endpoint).content
  data = json.loads(data_raw)
  runs = data['mythic_plus_previous_weekly_highest_level_runs']
  nb_runs = len(runs)
  coffre2 = 0

  if nb_runs > 7:
    coffre2 = runs[3]["mythic_level"]
  elif nb_runs > 3:
    coffre2 = runs[3]["mythic_level"]

  return (coffre2, nb_runs)


class MyClient(discord.Client):

  async def on_ready(self):
    print('Logged in as')
    print(self.user.name)
    print(self.user.id)
    print('------')

  async def on_message(self, message):
    # we do not want the bot to reply to itself
    if message.author.id == self.user.id:
      return

    if message.content.startswith('/suivimm+ resume'):
      await message.channel.send(
        'Je calcule le tableau de suivi des MM+ {0.author.mention}'.format(
          message))
      getMMplusData(roster)
      await message.channel.send(file=discord.File('sortiepropre.html'))

    if message.content.startswith('/suivimm+ liste'):
      await message.channel.send(
        'Voici la liste des personnes suivies {0.author.mention}'.format(
          message))
      await message.channel.send(roster)

    if message.content.startswith('/suivimm+ delete'):
      pseudo = str(message.content).replace("/suivimm+ delete", "")
      retour = deleteRoster(pseudo)
      await message.channel.send(
        'Je lance la suppression {0.author.mention}'.format(message))
      await message.channel.send(retour)

    if message.content.startswith('/suivimm+ add'):
      pseudo = str(message.content).replace("/suivimm+ add", "")
      retour = addRoster(pseudo)
      await message.channel.send(
        'Je lance la modification {0.author.mention}'.format(message))
      await message.channel.send(retour)

    if message.content.startswith('/suivimm+ slacker'):
      await message.channel.send(
        'Je calcule la liste des slacker {0.author.mention}'.format(message))
      liste = getSlacker(roster)
      await message.channel.send(liste)

    if message.content.startswith('/suivimm+ help'):
      await message.channel.send(
        'Voici les commandes possibles {0.author.mention}'.format(message))
      await message.channel.send(
        "Pour lister le Roster configuré dans le bot /suivimm+ liste")
      await message.channel.send("Pour avoir le tableau recap /suivimm+ resume"
                                 )
      await message.channel.send(
        "Pour ajouter un joueur au roster /suivimm+ add [nom du joueur sans crochet]"
      )
      await message.channel.send(
        "Pour supprimer un joueur au roster /suivimm+ delete [nom du joueur sans crochet]"
      )
      await message.channel.send(
        "Pour voir tous les joueurs qui n'ont pas encore leurs deux coffres mini /suivimm+ slacker"
      )


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
my_token = os.environ['token']
client.run(my_token)
