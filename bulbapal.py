import requests
from urllib.parse import unquote, quote
import pyperclip
import re

wikiResponse = requests.get(f'https://bulbapedia.bulbagarden.net/w/index.php?title=List_of_Pok%C3%A9mon_Trading_Card_Game_expansions&action=raw').text
EXPANSIONLIST = []
for wikiExpansion in re.finditer(r'\| {{TCG\|(.+?)(\|.+?)?}}[\s\S]+?\| ([\w\d]+?)\n\|(-|})', wikiResponse):
  EXPANSIONLIST.append([wikiExpansion.group(1), wikiExpansion.group(3)])
  
CARDNAMEREPLACES = [
  ['{G}', 'Grass'], 
  ['{W}', 'Water'], 
  ['{R}', 'Fire'], 
  ['{F}', 'Fighting'], 
  ['{L}', 'Lightning'], 
  ['{P}', 'Psychic'], 
  ['{C}', 'Colorless'], 
  ['{M}', 'Metal'], 
  ['{D}', 'Darkness'], 
  ['{N}', 'Dragon'], 
  ['{Y}', 'Fairy'],
  ['’', '\'']
]

CARDTYPEORDER = [
  'Grass',
  'Fire',
  'Water',
  'Lightning',
  'Fighting',
  'Psychic',
  'Colorless',
  'Darkness',
  'Metal',
  'Dragon',
  'Fairy',
  'Trainer',
  'Item',
  'Tool',
  'Pokémon Tool',
  'Stadium',
  'Supporter',
  'Energy'
]

def replace_all_array(text, array):
  for i in array:
    text = text.replace(i[0], i[1])
  return text

def beastFind(cardname):
  for beast in ['Nihilego','Buzzwole','Pheromosa','Xurkitree','Celesteela','Kartana','Guzzlord','Poipole','Naganadel','Stakataka','Blacephalon','Dusk Mane Necrozma','Dawn Wings Necrozma','Ultra Necrozma']:
    if cardname.find(beast) != -1:
      return True
  return False

def tcgReglink(cardname):
  return '[[' + cardname + '|' + cardname[:cardname.find('(')-1] + ']]'

def tcgID(bulbaUrl):
  bulbaUrl = unquote(bulbaUrl.replace('https://bulbapedia.bulbagarden.net/wiki/','')).replace('_',' ')
  #-id https://bulbapedia.bulbagarden.net/wiki/Galarian_Farfetch%27d_(Rebel_Clash_94)

  for testRule in ['4','G','GL','C','FB','M']:
    if bulbaUrl.find(' '+testRule+' ') != -1:
      return tcgReglink(bulbaUrl).replace(' '+testRule+']',']').replace(' '+testRule+' LV.X]',']') + '{{SP|' + testRule + '}}' + ('' if bulbaUrl.find(' LV.X (') == -1 else '[[' + bulbaUrl + '|LV.X]]')

  for testRule in ['-EX','{{EX}}'],[' V','{{TCGV}}'],[' VMAX','{{VMAX}}'],[' VSTAR', '{{VSTAR}}'],[' BREAK','{{BREAK}}'],[' ♢','{{Prism Star}}'],[' ☆','{{Star}}'],[' LEGEND','<br>{{LEGEND}}'],[' ex', '{{ex}}']:
    if bulbaUrl.find(testRule[0]+' ') != -1:
        return tcgReglink(bulbaUrl).replace(testRule[0]+']',']').replace('[[M ','{{Mega}}[[M ') + testRule[1] + ('' if bulbaUrl.find('δ') == -1 else '[[' + bulbaUrl + '|δ]]')

  #GX separate for Tag Team, Ultra Beast
  if bulbaUrl.find('-GX ') != -1:
    redGX = 'Red ' if beastFind(bulbaUrl) == True else ''
    ttGX = 'TT ' if bulbaUrl.find(' & ') != -1 else ''
    return tcgReglink(bulbaUrl).replace('-GX]',']') + '{{' + redGX + ttGX + 'GX}}'

  cardMon = bulbaUrl[:bulbaUrl.find('(')-1]
  cardSet = bulbaUrl[bulbaUrl.find('(')+1:bulbaUrl.rindex(' ')]
  cardNum = bulbaUrl[bulbaUrl.rindex(' ')+1:bulbaUrl.rindex(')')]
  return f'{{{{TCG ID|{cardSet}|{cardMon}|{cardNum}}}}}'

def tcgCD(bulbaUrl):
  if bulbaUrl.find('bulbagarden') == -1:
    return('Not a Bulbapedia link.')
  else:
    try:
      wikiResponse = requests.get(bulbaUrl.replace('/wiki/','/w/index.php?title=').replace('&action=raw','')+'&action=raw')
    except: raise
    if (wikiResponse.status_code != 200):
      return('Invalid link.')
    else:
      try:
        boxIndex = wikiResponse.text.index('ardInfobox/Expansion')
        cardBox = wikiResponse.text[wikiResponse.text[:boxIndex].rindex('{')+1:boxIndex]+'ardInfobox' #TCGEnergyCardInfobox, TCGTrainerCardInfobox
        
        searchableText = ('{{' + cardBox+wikiResponse.text[boxIndex+10:wikiResponse.text.rindex(cardBox+'/Footer')-1]).replace('|class=','|type=').replace('{{TCG|','').replace('{{rar|','').split('{{'+cardBox+'/Expansion')[1:] #not replacing '}' to '' here because of -1 index search later
        boxIndex = searchableText[0].find('|type=')+6
        realType = searchableText[0][boxIndex:searchableText[0][boxIndex:].find('|')+boxIndex]
        responseText = '{{cardlist/entry|cardname=' + tcgID(bulbaUrl) + '|type=' + ('Energy|energy=' if cardBox == 'TCGEnergyCardInfobox' else '') + realType
      except: raise

      setCounter = 1
      setNumText = ''
      for txtArray in searchableText:
        enSetIndex = txtArray.find('|expansion=')
        jpSetIndex = txtArray.find('|jpexpansion=')
        if jpSetIndex == -1:
            jpSetIndex = txtArray.find('|jphalfdeck=')
            
        if enSetIndex != -1 and (jpSetIndex == -1 or enSetIndex < jpSetIndex):
          responseText += txtArray[enSetIndex:jpSetIndex].replace('|expansion','|enset' + setNumText).replace('|rarity','|enrarity' + setNumText).replace('|cardno','|ennum' + setNumText).replace('}','')
        if jpSetIndex != -1 and enSetIndex < jpSetIndex:
          responseText += txtArray[jpSetIndex:-2].replace('|jpexpansion','|jpset' + setNumText).replace('|jphalfdeck','|jpset' + setNumText).replace('|jprarity','|jprarity' + setNumText).replace('|jpcardno','|jpnum' + setNumText).replace('}','')
        
        setCounter += 1
        setNumText = str(setCounter)
      
      responseText += '}}'

      return(responseText)

def tcgDCL(decklist):
  listEntry = r'^(\d+?) (.+?) ([A-Z]{3}) (\w+?)$'
  decklist = decklist.replace('\r', '')
  print(decklist)
  formattedList = ''
  unsortedCardData = []

  for line in decklist.split('\n'):
    if(re.match(listEntry, line)):
      entry = re.search(listEntry, line)      
      try: cardExpansion = [expansion[0] for expansion in EXPANSIONLIST if expansion[1] == entry.group(3)][0]
      except: cardExpansion = '?'
      
      cardName = quote(replace_all_array(entry.group(2), CARDNAMEREPLACES))
      cardNum = entry.group(4)
      urlTitle = f'{cardName}_({quote(cardExpansion)}_{cardNum})'.replace('%20', '_')
      cardUrl = f'https://bulbapedia.bulbagarden.net/wiki/{urlTitle}'
      cardUrlRaw = f'https://bulbapedia.bulbagarden.net/w/index.php?title={urlTitle}&action=raw'
      
      wikiResponse = requests.get(cardUrlRaw).text
      if wikiResponse.startswith('#REDIRECT'):
        urlTitle = quote(re.search(r'\[\[(.+?)\]', wikiResponse).group(1)).replace('%20', '_')
        cardUrlRaw = f'https://bulbapedia.bulbagarden.net/w/index.php?title={urlTitle}&action=raw'
        wikiResponse = requests.get(cardUrlRaw).text
      
      if wikiResponse != '' and wikiResponse.find('<title>Bad title - ') == -1:
        try: cardType = re.search(r'\|subclass=(.+?)(\n|\|)' , wikiResponse).group(1)
        except: cardType = re.search(r'\|type=(.+?)(\n|\|)' , wikiResponse).group(1)
        cardRarity = re.search(r'expansion={{TCG\|' + cardExpansion + r'}}.+?{{rar\|(.+?)}}\|cardno=0*?' + cardNum + r'(\/|\|)', wikiResponse).group(1)
        
        if wikiResponse.find('TCGEnergyCardInfobox') != -1:
          energyType = cardType
          cardType = 'Energy'
      else:
        cardType = 'None'
        cardRarity = 'None'
      
      cardTcgId = tcgID(cardUrl)
      formattedList += f'{{{{decklist/entry|{entry.group(1)}|{cardTcgId}|{cardType}|{energyType}|{cardRarity}}}}}\n'
      unsortedCardData.append([len(CARDTYPEORDER) if cardType not in CARDTYPEORDER else CARDTYPEORDER.index(cardType), 0 if '[' in cardTcgId else 1, cardName, cardExpansion, cardNum])

  if formattedList is not None:
    formattedList = '\n'.join([x for _, x in sorted(zip(unsortedCardData, formattedList.split('\n')))]) # sorting
    return('{{decklist/header}}\n' + formattedList + '\n{{decklist/footer}}')

def bulbaParse(message):
  message = message.replace('<','').replace('>','')
  if message == '-help': #not favoured for local
    return('Use a Bulbapedia link as the parameter.\n-id  <link>        {{TCG ID}}\n-cd  <link>        {{cardlist/entry}}\n-dcl <clipboard>    {{decklist/entry}}')

  if message.startswith('-id '):
    #-id https://bulbapedia.bulbagarden.net/wiki/Galarian_Farfetch%27d_(Rebel_Clash_94)
    try:
      return(tcgID(message[4:]))
    except:
      return('💥')

  elif message.startswith('-cd '):
    try:
      return(tcgCD(message[4:]))
    except:
      return('💥')
  
  elif message.startswith('-dcl'):
    try:
      clipboard = pyperclip.paste()
      return(tcgDCL(clipboard))
    except Exception as e:
      print(e)
    # except:
    #   return('💥')
