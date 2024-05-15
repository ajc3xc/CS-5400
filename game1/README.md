#################################
#	Coding Standards	
#################################

You are free to use any of the following programming languages for your submission :

  - C++
  - C#
  - Java
  - Python3 (NOT Python2)
  - JavaScript
  - TypeScript

Your code must be well formatted and styled according to good coding standards, such as the MST coding standard outlined here :
https://bonsai.auburn.edu/dtauritz/coding.html

It is required that your code is well documented.

NOTE : Sloppy, undocumented, or otherwise unreadable code will be penalized for not following good coding standards (as laid out in the grading rubric on the course website)

#################################
#          !IMPORTANT!          
#################################

Read the README in the sub-directory corresponding to your chosen language.

Read the chess framework's documentation for your chosen language here :

- C++: https://siggame.github.io/Joueur.cpp/namespacecpp__client_1_1chess.html
- Python:https://siggame.github.io/Joueur.py/chess/index.html
- Typescript: https://siggame.github.io/Joueur.ts/modules/chess.html
- Javascript: https://siggame.github.io/Joueur.js/Chess.html
- C#: https://siggame.github.io/Joueur.cs/games/Joueur.cs.Games.Chess.html
- Java: https://siggame.github.io/Joueur.java/

#################################
#	Submission Rules	
#################################

Included in the top level of your repository is a file named `ReadyForGrading.txt`, which you will use to indicate which version of your code is the one to be graded as well as which programming language you're using; note that you may switch languages between assignments (though, it is not recommended...) . When you are ready to submit your final version, change the first line of this file to the word `yes` or `Yes` and the second line to your programming language, then commit and push your code. When entering your programming language, enter the **extension** of the language (`.py`,`.cs`,`.java`,`.ts`,`.js`, etc.). You may commit and push as much as you want, but your submission will be confirmed as "final" if the first line of "ReadyForGrading.txt" is "yes" at 11:59pm on the due date. If you do not plan to submit before the deadline, then you should NOT modify "ReadyForGrading.txt" until your final submission is ready. Once your final submission is ready, change the first line of "ReadyForGrading.txt" to "yes", commit and push your code, and do not make any further changes to it.


#################################
#       Compiling & Running	
#################################

You have been provided a bash script called `play.sh`, which compiles and runs your code; it also starts a game session between your AI and itself. DO NOT MODIFY THIS SCRIPT.
You can run `play.sh` using the following command format :
	`./play.sh Joueur.<lang> Session_ID`
Where Joueur.<lang> is the directory for the language you are coding in. An example of the above command for c++ would be :
	`./play.sh Joueur.cpp AIisAwesome`
