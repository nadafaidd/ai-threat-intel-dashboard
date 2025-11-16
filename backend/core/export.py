from datetime import datetime

def to_markdown(top5_entries):
    lines = [f"# Daily Threat Brief — {datetime.utcnow().strftime('%Y-%m-%d')}\n"]
    for i, e in enumerate(top5_entries, 1):
        lines.append(f"## {i}. {e['title']}\n")
        lines.append(e['summary'] + "\n")
        lines.append(f"**Risk:** {e['risk']}  ")
        if e.get('products'): lines.append(f"**Products:** {', '.join(e['products'])}  ")
        if e.get('cves'): lines.append(f"**CVEs:** {', '.join(e['cves'])}  ")
        if e.get('actions'):
            lines.append("**Immediate actions:**")
            for a in e['actions']:
                lines.append(f"- {a}")
        lines.append("\n")
    return "\n".join(lines)
