# **Vextryyn’s Mod Manager**  
*(Name is not final)*

This project is part of a larger mod-management tool I’ve been developing. Right now, there’s no solid Linux solution for managing PokeMMO mods, so this tool started as a way to fill that gap—not just for PokeMMO, but potentially for other games I play as well. Since it’s functional and some people may find it useful, I’m releasing it early, even if it’s still a bit rough around the edges.

For Windows users, there’s already a great mod manager by Ryukotsuki:  
**https://github.com/Ryukotsuki/Poke-Manager**

If that project ever gets a Linux port, I’ll likely wind down standalone development here and shift back to my broader project

**Extra note:** True Borderless will likely not be an option until there is something reliable for Wayland, I do not plan to do anything x11 since that will be going away in the near future. Debating on utilizng gamescope for advanced functions but unsure, there also seem to be some pretty universal solutions for hyperland, but I would rather a one approach works for all solution. Any recommendations are appreciated.

---
## **Current Feature Status**
_Updated for 0.0.6a_
### **Not Implemented Yet**
- Custom speech bubbles  
- Berry watering colors(colors should work, I rarely do berry stuff, so I havent tested yet. I dont want to move it to partial until I've confirmed its working)
- Discord Server(I just need to set up my docker bot again)

### **Partially Working**
- **Login Screen Preview**  
  - Basic animations load; layered animations (like Unova) don’t yet play correctly.
- **Encounter Counter**
  - Minimal counters aren’t included yet.  
    - If you are unclear what the difference is: Minimal mode shows only icons + counts; normal mode also shows Pokémon names.
  - Varitou Counter may not refresh on add, plese check Encounter Counter section for details
- **Mod Manager**
  - No enable/disable toggle yet — **anything in the list is active**.
  - does not check game mods folder for existing mods - **Will overwrite duplicates, but if existing is not in list it will not overwrite or enable**
  - **In Progress**:
    - symlinks
    - custom modfolder location
    - read existing non duplicate mods
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
Toggling **Normal → Vartiou → Normal** usually fixes it.

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
- **Complete** applies mods and sets the Archetype theme.
- **Play PokeMMO** launches the game.

---
