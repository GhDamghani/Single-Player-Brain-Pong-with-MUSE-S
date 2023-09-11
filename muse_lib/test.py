from pylsl import resolve_byprop
from constants import LSL_SCAN_TIMEOUT

streams = resolve_byprop('type', 'EEG', timeout=LSL_SCAN_TIMEOUT)
stream = streams[0]
print(dir(stream))
print(stream.source_id())
print(stream.as_xml())
print(stream.name())

print('00:55:da:b9:3f:d0' in stream.name())