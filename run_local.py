import bulbapal #local
import sys
#import os #copy

result = bulbapal.bulbaParse(' '.join(sys.argv[1:]))
print(result)
"""
if result.startswith('{{') == True or result.startswith('[[') == True:
  for specialChar in ['^','&','<','>','|','´','`',',',';','=','(',')','!','"']:
    result = result.replace(specialChar, '^^^'+specialChar)
  os.system('echo ' + result.replace('%','%%%%') + '| clip')
  print('Copied to clipboard.')
"""
