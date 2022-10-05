#!
dot -Tpng -oattack_vs_defence.png  <<- EOM
digraph G
{
	rankdir=LR;

	PC->Monster [ label = "Attack 62%" ];
	PC->PC [ label = "Attack 62%" ];
	Monster->PC [ label = "Attack 38%" ];
	Monster->Monster [ label = "Attack 38%\n(But we don't care)" ];
}
EOM
