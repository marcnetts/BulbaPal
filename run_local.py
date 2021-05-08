import bulbapal #local
import os #copy

commandInput = None
prefixInput = ''
while commandInput != 'z':
    commandInput = input("Enter a command, type 'prefix' for automatic prefix or 'z' to quit:\n"+prefixInput)
    if commandInput == 'prefix':
        prefixInput = input("Enter an automatic prefix (example: '-cd ' with a space):\n")
    elif commandInput != 'z':
        result = bulbapal.bulbaParse(prefixInput+commandInput)
        print(result)

        if result != None and (result.startswith('{{') == True or result.startswith('[[') == True):
          for specialChar in ['^','&','<','>','|','´','`',',',';','=','(',')','!','"']:
            result = result.replace(specialChar, '^^^'+specialChar)
          os.system('echo|set/p=' + result.replace('%','%%%%') + '| clip')
          print('Copied to clipboard.')
