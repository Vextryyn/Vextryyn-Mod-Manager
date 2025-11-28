Overall this is part of a larger Mod Manager project im working on. At the time im opening this up, there is no viable linux solution for pokemmo mod management, so I figured this was a good starting point for a mod manager that works for all the games I play. Since it functions I decided someone out there may find it useful. Still pretty ugly and will need a full rewrite before I consider it finished.

For Windows, there is a perfectly viable solution by Ryukotsuki https://github.com/Ryukotsuki/Poke-Manager

Whenever a Linux port is released by Ryukotsuki, I will likely quit building only this and pivot back to my main project.

Not implemented yet:
Custom Cursors
Custom Speech Bubbles
Berry watering colors

Partially functional:
Login Screen Preview - complex animations like the Unova login screen may work but I havent gotten the layered animations to play correctly just yet
Encounter Counter - minimal counters have not been added for preview yet, please note they are just icons and counts, where normal also has pokemon names

How To:

For right now, I recommend to extract in its own folder. At this moment I havent moved all folders into cache or set up automated cleanup for most things, so it will keep your custom items in their respective folders.

1. Login Screen
    You should be able to just add old login screen animations and it will remove all the old fluff and should load in correctly. I have had a tough time tracking down the old login screen animations since the change, so i have limited testing material. If you have any that do not work, or can point me to where i can find all the old login animations please let me know.

2. Encounter Counter
    choose whichever counter you like, if you want to use one of Vartiou's counters, just load in the zip file and it will move the nessecary files to the correct location. You can load in as many Vartiou counters as you would like and you can choose at will.
    
    Bug Note: it doesnt update right away after adding the varitou, just toggle the encounter counter type to normal and back to Vartiou

3. Window Colors
    pretty self explanitory, choose your colors

4. Other
    Selections work, but no previews or customs currently

5. Mods
    Simple drag and drop mod manager, drag mods to rearrange them. Currently there is no enable disabled option so anything included will be enabled.

6. Archetype
    Confirms if your Archetype matches what is on thier git, and informs if an update is available.
    Download will update Archetype if an update is available
    Game path ensures mods will go to the correct location and ensure you can start the game
    Complete adds the mods to pokemmo, and sets the theme to Archetype. 
    Play Pokemmo does what it says. 