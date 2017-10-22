from pipeline.conf import settings
from pipeline.compilers import SubProcessCompiler, CompilerError
import hashlib
import os
import subprocess
import re

class TypeScriptCompiler(SubProcessCompiler):
    output_extension = 'js'

    def match_file(self, path):
        return path.endswith('.ts')

    def compile_file(self, content, path):
        # tsc will not read input from stdin, so we need a fake file...
        content_hash = hashlib.md5(content).hexdigest()
        ifpath = "/tmp/%s.in.ts" % content_hash
        f = open(ifpath, "w")
        f.write(content)
        f.close()
        # tsc errors are written to stdout, "by design"...
        # https://github.com/Microsoft/TypeScript/issues/615
        # so output needs a file as well
        ofpath = "/tmp/%s.out.ts" % content_hash
        command = "%s %s %s --outFile %s" % (
            settings.PIPELINE_TYPESCRIPT_BINARY,
            settings.PIPELINE_TYPESCRIPT_ARGUMENTS,
            ifpath,
            ofpath
        )
        print command
        self.run_typescript_compiler(command, ifpath, path)
        os.remove(ifpath)
        f = open(ofpath, "r")
        result = f.read()
        f.close()
        os.remove(ofpath)
        return result

    def run_typescript_compiler(self, command, ifpath, realFilePath):
        pipe = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    
        # Errors are reported on stdout
        tsc_output = pipe.stdout.read()

        if pipe.wait() != 0:
            # Replace the tempname in errors with the real path
            rgx = ".+%s" % ifpath
            cleaned_errors = re.sub(rgx, realFilePath, tsc_output)
            raise CompilerError("TypeScript compiler returned errors:\n%s" % cleaned_errors)