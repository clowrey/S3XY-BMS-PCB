#!/usr/bin/env python3
"""
Apply the component mapping to reassociate PCB footprints with schematic symbols.
"""

import re

# Direct mapping: PCB_REF -> (NEW_REF, SCHEMATIC_UUID)
MAPPING = {
    # MCU
    'U11': ('U27', 'e9131814-0fd0-4849-9e00-37477ad2ee85'),
    
    # Crystal
    'Y1': ('Y2', '114ce896-9d2e-4f4a-99c7-1d06169e7762'),
    
    # Inductor
    'L6': ('L7', '81ea4cab-2d71-4b8a-8c70-67ca8e9489c5'),
    
    # LED
    'D34': ('D33', '827f3c6a-8683-48e2-8797-78f8f7ccbf8c'),
    
    # Switches
    'SW1': ('SW3', 'c462dde2-8d33-4944-9461-42ab8017ec14'),
    'SW2': ('SW4', '8714c774-6e97-4614-ae33-6a064005529f'),
    
    # Connector
    'J9': ('J16', '3655f5dc-78f0-4980-abba-cb1727603416'),
    
    # Capacitors - PCB sorted -> SCH sorted
    'C27': ('C37', '6c7f03a8-70dd-4ebe-bb07-236673108691'),
    'C32': ('C48', 'ffd91b9f-ec3c-4091-b6d6-27f751d5a551'),
    'C35': ('C61', 'bc989d8d-9f40-41eb-b7ab-96d69ed0b185'),
    'C36': ('C69', 'ee311b15-2016-4c7e-83a2-5b1bee8661a5'),
    'C46': ('C71', '3f29c3b7-eebf-4047-9201-fee02c8c5fdf'),
    'C47': ('C72', '18988aca-3352-4f03-bec6-161e8a071ef0'),
    'C58': ('C117', '1a5988b0-b975-4058-bfd5-9895e9de44cc'),
    'C59': ('C118', '08a9067d-188d-4e72-8b0f-cc126224f7f5'),
    'C60': ('C120', '4e3eaf2c-55b8-4d46-b03b-d843768c9e56'),
    'C63': ('C123', '7aea52b4-3055-4f2a-aef2-798bda605aef'),
    'C64': ('C124', '0dcab54f-d5d7-4a99-babe-8c651bbd87b3'),
    'C65': ('C126', '8a796792-e1c8-45ae-a05f-2625b15906fd'),
    'C66': ('C127', '4d7b5974-73c5-4078-aa05-856c81275efe'),
    'C67': ('C128', '44b4b8ea-c748-4761-b496-627b1ace9521'),
    'C70': ('C129', '0f949479-a7e9-4af1-9b22-d27ba227d642'),
    'C74': ('C130', 'daf50076-ab18-45b1-baaa-0c4227b2f622'),
    'C78': ('C131', 'e41a5372-d764-49df-8ffa-b16dc5d8e01d'),
    
    # Resistors - PCB sorted -> SCH sorted
    'R33': ('R19', 'd0bb546d-01b1-47de-8ba8-9a857a26e9cb'),
    'R43': ('R21', 'f3d7b815-cebc-4b68-9446-81b032afa6de'),
    'R46': ('R24', 'e16f74c3-1aea-40eb-8095-078a827e1055'),
    'R49': ('R48', '6e4cf0f6-c652-479c-98b9-e9cf6e9c484d'),
    'R50': ('R58', '5f058f98-653f-4803-af1d-30e4b7222025'),
    'R51': ('R167', 'b0a946fc-02f0-414f-b178-91b6b13bd5a6'),
    'R52': ('R168', '773a0e0e-14d2-41d6-bb67-56306bf94f83'),
    'R56': ('R170', 'b98c1234-edff-4803-a0be-8a8d2638c8fb'),
    'R80': ('R171', '110cc942-f5d0-4c75-a2bb-e1d38da8302d'),
}


def apply_mapping(pcb_file, output_file):
    """Apply the mapping to the PCB file."""
    with open(pcb_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes_made = 0
    
    for old_ref, (new_ref, sch_uuid) in MAPPING.items():
        # Find all footprint blocks
        # Pattern to find footprint header with position
        pattern = r'(\t\(footprint "([^"]+)"\s*\n\t\t\(layer "[^"]+"\)\s*\n\t\t\(uuid "([a-f0-9-]+)"\)\s*\n\t\t\(at ([0-9.-]+) ([0-9.-]+))'
        
        for match in re.finditer(pattern, content):
            y_coord = float(match.group(5))
            
            # Only process components in copied area (Y < 180)
            if y_coord >= 180:
                continue
            
            # Find the full footprint block
            block_start = match.start()
            depth = 0
            block_end = block_start
            for i, char in enumerate(content[block_start:], block_start):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth == 0:
                        block_end = i + 1
                        break
            
            block = content[block_start:block_end]
            
            # Check if this block has the reference we're looking for
            ref_pattern = rf'\(property "Reference" "{re.escape(old_ref)}"'
            if not re.search(ref_pattern, block):
                continue
            
            # Check if already has a path (skip if already linked)
            if re.search(r'\(path "/[a-f0-9-]+"\)', block):
                print(f"Skipping {old_ref} - already linked")
                continue
            
            print(f"Processing {old_ref} -> {new_ref}")
            
            new_block = block
            
            # 1. Change reference in property
            new_block = re.sub(
                rf'(\(property "Reference" )"{re.escape(old_ref)}"',
                rf'\1"{new_ref}"',
                new_block
            )
            
            # 2. Add path, sheetname, sheetfile
            insert_text = f'\n\t\t(path "/{sch_uuid}")\n\t\t(sheetname "/")\n\t\t(sheetfile "isoSPI-M3Y-BMS-PCB.kicad_sch")'
            
            # Try to find (attr ...) and insert after it
            attr_match = re.search(r'\(attr [^\)]+\)', new_block)
            if attr_match:
                insert_pos = attr_match.end()
                new_block = new_block[:insert_pos] + insert_text + new_block[insert_pos:]
            else:
                # Insert before first (fp_line or (fp_arc
                fp_match = re.search(r'\n\t\t\(fp_', new_block)
                if fp_match:
                    insert_pos = fp_match.start()
                    new_block = new_block[:insert_pos] + insert_text + new_block[insert_pos:]
                else:
                    # Insert before first (pad
                    pad_match = re.search(r'\n\t\t\(pad ', new_block)
                    if pad_match:
                        insert_pos = pad_match.start()
                        new_block = new_block[:insert_pos] + insert_text + new_block[insert_pos:]
            
            # Update content with new block
            content = content[:block_start] + new_block + content[block_end:]
            changes_made += 1
            break  # Only process first match for this reference
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nTotal changes made: {changes_made}")
    print(f"Output written to: {output_file}")
    return changes_made


if __name__ == '__main__':
    pcb_file = 'isoSPI-M3Y-BMS-PCB.kicad_pcb'
    output_file = 'isoSPI-M3Y-BMS-PCB.kicad_pcb'
    
    print("=" * 60)
    print("Applying component mapping to reassociate PCB with schematic")
    print("=" * 60)
    print()
    
    changes = apply_mapping(pcb_file, output_file)
    
    if changes > 0:
        print("\n" + "=" * 60)
        print("SUCCESS! Please reload the PCB in KiCad.")
        print("Then run 'Update PCB from Schematic' (F8) to sync nets.")
        print("=" * 60)
