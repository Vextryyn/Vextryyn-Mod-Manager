# **Vextryyn’s Mod Manager**  
*(Name is not final, suggtestions welcome)*

This project is part of a larger mod-management tool I’ve been developing. Right now, there’s no solid Linux solution for managing PokeMMO mods, so this tool started as a way to fill that gap—not just for PokeMMO, but for other games I play as well. Since it’s functional and some people may find it useful, I’m releasing it, even if it’s still a bit rough around the edges.

For Windows users, there’s already a great mod manager by Ryukotsuki:  
**https://github.com/Ryukotsuki/Poke-Manager**

If that project ever gets a Linux port, I’ll likely wind down standalone development here and shift back to my broader project

---
**Requirements**
 - Git

 Arch
  - pacman -S git

 Debian/Ubuntu
  - apt install git

---
## **Current Feature Status**
_0.0.9_
Added Config Selector 
I included the default.json just in case, but I dont believe it is needed anymore with the changes I added. 

_Updated for 0.0.9_
### **Not Implemented Yet**
- Custom speech bubbles  
- Berry watering colors(colors should work, I rarely do berry stuff, so I havent tested yet. I dont want to move it to partial until I've confirmed its working)
- Discord Server

### **Partially Working**
- **Login Screen Preview**  
  - Basic animations load; layered animations (like Unova) don’t yet play correctly.
- **Encounter Counter**
  - Minimal counters aren’t included yet.  
    - If you are unclear what the difference is: Minimal mode shows only icons + counts; normal mode also shows Pokémon names.
  - Varitou Counter may not refresh on add, plese check Encounter Counter section for details
- **Mod Manager**
  - symlink handling
  - custom modfolder location
  
-**Not Working/In Progress**
  - No Mod enable/disable toggle yet — **anything in the list is active**.
  - Multiple mod profiles

---

## **Getting Started**

At this time, the mod manager will generate multiple folders for custom assets, so for now, it’s best to extract the appimage into its own directory. This is for your own sanity, its not a hard requirement. 

---

## **Features**

### **Login Screen**
You can add older login screen animations, and the manager will remove unnecessary files automatically.  
Testing options are limited since older animations are harder to find after recent game changes.  
If you have any animations that fail—or know where to find a complete set—please share them.

---

### **Encounter Counter**
Choose whichever counter style you prefer.

If you’re using **Vartiou’s counters**:
- Load the `.zip` as-is.
- The tool will place the required files automatically.
- You can load multiple Vartiou counters and switch between them freely.

**Note:** After adding a Vartiou counter, the preview may not refresh immediately.  
Toggling **Vartiou → any other selection → Vartiou** usually fixes it.

---

### **Window Colors**
Straightforward: choose your preferred color theme.

---

### **Custom Cursors** *(Available in v0.0.6a)*
Custom cursor import and preview are now supported.

- Default size is **128×64**, but other sizes should work fine.  
- The preview tool lets you assign regions for each cursor type.  
- Larger images produce larger in-game cursors.  
- If you work with unusual formats or need a bigger preview window, feedback is appreciated.

**Cursor Preview**
- Green rectangles mark cursor regions.
- Red dots show the hotspot (click point).
- For customization fields:  
  - X and Y is relative to the cursor's selection square.  
  - `xywh` is relative to the full image.

---

### **Mods**
A simple drag-and-drop mod manager:
- Rearrange mods by dragging them.  

---

### **Archetype**
- Checks whether your installed Archetype matches the latest version on GitHub.
- Alerts you if an update is available.
- Can automatically update Archetype when needed.
- Ensures the game path is correct and mod placement is valid.
- Config Selector, use for quickly choosing between configs
- Play mode, choose between Default Pokemmo, Gamescope fullscreen options and VKCapture(generally streaming related stuff)
- **Complete** applies mods and sets the Archetype theme.
- **Play PokeMMO** launches the game.

---
