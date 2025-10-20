import os
import json
import time

class SuricataClient:
    """
    Tails Suricata eve.json and yields parsed JSON events.

    Behavior:
      - Resolves path from eve_path arg, SURICATA_EVE_PATH env, or common defaults.
      - Emits a small backlog (last `backlog_lines`) on start.
      - Supports newline-delimited JSON objects OR a single JSON array in the file.
      - Handles file rotation/truncation by reopening when size shrinks.
      - Buffers multiline JSON objects until a full JSON object can be parsed.

    Usage:
      c = SuricataClient(eve_path=r"C:\Program Files\Suricata\log\eve.json")
      for evt in c.stream():
          handle(evt)
    """
    def __init__(self, suricata_url=None, eve_path=None, poll_interval=0.2, backlog_lines=200):
        self.poll_interval = poll_interval
        self.backlog_lines = backlog_lines
        env_path = os.environ.get("SURICATA_EVE_PATH")
        # allow suricata_url like file://C:/path/eve.json
        file_from_url = None
        if isinstance(suricata_url, str) and suricata_url.startswith("file://"):
            file_from_url = suricata_url[7:]
        self.eve_path = (
            eve_path
            or file_from_url
            or env_path
            or "/var/log/suricata/eve.json"
        )

        # Windows common install locations fallback (explicitly include Program Files and ProgramData)
        if os.name == "nt" and (not self.eve_path or not os.path.exists(self.eve_path)):
            possible = [
                r"C:\Program Files\Suricata\log\eve.json",
                r"C:\ProgramData\Suricata\log\eve.json",
                r"C:\Suricata\log\eve.json",
            ]
            for p in possible:
                if os.path.exists(p):
                    self.eve_path = p
                    break

    def _read_backlog(self, path):
        """Return a list of JSON-parsed events from the end of file (up to backlog_lines)."""
        try:
            with open(path, "rb") as fh:
                # read last N bytes heuristic to get recent lines
                fh.seek(0, os.SEEK_END)
                size = fh.tell()
                read_bytes = 65536
                if size < read_bytes:
                    fh.seek(0)
                    data = fh.read().decode('utf-8', errors='ignore')
                else:
                    fh.seek(max(0, size - read_bytes))
                    data = fh.read().decode('utf-8', errors='ignore')
        except Exception:
            return []

        data = data.strip()
        if not data:
            return []

        # If file is a JSON array, parse entire file
        if data.lstrip().startswith('['):
            try:
                # try reading whole file as array
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    alltext = fh.read()
                arr = json.loads(alltext)
                if isinstance(arr, list):
                    # return only last backlog_lines items
                    return arr[-self.backlog_lines:]
            except Exception:
                # fall through to newline-delimited parsing
                pass

        # newline-delimited JSON: take last backlog_lines lines and parse
        lines = data.splitlines()
        # if we read only tail bytes, ensure we get full last lines: keep last backlog_lines
        lines = lines[-self.backlog_lines:]
        events = []
        buffer = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # try parse line directly
            try:
                evt = json.loads(line)
                events.append(evt)
                buffer = ""
                continue
            except Exception:
                # accumulate into buffer for possible multiline JSON objects
                buffer += line + "\n"
                try:
                    evt = json.loads(buffer)
                    events.append(evt)
                    buffer = ""
                except Exception:
                    # still incomplete; continue
                    continue
        return events

    def stream(self):
        """Generator that yields dict events as lines are appended to eve.json."""
        path = self.eve_path
        # wait for file to appear
        while not path or not os.path.exists(path):
            time.sleep(1)
            # re-check env in case it's set after start
            env_path = os.environ.get("SURICATA_EVE_PATH")
            if env_path:
                path = env_path
                self.eve_path = env_path
            # continue waiting until file exists

        # yield backlog first
        for evt in self._read_backlog(path):
            yield evt

        # now tail the file for new entries
        fh = None
        last_size = 0
        buffer = ""
        try:
            fh = open(path, "r", encoding="utf-8", errors="ignore")
            fh.seek(0, os.SEEK_END)
            last_size = os.path.getsize(path)
        except Exception:
            # try later in loop
            fh = None

        while True:
            try:
                if fh is None:
                    try:
                        fh = open(path, "r", encoding="utf-8", errors="ignore")
                        fh.seek(0, os.SEEK_END)
                        last_size = os.path.getsize(path)
                    except Exception:
                        time.sleep(self.poll_interval)
                        continue

                line = fh.readline()
                if not line:
                    # check for rotation/truncation
                    try:
                        current_size = os.path.getsize(path)
                        if current_size < last_size:
                            # file rotated/truncated: reopen and treat as new file
                            try:
                                fh.close()
                            except Exception:
                                pass
                            fh = open(path, "r", encoding="utf-8", errors="ignore")
                            last_size = os.path.getsize(path)
                            buffer = ""
                            # optionally yield backlog of new file
                            for evt in self._read_backlog(path):
                                yield evt
                            continue
                        last_size = current_size
                    except Exception:
                        pass
                    time.sleep(self.poll_interval)
                    continue

                line = line.rstrip("\n")
                if not line.strip():
                    continue

                # try direct parse
                try:
                    evt = json.loads(line)
                    # if we have buffered incomplete chunk, try to prepend and parse whole
                    if buffer:
                        try:
                            # combine buffer + line and attempt parse
                            combined = buffer + "\n" + line
                            evt2 = json.loads(combined)
                            yield evt2
                            buffer = ""
                            continue
                        except Exception:
                            # cannot parse combined; clear buffer (avoid infinite growth)
                            buffer = ""
                    yield evt
                    continue
                except Exception:
                    # accumulate and attempt to parse buffer
                    buffer += line + "\n"
                    try:
                        evt = json.loads(buffer)
                        yield evt
                        buffer = ""
                    except Exception:
                        # still incomplete; continue reading
                        # to avoid unbounded buffer, if buffer grows huge, reset
                        if len(buffer) > 1_000_000:
                            buffer = ""
                        continue

            except GeneratorExit:
                break
            except Exception:
                # on unexpected error, close file and retry after a pause
                try:
                    if fh:
                        fh.close()
                except Exception:
                    pass
                fh = None
                buffer = ""
                time.sleep(1)