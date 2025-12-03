#!/usr/bin/env python3
"""
Script to reassociate copied PCB components with U27's schematic circuit.
"""

import re
import os
from collections import defaultdict

def parse_schematic_components(sch_file):
    """Extract components from schematic that are above the sheet (negative Y)."""
    with open(sch_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    components = []
    
    # Split by symbol blocks - look for the pattern that starts a symbol instance
    # Pattern: tab + (symbol + newline
    parts = content.split('\n\t(symbol\n')
    
    for i, part in enumerate(parts[1:], 1):  # Skip first part (before any symbol)
        block = '\t(symbol\n' + part.split('\n\t)\n\t(symbol\n')[0]
        
        # Check for lib_name (indicates it's a library symbol copy, not definition)
        if '(lib_name ' not in block and '(lib_id ' not in block:
            continue
        
        # Extract lib_id
        lib_match = re.search(r'\(lib_id "([^"]+)"\)', block)
        if not lib_match:
            continue
        lib_id = lib_match.group(1)
        
        # Extract position from (at X Y) - first occurrence
        at_match = re.search(r'\(at ([0-9.-]+) ([0-9.-]+)', block)
        if not at_match:
            continue
        x, y = float(at_match.group(1)), float(at_match.group(2))
        
        # Only keep components with negative Y (above sheet)
        if y >= 0:
            continue
            
        # Extract UUID
        uuid_match = re.search(r'\(uuid "([a-f0-9-]+)"\)', block)
        if not uuid_match:
            continue
        uuid = uuid_match.group(1)
        
        # Extract Reference
        ref_match = re.search(r'\(property "Reference" "([^"]+)"', block)
        if not ref_match:
            continue
        reference = ref_match.group(1)
        
        # Skip power symbols by reference
        if reference.startswith('#'):
            continue
            
        # Extract footprint
        fp_match = re.search(r'\(property "Footprint" "([^"]+)"', block)
        footprint = fp_match.group(1) if fp_match else ""
        
        components.append({
            'reference': reference,
            'lib_id': lib_id,
            'footprint': footprint,
            'x': x,
            'y': y,
            'uuid': uuid
        })
    
    return components


def parse_pcb_components(pcb_file):
    """Extract footprints from PCB that are in the copied area (Y < 180) and unlinked."""
    with open(pcb_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    components = []
    
    # Split by footprint blocks
    parts = content.split('\n\t(footprint "')
    
    for i, part in enumerate(parts[1:], 1):
        block = '\t(footprint "' + part.split('\n\t)\n\t(footprint "')[0]
        
        # Extract footprint type
        fp_match = re.search(r'\(footprint "([^"]+)"', block)
        if not fp_match:
            continue
        footprint = fp_match.group(1)
        
        # Extract position - look for (at X Y in the block header area
        at_match = re.search(r'\(at ([0-9.-]+) ([0-9.-]+)', block)
        if not at_match:
            continue
        x, y = float(at_match.group(1)), float(at_match.group(2))
        
        # Only keep components in copied area (Y < 180)
        if y >= 180:
            continue
            
        # Extract UUID
        uuid_match = re.search(r'\(uuid "([a-f0-9-]+)"\)', block)
        if not uuid_match:
            continue
        uuid = uuid_match.group(1)
        
        # Extract Reference
        ref_match = re.search(r'\(property "Reference" "([^"]+)"', block)
        if not ref_match:
            continue
        reference = ref_match.group(1)
        
        # Check if it has a path (linked to schematic)
        has_path = bool(re.search(r'\(path "/[a-f0-9-]+"\)', block))
        
        # Only get unlinked components
        if has_path:
            continue
        
        components.append({
            'reference': reference,
            'footprint': footprint,
            'x': x,
            'y': y,
            'uuid': uuid,
        })
    
    return components


def get_footprint_type(footprint):
    """Categorize footprint by type."""
    fp_lower = footprint.lower()
    if 'rp2350' in fp_lower and ('qfn' in fp_lower or 'ep' in fp_lower):
        return 'MCU'
    if 'capacitor' in fp_lower or 'c_0' in fp_lower:
        return 'CAP'
    if 'resistor' in fp_lower or 'r_0' in fp_lower:
        return 'RES'
    if 'led' in fp_lower:
        return 'LED'
    if 'crystal' in fp_lower:
        return 'CRYSTAL'
    if 'l_pol' in fp_lower or 'inductor' in fp_lower:
        return 'INDUCTOR'
    if 'sw_push' in fp_lower or 'switch' in fp_lower:
        return 'SWITCH'
    if 'pinheader' in fp_lower or 'connector' in fp_lower or 'conn' in fp_lower:
        return 'CONNECTOR'
    return 'OTHER'


def create_mapping(sch_components, pcb_components):
    """Create a mapping from PCB components to schematic components based on footprint type."""
    
    # Group by footprint type
    sch_by_type = defaultdict(list)
    pcb_by_type = defaultdict(list)
    
    for comp in sch_components:
        fp_type = get_footprint_type(comp['footprint'])
        sch_by_type[fp_type].append(comp)
    
    for comp in pcb_components:
        fp_type = get_footprint_type(comp['footprint'])
        pcb_by_type[fp_type].append(comp)
    
    # Sort each group by reference number for consistent mapping
    for fp_type in sch_by_type:
        sch_by_type[fp_type].sort(key=lambda x: (x['reference'][0], int(re.search(r'\d+', x['reference']).group()) if re.search(r'\d+', x['reference']) else 0))
    
    for fp_type in pcb_by_type:
        pcb_by_type[fp_type].sort(key=lambda x: (x['reference'][0], int(re.search(r'\d+', x['reference']).group()) if re.search(r'\d+', x['reference']) else 0))
    
    mapping = []
    
    for fp_type in set(list(sch_by_type.keys()) + list(pcb_by_type.keys())):
        sch_list = sch_by_type.get(fp_type, [])
        pcb_list = pcb_by_type.get(fp_type, [])
        
        print(f"\n{fp_type}: {len(sch_list)} schematic, {len(pcb_list)} PCB")
        
        # Match by position in sorted list
        for i, pcb_comp in enumerate(pcb_list):
            if i < len(sch_list):
                sch_comp = sch_list[i]
                mapping.append({
                    'pcb_ref': pcb_comp['reference'],
                    'pcb_uuid': pcb_comp['uuid'],
                    'sch_ref': sch_comp['reference'],
                    'sch_uuid': sch_comp['uuid'],
                    'footprint_type': fp_type
                })
                print(f"  {pcb_comp['reference']} -> {sch_comp['reference']}")
            else:
                print(f"  {pcb_comp['reference']} -> NO MATCH (extra PCB component)")
    
    return mapping


def apply_mapping_to_pcb(pcb_file, mapping, output_file):
    """Apply the mapping to create a new PCB file with reassociated components."""
    with open(pcb_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for m in mapping:
        pcb_uuid = m['pcb_uuid']
        sch_uuid = m['sch_uuid']
        old_ref = m['pcb_ref']
        new_ref = m['sch_ref']
        
        # Find the footprint block by UUID
        # Pattern: (uuid "pcb_uuid")
        uuid_pattern = f'(uuid "{pcb_uuid}")'
        
        if uuid_pattern not in content:
            print(f"WARNING: Could not find UUID {pcb_uuid} in PCB file")
            continue
        
        # Find the start of this footprint block
        uuid_pos = content.find(uuid_pattern)
        
        # Find the footprint block start (search backward for (footprint)
        block_start = content.rfind('\t(footprint "', 0, uuid_pos)
        if block_start == -1:
            print(f"WARNING: Could not find footprint block start for {pcb_uuid}")
            continue
        
        # Find the end of this footprint block
        # Count parentheses to find matching close
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
        
        old_block = content[block_start:block_end]
        new_block = old_block
        
        # 1. Change reference
        new_block = re.sub(
            rf'\(property "Reference" "{re.escape(old_ref)}"',
            f'(property "Reference" "{new_ref}"',
            new_block
        )
        
        # 2. Add path and sheetinfo if not present
        if '(path "/' not in new_block:
            # Find position after (attr ...) or before first (fp_line
            # Insert path, sheetname, sheetfile
            insert_text = f'\n\t\t(path "/{sch_uuid}")\n\t\t(sheetname "/")\n\t\t(sheetfile "isoSPI-M3Y-BMS-PCB.kicad_sch")'
            
            # Find a good insertion point - after (attr ...) line
            attr_match = re.search(r'\(attr [^\)]+\)', new_block)
            if attr_match:
                insert_pos = attr_match.end()
                new_block = new_block[:insert_pos] + insert_text + new_block[insert_pos:]
            else:
                # Try inserting before first (fp_line
                fp_line_match = re.search(r'\n\t\t\(fp_line', new_block)
                if fp_line_match:
                    insert_pos = fp_line_match.start()
                    new_block = new_block[:insert_pos] + insert_text + new_block[insert_pos:]
        
        content = content[:block_start] + new_block + content[block_end:]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nWrote updated PCB to: {output_file}")


if __name__ == '__main__':
    sch_file = 'isoSPI-M3Y-BMS-PCB.kicad_sch'
    pcb_file = 'isoSPI-M3Y-BMS-PCB.kicad_pcb'
    output_file = 'isoSPI-M3Y-BMS-PCB.kicad_pcb'  # Overwrite original
    
    print("=" * 60)
    print("Parsing schematic components (above sheet)...")
    print("=" * 60)
    sch_components = parse_schematic_components(sch_file)
    
    print(f"Found {len(sch_components)} schematic components above sheet:")
    for comp in sorted(sch_components, key=lambda x: x['reference']):
        print(f"  {comp['reference']:10} | {comp['footprint'][:50]}")
    
    print("\n" + "=" * 60)
    print("Parsing PCB components (copied area, unlinked)...")
    print("=" * 60)
    pcb_components = parse_pcb_components(pcb_file)
    
    print(f"Found {len(pcb_components)} unlinked PCB components:")
    for comp in sorted(pcb_components, key=lambda x: x['reference']):
        print(f"  {comp['reference']:10} | {comp['footprint'][:50]}")
    
    print("\n" + "=" * 60)
    print("Creating mapping...")
    print("=" * 60)
    mapping = create_mapping(sch_components, pcb_components)
    
    print("\n" + "=" * 60)
    print(f"Total mappings: {len(mapping)}")
    print("=" * 60)
    
    # Ask for confirmation
    response = input("\nApply mapping to PCB file? (yes/no): ")
    if response.lower() == 'yes':
        apply_mapping_to_pcb(pcb_file, mapping, output_file)
        print("\nDone! Please reload the PCB file in KiCad and run DRC to verify.")
    else:
        print("Aborted.")
