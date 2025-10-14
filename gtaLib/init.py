def parse_ipl(path):
    """Very small parser stub for IPL/IDE text files.
    Returns a list of dict entries with model name and coordinates if the file exists.
    """
    entries = []
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                # Very naive: expect lines like "model x y z"
                if len(parts) >= 4:
                    try:
                        name = parts[0]
                        x = float(parts[1]); y = float(parts[2]); z = float(parts[3])
                        entries.append({'name': name, 'x': x, 'y': y, 'z': z})
                    except Exception:
                        continue
    except Exception:
        pass
    return entries

def load_dff(path):
    # Placeholder: return None or raise if not implemented
    raise NotImplementedError('DFF loading not implemented in gtaLib stub')

def load_txd(path):
    raise NotImplementedError('TXD loading not implemented in gtaLib stub')
