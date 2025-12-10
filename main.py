#!/usr/bin/env python3
import argparse
import sys
import re
from datetime import datetime

def parse_mermaid(code):
    lines = code.strip().split('\n')
    entities = {}
    relationships = []
    current_entity = None
    for line in lines:
        line = line.strip()
        if line.startswith('erDiagram'):
            continue
        if '{' in line and not line.startswith(' ') and not any(x in line for x in ['||', 'o{', '}|']):
            entity_name = line.split('{')[0].strip()
            entities[entity_name] = []
            current_entity = entity_name
        elif line == '}':
            current_entity = None
        elif current_entity and line:
            entities[current_entity].append(line)
        elif any(x in line for x in ['||', 'o{', '}|', '}']):
            parts = line.split(':')
            rel_part = parts[0].strip()
            label = parts[1].strip() if len(parts) > 1 else ''
            # parse relationship
            # e.g. CUSTOMER ||--o{ ORDER
            # split by spaces, but card has ||
            # use regex to find entities
            # assume format: ENT1 CARD ENT2
            match = re.match(r'([A-Za-z_][A-Za-z0-9_-]*)\s+(.+?)\s+([A-Za-z_][A-Za-z0-9_-]*)', rel_part)
            if match:
                ent1, card, ent2 = match.groups()
                relationships.append((ent1, ent2, card, label))
    return entities, relationships

def get_arrow(card):
    # map cardinality to draw.io arrows
    # ||--|| : one to one : ERone to ERone
    # ||--o{ : one to many : ERone to ERzeroToMany
    # o{--|| : many to one : ERzeroToMany to ERone
    # o{--o{ : many to many : ERzeroToMany to ERzeroToMany
    if card == '||--||':
        return 'ERone', 'ERone'
    elif card in ['||--o{', '||--|{']:
        return 'ERone', 'ERzeroToMany'
    elif card == '}o--||':
        return 'ERzeroToMany', 'ERone'
    elif card == 'o{--o{':
        return 'ERzeroToMany', 'ERzeroToMany'
    else:
        return 'none', 'none'  # default

def generate_drawio_xml(entities, relationships):
    now = datetime.now().isoformat() + 'Z'
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="{now}" agent="ER-CLI" version="21.0.0">
  <diagram name="ER Diagram" id="diagram_1">
    <mxGraphModel dx="1000" dy="600" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1600" pageHeight="1200" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>'''

    cell_id = 2
    entity_positions = {}
    positions = [(40, 40), (590, 40), (1140, 40), (40, 550), (590, 550), (1140, 550), (1690, 550), (2240, 550)]
    for i, (entity, attrs) in enumerate(entities.items()):
        entity_positions[entity] = f"entity{cell_id}"
        height = 30 + len(attrs) * 22
        x, y = positions[i % len(positions)]
        xml += f'''
        <mxCell id="{entity}" value="{entity}" style="swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=30;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=0;marginBottom=0;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="{x}" y="{y}" width="200" height="{height}" as="geometry"/>
        </mxCell>'''
        y_offset = 30
        for attr in attrs:
            xml += f'''
        <mxCell id="{entity}_attr{attrs.index(attr)}" value="{attr}" style="text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;" vertex="1" parent="{entity}">
          <mxGeometry y="{y_offset}" width="200" height="22" as="geometry"/>
        </mxCell>'''
            y_offset += 22
        cell_id += 1 + len(attrs)

    entity_pos = {entity: positions[i] for i, entity in enumerate(entities.keys())}

    for rel in relationships:
        ent1, ent2, card, label = rel
        start_arrow, end_arrow = get_arrow(card)
        pos1 = entity_pos[ent1]
        pos2 = entity_pos[ent2]
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        if abs(dx) > abs(dy):
            # horizontal connection
            if dx > 0:
                exitX, exitY, entryX, entryY = 1, 0.5, 0, 0.5
            else:
                exitX, exitY, entryX, entryY = 0, 0.5, 1, 0.5
        else:
            # vertical connection
            if dy > 0:
                exitX, exitY, entryX, entryY = 0.5, 1, 0.5, 0
            else:
                exitX, exitY, entryX, entryY = 0.5, 0, 0.5, 1
        xml += f'''
        <mxCell id="rel{cell_id}" value="{label}" style="edgeStyle=curvedEdgeStyle;rounded=0;orthogonalLoop=0;jettySize=auto;html=1;routing=1;startArrow={start_arrow};startFill=0;endArrow={end_arrow};endFill=0;exitX={exitX};exitY={exitY};entryX={entryX};entryY={entryY};" edge="1" parent="1" source="{ent1}" target="{ent2}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>'''
        cell_id += 1

    xml += '''
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
    return xml

def main():
    parser = argparse.ArgumentParser(description='Convert Mermaid ER diagram to Draw.io XML')
    parser.add_argument('input', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='Input Mermaid file (default: stdin)')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=sys.stdout, help='Output XML file (default: stdout)')
    args = parser.parse_args()

    mermaid_code = args.input.read()
    entities, relationships = parse_mermaid(mermaid_code)
    xml = generate_drawio_xml(entities, relationships)
    args.output.write(xml)

if __name__ == '__main__':
    main()
