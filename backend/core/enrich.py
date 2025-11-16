import re

IOC_IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
IOC_DOMAIN = re.compile(r"\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
IOC_URL = re.compile(r"https?://[^\s]+" )

def extract_iocs(text):
    ips = IOC_IP.findall(text or "")
    doms = [d for d in IOC_DOMAIN.findall(text or "") if not d.replace('.', '').isdigit()]
    urls = IOC_URL.findall(text or "")
    return {"ips": list(set(ips)), "domains": list(set(doms)), "urls": list(set(urls))}
