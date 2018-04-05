import os
import os.path
import sys
import datetime
import webbrowser
import argparse
import time
import traceback

class CommandArgs:
    def __init__ (self):
        self.argParser = argparse.ArgumentParser ()
    
        self.argParser.add_argument ('-f', '--fcall', help = 'test fast calls', action = 'store_true')
        self.argParser.add_argument ('-i', '--inst', help = 'installed version rather than new one', action = 'store_true')
        self.argParser.add_argument ('-b', '--blind', help = 'don\'t start browser', action = 'store_true')
        
        self.__dict__.update (self.argParser.parse_args () .__dict__)

commandArgs = CommandArgs ()
        
transpileCommand = 'transcrypt' if commandArgs.inst else 'run_transcrypt'
                
shipDir = os.path.dirname (os.path.abspath (__file__)) .replace ('\\', '/')
appRootDir = '/'.join  (shipDir.split ('/')[ : -2])

def getAbsPath (relPath):
    return '{}/{}'.format (appRootDir, relPath)

def test (relProgramPrepath, run, switches, outputPrename = '', nodeJs = False):
    # Compute some slugs
    programPrepath = getAbsPath (relProgramPrepath)
    relOutputDir = f'{"/".join (relProgramPrepath.split ("/") [:-1])}/__target__'
    outputDir = getAbsPath (relOutputDir)
    relOutputPrepath = f'{relOutputDir}/{outputPrename}'
    outputPrepath = getAbsPath (relOutputPrepath)
    
    # If there are relevant console messages of the compilation process,
    # like with the static typechecking tests, write them into a file that can be served for a visual check
    if not os.path.exists (outputDir):
        os.makedirs (outputDir) # Transcrypt will make outputDir too late, so it has to happen here
    redirect = f' > {outputPrepath}.out' if outputPrename else ''
    
    # Compile with Transcrypt
    os.system (f'{transpileCommand} -b -m -da -sf -n -de {switches}{programPrepath}{redirect}')
    
    # Run back to back in CPython
    if run:
        os.system (f'{transpileCommand} -sf -r {switches}{programPrepath}') 
    
    openNewTab = 2
    if not commandArgs.blind:
        if nodeJs:
            '''
            os.system ('start cmd /k node __target__/{}.js'.format (filePrename))
            time.sleep (5)
            webbrowser.open ('http://localhost:8080', new = openNewTab)
            '''           
        else:
            webbrowser.open (f'http://localhost:8080/{relProgramPrepath}.html', new = openNewTab)
        
# Start a node http server in the Transcryp/transcrypt directory
if not commandArgs.blind:
    os.system (f'start cmd /k http-server {appRootDir} -c-1')   # -c-1 means 'Clear cache'

# Allow visual check of command line options
os.system (f'{transpileCommand} -h')

# Perform all tests
for switches in (('', '-f ') if commandArgs.fcall else ('',)):
    # test ('demos/nodejs_demo', 'nodejs_demo', False, True, switches + '-p .none ')
    # test ('demos/terminal_demo', 'terminal_demo', False, switches)
    
    test ('development/automated_tests/hello/autotest', True, switches)
    test ('development/automated_tests/transcrypt/autotest', True, switches + '-c ')  
    test ('development/automated_tests/time/autotest', True, switches)    
    test ('development/automated_tests/re/autotest', True, switches)    
    
    test ('development/manual_tests/module_random/module_random', False, switches)
    test ('development/manual_tests/transcrypt_only/transcrypt_only', False, switches)
    test ('development/manual_tests/transcrypt_and_python_results_differ/results', False, switches)
    test ('development/manual_tests/static_types/static_types', False, switches + '-ds -dc ', 'static_types')
    test ('development/manual_tests/async_await/test', False, switches)
    
    test ('tutorials/baseline/bl_010_hello_world/hello_world', False, switches)
    test ('tutorials/baseline/bl_020_assign/assign', False, switches)
    test ('tutorials/baseline/bl_030_if_else_prompt/if_else_prompt', False, switches)
    test ('tutorials/baseline/bl_035_if_else_event/if_else_event', False, switches)
    test ('tutorials/baseline/bl_040_for_simple/for_simple', False, switches)
    test ('tutorials/baseline/bl_042_for_nested/for_nested', False, switches)
    test ('tutorials/baseline/bl_045_while_simple/while_simple', False, switches)
    
    test ('demos/hello/hello', False, switches)
    test ('demos/jquery_demo/jquery_demo', False, switches)
    test ('demos/d3js_demo/d3js_demo', False, switches)
    test ('demos/ios_app/ios_app', False, switches)
    test ('demos/react_demo/react_demo', False, switches)
    test ('demos/riot_demo/riot_demo', False, switches)
    test ('demos/plotly_demo/plotly_demo', False, switches)
    test ('demos/three_demo/three_demo', False, switches)
    test ('demos/pong/pong', False, switches)
    test ('demos/pysteroids_demo/pysteroids', False, switches)
    
    test ('demos/turtle_demos/star', False, switches)
    test ('demos/turtle_demos/snowflake', False, switches)
    test ('demos/turtle_demos/mondrian', False, switches)
    test ('demos/turtle_demos/mandala', False, switches)    
          
    test ('demos/cyclejs_demo/cyclejs_demo', False, switches)
    test ('demos/cyclejs_demo/cyclejs_http_demo', False, switches)
    test ('demos/cyclejs_demo/component_demos/isolated_bmi_slider/bmi', False, switches)
    test ('demos/cyclejs_demo/component_demos/labeled_slider/labeled_slider', False, switches)
   
'''
# Make docs, the resulting files are untracked
origDir = os.getcwd ()
sphinxDir = '/'.join ([appRootDir, 'docs/sphinx'])
os.chdir (sphinxDir)
os.system ('touch *.rst')
os.system ('make html')
os.chdir (origDir)
'''
        
print ('\nShipment test ready')
