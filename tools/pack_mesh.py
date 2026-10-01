"""Compact evaluated triangles into indexed binary arrays for the offline viewer."""
import base64
import struct


def pack_meshes(payload):
    for mesh in payload['meshes']:
        if isinstance(mesh['positions'], str):
            continue
        unique, positions, normals, indices = {}, [], [], []
        for i in range(0, len(mesh['positions']), 3):
            p = tuple(mesh['positions'][i:i+3])
            n = tuple(mesh['normals'][i:i+3])
            key = p + n
            if key not in unique:
                unique[key] = len(positions) // 3
                positions.extend(p)
                normals.extend(round(v * 32767) for v in n)
            indices.append(unique[key])
        for name, values, fmt in [('positions', positions, 'f'),
                                  ('normals', normals, 'h'), ('indices', indices, 'I')]:
            mesh[name] = base64.b64encode(struct.pack(f'<{len(values)}{fmt}', *values)).decode('ascii')
    payload['encoding'] = 'indexed-base64-le'
    return payload
