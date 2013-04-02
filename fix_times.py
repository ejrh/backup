import sys
import os
import os.path

target_dir = sys.argv[1]
source_dir = sys.argv[2]
fixed = 0
for dirpath, dirnames, filenames in os.walk(target_dir):
    for f in filenames:
        try:
            target_path = os.path.join(dirpath, f)
            source_path = target_path.replace(target_dir, source_dir)
            source_time = os.path.getmtime(source_path)
            target_time = os.path.getmtime(target_path)
            if (source_time - target_time < -1) or (source_time - target_time > 1):
                print >>sys.stderr, 'Changing mtime on %s from %s to %s' % (target_path, target_time, source_time)
                atime = os.path.getatime(target_path)
                os.utime(target_path, (atime, source_time))
                fixed += 1
        except WindowsError, ex:
            print >>sys.stderr, ex
            pass

print >>sys.stderr, 'Fixed %d file mtimes' % fixed
