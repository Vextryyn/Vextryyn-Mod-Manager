import os

class PokeGen:
    @staticmethod
    def read_mod_lists(mods_folder: str):
        mod_order_file = os.path.join(mods_folder, "mod_order.txt")
        mod_disabled_file = os.path.join(mods_folder, "mod_disabled.txt")
        order = []
        if os.path.exists(mod_order_file):
            with open(mod_order_file, "r", encoding="utf-8") as f:
                order = [line.strip() for line in f if line.strip()]
        disabled = set()
        if os.path.exists(mod_disabled_file):
            with open(mod_disabled_file, "r", encoding="utf-8") as f:
                disabled = {line.strip() for line in f if line.strip()}
        return order, disabled

    @staticmethod
    def update_poke(file_path: str, mods_folder: str):
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        else:
            lines = []

        mods_list, disabled = PokeGen.read_mod_lists(mods_folder)
        enabled_ordered = [m for m in mods_list if m not in disabled]
        mods_str = "/".join(enabled_ordered)

        found_mods = False
        found_theme = False
        new_lines = []

        for line in lines:
            if line.strip().startswith("#"):
                new_lines.append(line)
                continue

            if line.startswith("client.mods.enabled_mods="):
                new_lines.append(f"client.mods.enabled_mods=archetype-theme/archetype-rounded-icons/{mods_str}\n")
                found_mods = True
            elif line.startswith("client.ui.theme="):
                new_lines.append(f"client.ui.theme=Archetype\n")
                found_theme = True
            else:
                new_lines.append(line)

        if not found_mods:
            new_lines.append(f"client.mods.enabled_mods={mods_str}\n")
        if not found_theme:
            new_lines.append(f"client.ui.theme=Archetype\n")

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        print(f"✅ Updated {file_path}")
        print(f" - client.mods.enabled_mods={mods_str}")
        print(f" - client.ui.theme=Archetype")
