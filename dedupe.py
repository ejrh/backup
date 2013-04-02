import sys
import os
import hashlib

import journalcmd


BUFFER_SIZE = 65536

class Deduper(object):
    def __init__(self):
        self.frn_map = {}
        self.md5_map = {}
        self.manifest = {}

    def get_file_frn(self, path):
        tups, name = journalcmd.read_file_usn(path)
        return tups[3]
    
    def get_file_md5(self, path):
        path = os.path.normpath(path)
        
        if path in self.manifest:
            return self.manifest[path]
        
        f = open(path, 'rb')
        m = hashlib.md5()
        while True:
            buf = f.read(BUFFER_SIZE)
            if len(buf) == 0:
                break
            m.update(buf)
        f.close()
        
        md5 = m.hexdigest()
        
        self.manifest[path] = md5
        print '%s *%s' % (md5, path)
        return md5

    def dedupe_file(self, path):
        frn = self.get_file_frn(path)
        if frn in self.frn_map:
            self.frn_map[frn].append(path)
            return
        
        md5 = self.get_file_md5(path)
        if md5 not in self.md5_map:
            self.md5_map[md5] = path
            self.frn_map[frn] = [path]
            return
        
        from_path = self.md5_map[md5]
        print 'Can dedupe: %s (from %s)' % (path, from_path)
        self.md5_map[md5] = path
        self.frn_map[frn] = [path]

    def dedupe_dir(self, dirpath):
        for fn in os.listdir(dirpath):
            subpath = os.path.join(dirpath, fn)
            if os.path.isdir(subpath):
                self.dedupe_dir(subpath)
            else:
                self.dedupe_file(subpath)
    
    def load_manifest(self, filename):
        f = open(filename, 'rt')
        for line in f:
            md5, path = line.strip().split(' *', 1)
            path = os.path.normpath(path)
            self.manifest[path] = md5
        f.close()
        
    def run(self, target):
        self.dedupe_dir(target)

def main():
    target = sys.argv[1]
    d = Deduper()
    d.load_manifest(sys.argv[2])
    d.run(target)

if __name__ == '__main__':
    main()
