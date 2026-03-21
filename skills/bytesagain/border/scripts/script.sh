#!/usr/bin/env bash
set -euo pipefail

# border — CSS Border Style Generator
# Version: 1.0.0
# Powered by BytesAgain | bytesagain.com | hello@bytesagain.com

DATA_DIR="${HOME}/.border"
DATA_FILE="${DATA_DIR}/data.jsonl"
CONFIG_FILE="${DATA_DIR}/config.json"
EXPORT_DIR="${DATA_DIR}/exports"

mkdir -p "${DATA_DIR}" "${EXPORT_DIR}"
touch "${DATA_FILE}"

if [ ! -f "${CONFIG_FILE}" ]; then
  echo '{"default_width": 1, "default_style": "solid", "default_color": "#333333", "default_selector": ".element"}' > "${CONFIG_FILE}"
fi

COMMAND="${1:-help}"

case "${COMMAND}" in

  create)
    python3 << 'PYEOF'
import os, sys, json, uuid, datetime

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.border/data.jsonl"))
width = os.environ.get("BORDER_WIDTH", "1")
style = os.environ.get("BORDER_STYLE", "solid")
color = os.environ.get("BORDER_COLOR", "#333333")
radius = os.environ.get("BORDER_RADIUS", "0")
selector = os.environ.get("BORDER_SELECTOR", ".element")

ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
short_id = uuid.uuid4().hex[:8]
border_id = f"border_{ts}_{short_id}"

properties = {
    "border": f"{width}px {style} {color}"
}

if radius and radius != "0":
    if radius.isdigit():
        radius = f"{radius}px"
    properties["border-radius"] = radius

css_props = ";\n  ".join(f"{k}: {v}" for k, v in properties.items())
css = f"{selector} {{\n  {css_props};\n}}"

record = {
    "id": border_id,
    "command": "create",
    "selector": selector,
    "properties": properties,
    "css": css,
    "params": {"width": width, "style": style, "color": color, "radius": radius},
    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
}

with open(data_file, "a") as f:
    f.write(json.dumps(record) + "\n")

print(json.dumps({"status": "success", "command": "create", "data": record}, indent=2))
PYEOF
    ;;

  radius)
    python3 << 'PYEOF'
import os, sys, json, uuid, datetime

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.border/data.jsonl"))
radius = os.environ.get("BORDER_RADIUS", "8px")
selector = os.environ.get("BORDER_SELECTOR", ".element")

ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
short_id = uuid.uuid4().hex[:8]
border_id = f"radius_{ts}_{short_id}"

# Support shorthand: single value or space-separated for each corner
if radius.isdigit():
    radius = f"{radius}px"

properties = {"border-radius": radius}

# Generate webkit prefix too
prefixed_props = {
    "-webkit-border-radius": radius,
    "-moz-border-radius": radius,
    "border-radius": radius
}

css_props = ";\n  ".join(f"{k}: {v}" for k, v in prefixed_props.items())
css = f"{selector} {{\n  {css_props};\n}}"

record = {
    "id": border_id,
    "command": "radius",
    "selector": selector,
    "properties": prefixed_props,
    "css": css,
    "params": {"radius": radius},
    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
}

with open(data_file, "a") as f:
    f.write(json.dumps(record) + "\n")

print(json.dumps({"status": "success", "command": "radius", "data": record}, indent=2))
PYEOF
    ;;

  shadow)
    python3 << 'PYEOF'
import os, sys, json, uuid, datetime

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.border/data.jsonl"))
shadow = os.environ.get("BORDER_SHADOW", "2,4,10,0,rgba(0,0,0,0.2)")
selector = os.environ.get("BORDER_SELECTOR", ".element")

ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
short_id = uuid.uuid4().hex[:8]
border_id = f"shadow_{ts}_{short_id}"

# Parse shadow: offsetX, offsetY, blur, spread, color
parts = shadow.split(",", 4)
if len(parts) >= 5:
    ox, oy, blur_val, spread, color = parts[0], parts[1], parts[2], parts[3], parts[4]
elif len(parts) >= 4:
    ox, oy, blur_val, spread = parts[0], parts[1], parts[2], parts[3]
    color = "rgba(0,0,0,0.2)"
else:
    ox, oy, blur_val = parts[0] if len(parts) > 0 else "2", parts[1] if len(parts) > 1 else "4", parts[2] if len(parts) > 2 else "10"
    spread, color = "0", "rgba(0,0,0,0.2)"

shadow_value = f"{ox}px {oy}px {blur_val}px {spread}px {color}"

properties = {
    "-webkit-box-shadow": shadow_value,
    "-moz-box-shadow": shadow_value,
    "box-shadow": shadow_value
}

css_props = ";\n  ".join(f"{k}: {v}" for k, v in properties.items())
css = f"{selector} {{\n  {css_props};\n}}"

record = {
    "id": border_id,
    "command": "shadow",
    "selector": selector,
    "properties": properties,
    "css": css,
    "params": {"offsetX": ox, "offsetY": oy, "blur": blur_val, "spread": spread, "color": color},
    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
}

with open(data_file, "a") as f:
    f.write(json.dumps(record) + "\n")

print(json.dumps({"status": "success", "command": "shadow", "data": record}, indent=2))
PYEOF
    ;;

  outline)
    python3 << 'PYEOF'
import os, sys, json, uuid, datetime

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.border/data.jsonl"))
outline = os.environ.get("BORDER_OUTLINE", "2,solid,#0066ff,4")
selector = os.environ.get("BORDER_SELECTOR", ".element")

ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
short_id = uuid.uuid4().hex[:8]
border_id = f"outline_{ts}_{short_id}"

parts = outline.split(",")
width = parts[0] if len(parts) > 0 else "2"
style = parts[1] if len(parts) > 1 else "solid"
color = parts[2] if len(parts) > 2 else "#0066ff"
offset = parts[3] if len(parts) > 3 else "0"

properties = {
    "outline": f"{width}px {style} {color}",
    "outline-offset": f"{offset}px"
}

css_props = ";\n  ".join(f"{k}: {v}" for k, v in properties.items())
css = f"{selector} {{\n  {css_props};\n}}"

record = {
    "id": border_id,
    "command": "outline",
    "selector": selector,
    "properties": properties,
    "css": css,
    "params": {"width": width, "style": style, "color": color, "offset": offset},
    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
}

with open(data_file, "a") as f:
    f.write(json.dumps(record) + "\n")

print(json.dumps({"status": "success", "command": "outline", "data": record}, indent=2))
PYEOF
    ;;

  animate)
    python3 << 'PYEOF'
import os, sys, json, uuid, datetime

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.border/data.jsonl"))
animation = os.environ.get("BORDER_ANIMATION", "pulse")
color = os.environ.get("BORDER_COLOR", "#333333")
duration = os.environ.get("BORDER_DURATION", "2")
selector = os.environ.get("BORDER_SELECTOR", ".element")

ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
short_id = uuid.uuid4().hex[:8]
border_id = f"animate_{ts}_{short_id}"
anim_name = f"border_{animation}_{short_id}"

if animation == "pulse":
    keyframes = f"""@keyframes {anim_name} {{
  0% {{ border-color: {color}; }}
  50% {{ border-color: transparent; }}
  100% {{ border-color: {color}; }}
}}"""
    css = f"""{keyframes}

{selector} {{
  border: 2px solid {color};
  animation: {anim_name} {duration}s ease-in-out infinite;
}}"""

elif animation == "glow":
    keyframes = f"""@keyframes {anim_name} {{
  0% {{ box-shadow: 0 0 5px {color}; }}
  50% {{ box-shadow: 0 0 20px {color}, 0 0 40px {color}; }}
  100% {{ box-shadow: 0 0 5px {color}; }}
}}"""
    css = f"""{keyframes}

{selector} {{
  border: 2px solid {color};
  animation: {anim_name} {duration}s ease-in-out infinite;
}}"""

elif animation == "rotate":
    keyframes = f"""@keyframes {anim_name} {{
  0% {{ border-image: linear-gradient(0deg, {color}, transparent) 1; }}
  25% {{ border-image: linear-gradient(90deg, {color}, transparent) 1; }}
  50% {{ border-image: linear-gradient(180deg, {color}, transparent) 1; }}
  75% {{ border-image: linear-gradient(270deg, {color}, transparent) 1; }}
  100% {{ border-image: linear-gradient(360deg, {color}, transparent) 1; }}
}}"""
    css = f"""{keyframes}

{selector} {{
  border: 3px solid;
  border-image: linear-gradient(0deg, {color}, transparent) 1;
  animation: {anim_name} {duration}s linear infinite;
}}"""

elif animation == "dash":
    keyframes = f"""@keyframes {anim_name} {{
  to {{ stroke-dashoffset: -1000; }}
}}"""
    css = f"""{keyframes}

{selector} {{
  border: 2px dashed {color};
  background: linear-gradient(90deg, {color} 50%, transparent 50%) repeat-x,
              linear-gradient(90deg, {color} 50%, transparent 50%) repeat-x,
              linear-gradient(0deg, {color} 50%, transparent 50%) repeat-y,
              linear-gradient(0deg, {color} 50%, transparent 50%) repeat-y;
  background-size: 15px 2px, 15px 2px, 2px 15px, 2px 15px;
  background-position: 0 0, 0 100%, 0 0, 100% 0;
  animation: {anim_name} {duration}s linear infinite;
}}"""
else:
    css = f"{selector} {{ border: 2px solid {color}; }}"
    keyframes = ""

record = {
    "id": border_id,
    "command": "animate",
    "selector": selector,
    "animation_type": animation,
    "duration": duration,
    "color": color,
    "css": css,
    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
}

with open(data_file, "a") as f:
    f.write(json.dumps(record) + "\n")

print(json.dumps({"status": "success", "command": "animate", "data": record}, indent=2))
PYEOF
    ;;

  preset)
    python3 << 'PYEOF'
import os, sys, json, uuid, datetime

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.border/data.jsonl"))
preset_name = os.environ.get("BORDER_PRESET", "card")
selector = os.environ.get("BORDER_SELECTOR", ".element")

ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
short_id = uuid.uuid4().hex[:8]
border_id = f"preset_{ts}_{short_id}"

presets = {
    "card": {
        "border": "1px solid #e0e0e0",
        "border-radius": "8px",
        "box-shadow": "0 2px 8px rgba(0,0,0,0.1)"
    },
    "pill": {
        "border": "2px solid #333",
        "border-radius": "9999px",
        "padding": "8px 24px"
    },
    "neon": {
        "border": "2px solid #00ff41",
        "border-radius": "4px",
        "box-shadow": "0 0 10px #00ff41, inset 0 0 10px rgba(0,255,65,0.1)"
    },
    "retro": {
        "border": "4px double #8B4513",
        "border-radius": "0",
        "outline": "2px solid #D2691E",
        "outline-offset": "4px"
    },
    "minimal": {
        "border": "none",
        "border-bottom": "2px solid #333",
        "border-radius": "0"
    },
    "glassmorphism": {
        "border": "1px solid rgba(255,255,255,0.18)",
        "border-radius": "16px",
        "background": "rgba(255,255,255,0.05)",
        "backdrop-filter": "blur(10px)",
        "-webkit-backdrop-filter": "blur(10px)",
        "box-shadow": "0 8px 32px rgba(0,0,0,0.37)"
    }
}

if preset_name not in presets:
    print(json.dumps({
        "status": "error",
        "message": f"Preset '{preset_name}' not found. Available: {', '.join(presets.keys())}"
    }), file=sys.stderr)
    sys.exit(3)

properties = presets[preset_name]
css_props = ";\n  ".join(f"{k}: {v}" for k, v in properties.items())
css = f"/* Preset: {preset_name} */\n{selector} {{\n  {css_props};\n}}"

record = {
    "id": border_id,
    "command": "preset",
    "preset": preset_name,
    "selector": selector,
    "properties": properties,
    "css": css,
    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
}

with open(data_file, "a") as f:
    f.write(json.dumps(record) + "\n")

print(json.dumps({"status": "success", "command": "preset", "data": record}, indent=2))
PYEOF
    ;;

  random)
    python3 << 'PYEOF'
import os, sys, json, uuid, datetime, random

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.border/data.jsonl"))
selector = os.environ.get("BORDER_SELECTOR", ".element")

ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
short_id = uuid.uuid4().hex[:8]
border_id = f"random_{ts}_{short_id}"

styles = ["solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"]
colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24", "#6c5ce7", "#a29bfe",
          "#fd79a8", "#00cec9", "#e17055", "#0984e3", "#d63031", "#00b894"]

width = random.randint(1, 5)
style = random.choice(styles)
color = random.choice(colors)
radius = random.choice([0, 4, 8, 12, 16, 20, 50, 9999])
shadow_blur = random.randint(0, 20)
shadow_color = random.choice(colors)

properties = {
    "border": f"{width}px {style} {color}",
    "border-radius": f"{radius}px"
}

if random.random() > 0.3:
    properties["box-shadow"] = f"0 {random.randint(1,8)}px {shadow_blur}px {shadow_color}40"

css_props = ";\n  ".join(f"{k}: {v}" for k, v in properties.items())
css = f"/* Random border style */\n{selector} {{\n  {css_props};\n}}"

record = {
    "id": border_id,
    "command": "random",
    "selector": selector,
    "properties": properties,
    "css": css,
    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
}

with open(data_file, "a") as f:
    f.write(json.dumps(record) + "\n")

print(json.dumps({"status": "success", "command": "random", "data": record}, indent=2))
PYEOF
    ;;

  export)
    python3 << 'PYEOF'
import os, sys, json, datetime

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.border/data.jsonl"))
export_dir = os.environ.get("EXPORT_DIR", os.path.expanduser("~/.border/exports"))
fmt = os.environ.get("BORDER_FORMAT", "css")

records = []
if os.path.exists(data_file):
    with open(data_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

os.makedirs(export_dir, exist_ok=True)
ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

if fmt == "css":
    export_file = os.path.join(export_dir, f"borders_{ts}.css")
    with open(export_file, "w") as f:
        f.write("/* Generated by border skill */\n\n")
        for r in records:
            css = r.get("css", "")
            if css:
                f.write(f"/* ID: {r.get('id','')} | Command: {r.get('command','')} */\n")
                f.write(css + "\n\n")
elif fmt == "scss":
    export_file = os.path.join(export_dir, f"borders_{ts}.scss")
    with open(export_file, "w") as f:
        f.write("// Generated by border skill\n\n")
        for i, r in enumerate(records):
            props = r.get("properties", {})
            mixin_name = f"border-{r.get('command','style')}-{i+1}"
            f.write(f"@mixin {mixin_name} {{\n")
            for k, v in props.items():
                f.write(f"  {k}: {v};\n")
            f.write("}\n\n")
else:
    export_file = os.path.join(export_dir, f"borders_{ts}.json")
    with open(export_file, "w") as f:
        json.dump(records, f, indent=2)

print(json.dumps({
    "status": "success",
    "command": "export",
    "data": {"format": fmt, "file": export_file, "count": len(records)}
}, indent=2))
PYEOF
    ;;

  preview)
    python3 << 'PYEOF'
import os, sys, json

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.border/data.jsonl"))
export_dir = os.environ.get("EXPORT_DIR", os.path.expanduser("~/.border/exports"))
border_id = os.environ.get("BORDER_ID", "")

target = None
records = []
if os.path.exists(data_file):
    with open(data_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            records.append(entry)
            if border_id and entry.get("id") == border_id:
                target = entry

if border_id and not target:
    print(json.dumps({"status": "error", "message": f"Style not found: {border_id}"}), file=sys.stderr)
    sys.exit(3)

if not target and records:
    target = records[-1]

if not target:
    print(json.dumps({"status": "error", "message": "No styles found"}), file=sys.stderr)
    sys.exit(1)

css = target.get("css", "")
html = f"""<!DOCTYPE html>
<html>
<head>
  <title>Border Preview - {target.get('id','')}</title>
  <style>
    body {{ font-family: system-ui; padding: 40px; background: #f5f5f5; display: flex; justify-content: center; align-items: center; min-height: 80vh; }}
    {css}
    .element {{ width: 300px; height: 200px; display: flex; align-items: center; justify-content: center; background: white; font-size: 14px; color: #666; }}
  </style>
</head>
<body>
  <div class="element">
    <p>Border Preview<br><small>{target.get('id','')}</small></p>
  </div>
</body>
</html>"""

os.makedirs(export_dir, exist_ok=True)
preview_file = os.path.join(export_dir, f"preview_{target.get('id','unknown')}.html")
with open(preview_file, "w") as f:
    f.write(html)

print(json.dumps({
    "status": "success",
    "command": "preview",
    "data": {"id": target.get("id"), "preview_file": preview_file, "css": css}
}, indent=2))
PYEOF
    ;;

  list)
    python3 << 'PYEOF'
import os, sys, json

data_file = os.environ.get("DATA_FILE", os.path.expanduser("~/.border/data.jsonl"))

records = []
if os.path.exists(data_file):
    with open(data_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

print(json.dumps({
    "status": "success",
    "command": "list",
    "data": {"count": len(records), "styles": records}
}, indent=2))
PYEOF
    ;;

  help)
    cat << 'HELPEOF'
border — CSS Border Style Generator v1.0.0

Usage: scripts/script.sh <command>

Commands:
  create    Generate custom border (BORDER_WIDTH, BORDER_STYLE, BORDER_COLOR)
  radius    Generate border-radius (BORDER_RADIUS)
  shadow    Generate box-shadow (BORDER_SHADOW=oX,oY,blur,spread,color)
  outline   Generate outline (BORDER_OUTLINE=width,style,color,offset)
  animate   Generate animated border (BORDER_ANIMATION, BORDER_DURATION)
  preset    Apply named preset (BORDER_PRESET: card|pill|neon|retro|minimal|glassmorphism)
  random    Generate random style for inspiration
  export    Export styles (BORDER_FORMAT: css|scss|json)
  preview   Generate HTML preview (BORDER_ID)
  list      List all generated styles
  help      Show this help message
  version   Show version

Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
HELPEOF
    ;;

  version)
    echo '{"name": "border", "version": "1.0.0", "author": "BytesAgain"}'
    ;;

  *)
    echo "Unknown command: ${COMMAND}" >&2
    echo "Run 'scripts/script.sh help' for usage." >&2
    exit 1
    ;;
esac
