from pickle import NONE
import YGOlogic as ygo


magoNegro = ygo.Card("Mago Negro", 2500, 2100, ygo.CardType.MONSTER, NONE);
dragaoNegro = ygo.Card("Dragão Negro de Olhos Vermelhos", 2500, 2100, ygo.CardType.MONSTER, NONE);
dragaoBranco = ygo.Card("Dragão Branco de Olhos Azuis", 3000, 2500, ygo.CardType.MONSTER, NONE);
raigeki = ygo.Card("Raigeki", NONE, NONE, ygo.CardType.MAGIC, "Destrói todos o monstros no campo");
monsterReborn = ygo.Card("Monstro que renasce", NONE, NONE, ygo.CardType.MAGIC, "Ressuscita um monstro do cemitério");


Player1 = ygo.Player(input("Input the player's name: "), 4000, [magoNegro, dragaoNegro, dragaoBranco, raigeki, monsterReborn]);
Player1.shuffleDeck();
Player1.initialHand();


for card in Player1.hand:
    print(f"{card.getName()}");
