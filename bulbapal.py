import requests
from urllib.parse import unquote

def beastFind(cardname):
  for beast in ['Nihilego','Buzzwole','Pheromosa','Xurkitree','Celesteela','Kartana','Guzzlord','Stakataka','Blacephalon','Poipole','Poipole','Naganadel','Stakataka','Blacephalon',' Necrozma']:
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

  for testRule in ['-EX','{{EX}}'],[' V','{{TCGV}}'],[' VMAX','{{VMAX}}'],[' BREAK','{{BREAK}}'],[' ♢','{{Prism Star}}'],[' ☆','{{Star}}'],[' LEGEND','<br>{{LEGEND}}']:
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

def bulbaParse(message):
  message = message.replace('<','').replace('>','')
  if message == '-help': #not favoured for local
      return('Use a Bulbapedia link as the parameter.\n-id <link>         {{TCG ID}}\n-cd <link>         {{cardlist/entry}}')

  if message.startswith('-id '):
      #-id https://bulbapedia.bulbagarden.net/wiki/Galarian_Farfetch%27d_(Rebel_Clash_94)
      try:
        return(tcgID(message[4:]))
      except:
        return('💥')

  elif message.startswith('-cd '):
      #-cd https://bulbapedia.bulbagarden.net/wiki/Mawile_(Battle_Styles_100)
      if message[4:].find('bulbagarden') == -1:
        return('Not a Bulbapedia link.')
      else:
        try:
          wikiResponse = requests.get(message[4:].replace('/wiki/','/w/index.php?title=')+'&action=raw')
        except:
          return('💥')
        if (wikiResponse.status_code != 200):
          return('Invalid link.')
        else:
          try:
            typeIndex = wikiResponse.text.index('|type=')
            searchableText = wikiResponse.text[typeIndex:wikiResponse.text.index('{{PokémoncardInfobox/Footer')-1]
            responseText = '{{cardlist/entry|cardname=' + tcgID(message[4:]) + searchableText[:searchableText.index('\n')]
            searchableText = searchableText[searchableText.index('{{PokémoncardInfobox/Expansion'):].replace('{{TCG|','').replace('{{rar|','') #not replacing '}' to '' here because of -1 index search
          except:
            return('💥')

          setCounter = 1
          setNumText = ''
          for txtArray in searchableText.split('{{PokémoncardInfobox/Expansion')[1:]: #[1:] skips empty part
            enSetIndex = txtArray.find('|expansion=')
            jpSetIndex = txtArray.find('|jpexpansion=')
            if jpSetIndex == -1:
                jpSetIndex = txtArray.find('|jphalfdeck=')
                
            if enSetIndex != -1 and (jpSetIndex == -1 or enSetIndex < jpSetIndex):
              responseText += txtArray[enSetIndex:jpSetIndex-1].replace('|expansion','|enset' + setNumText).replace('|rarity','|enrarity' + setNumText).replace('|cardno','|ennum' + setNumText).replace('}','')
            if jpSetIndex != -1 and enSetIndex < jpSetIndex:
              responseText += txtArray[jpSetIndex:-1].replace('|jpexpansion','|jpset' + setNumText).replace('|jphalfdeck','|jpset' + setNumText).replace('|jprarity','|jprarity' + setNumText).replace('|jpcardno','|jpnum' + setNumText).replace('}','')
            
            setCounter += 1
            setNumText = str(setCounter)
          
          responseText += '}}'

          return(responseText)