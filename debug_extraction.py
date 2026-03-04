import json
from app.services.extraction import extract_chapter_intelligence

dummy_text = """
The sun set over the horizon. Beware of the shadows!
John walked into the tavern, looking for Lady Elara. 
Suddenly, Vael'Thar the ancient wizard appeared. 
"This is Zelithra Moonfall's domain," he proclaimed loudly.
No one expected a King to arrive like this.
There were Many people, but Only the Same few spoke.
The first day was peaceful. Last night was a nightmare.
He became a Tier-3 Mage after consulting the Inner Disciple.
They traveled from the Upper Realm to join the Azure Cloud Sect.
"""
print(json.dumps(extract_chapter_intelligence(dummy_text), indent=2))
