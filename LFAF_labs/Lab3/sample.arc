~~ ArcaneScript Sample Program
~~ Demonstrates all major token categories

~~ Variable declarations
summon health = 100;
summon mana   = 75.5;
summon name   = "Eftode Andrei";
summon alive  = true_rune;

~~ Arithmetic & power operator
summon damage = 3 ** 2 + health * 0.1 - mana / 5.0;

~~ Function definition
cast heal(target, amount) {
    summon new_hp = target + amount;
    if_cursed (new_hp > 100) {
        banish 100;
    }
    else_ward {
        banish new_hp;
    }
}

~~ Loop with logical operator
summon counter = 5;
while_enchanted (counter != 0 && alive == true_rune) {
    inscribe("Casting spell...");
    summon counter = counter - 1;
}

~~ Function call & comparison chain
summon result = heal(health, 25);
if_cursed (result >= 100) {
    inscribe("Fully healed!");
}
else_ward {
    inscribe("Still wounded.");
}
