import random
from typing import Optional, List

class MethaliDB:
    def __init__(self):
        self.proverbs = {
            "struggle": [
                "Kutoa ni moyo, usambe ni utajiri",  # Giving is from the heart, refusing is from wealth
                "Asiyefunzwa na mamaye hufunzwa na ulimwengu",  # Who isn't taught by mother is taught by the world
                "Haraka haraka haina baraka",  # Hurry hurry has no blessing
                "Mchimba kovu hulia kovu",  # The one who digs a hole falls in it
            ],
            "patience": [
                "Mpanda ngazi hushuka",  # He who climbs a ladder comes down
                "Subira yavuta heri",  # Patience brings good fortune
                "Mcheza kwao hutunzwa",  # He who plays at home is taken care of
            ],
            "wisdom": [
                "Fimbo ya mbali haiui nyoka",  # A stick from far doesn't kill a snake
                "Maji yakija hupwa",  # When water comes, it subsides
                "Usipoziba ufa, utajenga ukuta",  # If you don't fill the crack, you'll build a wall
            ],
            "friendship": [
                "Ikiwa hujui kufa, tazama kaburi",  # If you don't know death, look at the grave
                "Mwana wa mbwa ni mbwa",  # The child of a dog is a dog
                "Kidole kimoja hakivunji chawa",  # One finger doesn't crush a louse
            ],
            "success": [
                "Kupanda mchongoma, kushuka ngoma",  # Climbing the thorn tree, descending is a dance
                "Mchonga mawe kulia mwake",  # The stone carver cries for himself
                "Njia ya muongo ni fupi",  # The path of a liar is short
            ],
            "general": [
                "Samaki mkunje angali mbichi",  # Bend the fish while still fresh
                "Mchumia juani, hulia kivulini",  # He who exposes himself to the sun, cries in the shade
                "Kikulacho ki nguoni mwako",  # What eats you is in your clothes
                "Mgeni njoo, mwenyeji apone",  # Visitor come, host benefit
                "Kuuliza si ujinga",  # To ask is not foolishness
            ]
        }
    
    def get_relevant_proverb(self, context: str) -> Optional[str]:
        """Get proverb relevant to context"""
        context_lower = context.lower()
        
        for category, proverbs in self.proverbs.items():
            if category in context_lower:
                return random.choice(proverbs)
        
        # Check for keywords
        keywords = {
            "struggle": ["hard", "difficult", "shida", "ngumu", "problem", "sad"],
            "patience": ["wait", "subiri", "polepole", "haraka", "rush"],
            "wisdom": ["learn", "jifunze", "know", "jua", "understand", "elewa"],
            "friendship": ["friend", "rafiki", "bro", "help", "saidia"],
            "success": ["win", "shinda", "achieve", "fika", "promotion", "pass"]
        }
        
        for category, words in keywords.items():
            if any(word in context_lower for word in words):
                return random.choice(self.proverbs[category])
                
        return random.choice(self.proverbs["general"])
    
    def get_random_proverb(self) -> str:
        """Get random proverb"""
        all_proverbs = [p for proverbs in self.proverbs.values() for p in proverbs]
        return random.choice(all_proverbs)
    
    def explain_proverb(self, proverb: str) -> str:
        """Explain meaning of proverb"""
        explanations = {
            "Asiyefunzwa na mamaye hufunzwa na ulimwengu": 
                "Life itself will teach you lessons if you don't learn from elders first.",
            "Haraka haraka haina baraka": 
                "Rushing through things often means missing the blessings/details.",
            "Subira yavuta heri": 
                "Good things come to those who wait patiently.",
            "Kidole kimoja hakivunji chawa": 
                "You need teamwork/friends to solve big problems.",
            "Kuuliza si ujinga": 
                "There's no shame in asking questions when you don't know.",
            "Samaki mkunje angali mbichi": 
                "Fix problems while they're small, before they get big."
        }
        return explanations.get(proverb, "A wise saying from our elders.")