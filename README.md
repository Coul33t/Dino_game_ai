# Dino_game_ai
Smoll " AI " for the dino game http://www.trex-game.skipser.com/. It detects the presence and the position of **Mr T-Rex**, then tries to play at its best. It currently does not check for pterodactyl. Current record: 742

## How does it works?
The algorithm is very simple: 
1. Try to find **Mr T-Rex** on the screen. If he's not here, abort.
2. Compute 2 zones to check for black pixels: one in front of Mr T-Rex **(A)**, one at the location of the " GAME OVER " text **(B)**.
3. When the game starts (spacebar pressed), take screenshots at regular interval. After a certain number of frames have been captured, compute the mean value and max variation of black pixel density in **(A)**. Since there is no obstacle until a few frames, `mean + var` will be the threshold for sending our jump command (`val > mean + var`means that there's an obstacle in front of **Mr T-Rex**).
4. If the density of black pixel in **(A)** is higher than `mean + var`, send a jump command (press spacebar).
5. If there is a high density of black pixel in **(B)**, it means that there is the " GAME OVER " text in there, and so we lost the game.

### Libraries used
* OpenCV: detection of **Mr T-Rex** position
* pillow (PIL fork): screenshotting and detection of the catci (plural of cactus)
* pyautogui: automatic press on the spacebar
* pynput: detection of the start of the game (you have to press spacebar to start)
* matplotlib: plotting of the pixel density (debugging)

### Known bugs
* Pterodactyl can trigger the algorithm's stop condition
