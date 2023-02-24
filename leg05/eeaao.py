import json

keywords = json.load(open('eeaao_keywords.json'))
multiverses = json.load(open('eeaao_multiverses.json'))

# To check if to return keyword
def verse_jump(content):  
  location = content.split('$multiverse-', 1)[1]
  multiverseData = {}

  # Check if valid jump.
  try:
    multiverseData = multiverses[location]
    multiverseData["status"] = True
  except:
    # Not a valid jump. Return!
    return {"status": False}

  return multiverseData

def release_keyword(roles, keyword):
  # Check if Keyword should be released.
  for role in roles:
    try:
      assignedKeywords = keywords[str(role.id)]
      break
    except:
      continue

  if keyword in assignedKeywords:
    return True
  return False

def lumpia_attempt(roles, content):
  message = content.split('$everythinglumpia-', 1)[1]
  answers = message.split('-')
  
  if len(answers) != 6:
    return False

  validRole = False
  eeaaoData = []
  for role in roles:
    try:
      eeaaoData = keywords[str(role.id)]
      validRole = True
      break
    except:
      continue

  if not validRole:
    return False

  return answers == eeaaoData