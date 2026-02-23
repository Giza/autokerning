import sys
import json
import argparse
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

def apply_kerning(font_path, json_path, output_path=None):
    # Load the JSON kerning data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    kerning_pairs = data.get('kerning', {})
    
    if not kerning_pairs:
        print("No kerning pairs found in JSON.")
        return

    # Load the font
    print(f"Loading font {font_path}...")
    font = TTFont(font_path)
    cmap = font.getBestCmap()
    units_per_em = font['head'].unitsPerEm

    # Generate feature file string for GPOS kerning
    fea_lines = [
        "languagesystem DFLT dflt;",
        "languagesystem latn dflt;",
        "languagesystem cyrl dflt;", # Explicitly add cyrillic
        "feature kern {",
    ]
    
    # Track pairs added
    added_count = 0
    for pair_str, value in kerning_pairs.items():
        if len(pair_str) != 2:
            continue
            
        l_char, r_char = pair_str[0], pair_str[1]
        l_code, r_code = ord(l_char), ord(r_char)
        
        l_glyph = cmap.get(l_code)
        r_glyph = cmap.get(r_code)
        
        if l_glyph and r_glyph:
            # Convert px to font units
            font_units_val = int(round((value / 100.0) * units_per_em))
            
            # Add positioning rule
            fea_lines.append(f"    pos {l_glyph} {r_glyph} {font_units_val};")
            added_count += 1
            
    fea_lines.append("} kern;")
    fea_string = "\n".join(fea_lines)

    print(f"Adding {added_count} kerning pairs to GPOS table via feature definitions...")
    
    # Use feaLib to compile the features and inject into the font
    # This automatically builds the robust GPOS structures needed by modern applications
    try:
        addOpenTypeFeaturesFromString(font, fea_string)
    except Exception as e:
        print(f"Error compiling features: {e}")
        return

    # Delete the legacy 'kern' table if it exists as it conflicts with GPOS
    if 'kern' in font:
        print("Deleting legacy 'kern' table to prevent conflicts.")
        del font['kern']

    # Save the modified font
    if not output_path:
        output_path = font_path.replace('.ttf', '_kerned.ttf').replace('.otf', '_kerned.otf')
        
    print(f"Saving modified font to {output_path}...")
    font.save(output_path)
    print("Done!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Inject kerning JSON into a TTF/OTF font file using GPOS.")
    parser.add_argument("font", help="Path to original TTF/OTF file")
    parser.add_argument("json", help="Path to kerning JSON file")
    parser.add_argument("-o", "--output", help="Output font file path", default=None)
    
    args = parser.parse_args()
    apply_kerning(args.font, args.json, args.output)
