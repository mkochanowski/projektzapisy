import os

def processFile(filepath):
    f = open(filepath, "r+")
    lines = f.readlines()
    lastImportLineIndex = 0
    while lastImportLineIndex < len(lines):
        for i in range(lastImportLineIndex, len(lines)):
            if "import " in lines[i]:
                lastImportLineIndex += 1
                break
        else:
            break
    print("File %s: last import line is %d" % (filepath, lastImportLineIndex))
    
    newLines = []
    
    for line in lines:
        sline = line.strip()
        if sline.startswith("url("):
            chunks = line.strip(",")
            if len(chunks) < 2 or 'name=' in chunks[1] or 'include(' in chunks[1]:
                print("Warning: skipping line \"%s\" in file %s" % (sline, filepath))
                continue
            viewName = chunks[1].strip()
            if viewName.endswith("),"):
                viewName = viewName[:-2]
            # strip quotes
            viewName = viewName.replace("'", "").replace("\"", "")
            newLine = chunks[0] + ', ' + 'views.' + viewName + ', '
            if len(chunks) > 2:
                newLine += ", ".join(chunks[2:])
            else:
                newLine += "),\n"
        else:
            newLines.append(line)
    
    newLines.insert(lastImportLineIndex + 1, "from . import views\n")
    f.seek(0, 0)
    f.writelines(newLines)
    f.close()

i = 0
for root, subdir, files in os.walk("."):
    if "urls.py" in files:
        fpath = os.path.join(root, "urls.py")
        print("Fixing %s" % fpath)
        processFile(fpath)
        i += 1

print("%d files processed" % i)
