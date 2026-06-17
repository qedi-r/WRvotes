#!/usr/bin/env python3

import requests
import tempfile
import filecmp
import sys
import time
import datetime
import argparse, sys, os
import yaml
from git import Repo
from google.oauth2 import service_account
import googleapiclient.discovery
import csv_lint

""" Grab data files from Google docs
    Paul "Worthless" Nijjar, 2019-09-22
"""

TMPDIR=tempfile.TemporaryDirectory()
DEBUG_DEFAULT_LEVEL = 2


# ------ PARSE ARGS -------
def parse_args():
    parser = argparse.ArgumentParser(
      description = "Pull WaterlooRegionVotes files from the INTERNET and"
          " convert to csv files"
      )

    parser.add_argument("--configfile",
      help = "Where to find the config YAML",
      required = True,
      )
    parser.add_argument("--debuglevel",
      help = "How verbose to be. Higher is more verbose.",
      type = int,
      default = 2,
      )
    parser.add_argument("--no-download",
      help = "Do not download CSVs from Google Docs",
      action = "store_true",
      )
    parser.add_argument("--no-lint",
      help = "Do not check CSV files for errors",
      action = "store_true",
      )
    parser.add_argument("--no-commit",
      help = "Do not check files into git and push them",
      action = "store_true",
      )
    return parser.parse_args()

# ---------------------------------
def load_config(args):
    # From:
    # https://dev.to/jmarhee/using-pyyaml-to-support-yaml-and-json-configuration-files-in-your-cli-tools-1694

    with open(args.configfile, "r") as c:
        cfg = yaml.safe_load(c)

        # I want the flags to be in config[]
        cfg.update(vars(args))
        return cfg


# ------------------------------
def auth_to_google():
    # From: https://developers.google.com/api-client-library/python/auth/service-accounts
    SCOPES=['https://www.googleapis.com/auth/calendar']

    credentials = service_account.Credentials.from_service_account_file(
        config['service_credentials'],
        scopes=[],
        )

    cal_object = googleapiclient.http.build_http()
    return cal_object


# ------------------------------------
def setup_debug_log():
    # Better hope this is not an error!
    dbg = config['debug']

    if dbg['log']['enable']:
        global DEBUG_FILEHANDLE
        target = dbg['log']['logfile']
        DEBUG_FILEHANDLE = open(target, 'a', newline='') 
        # What if this fails?
        if not DEBUG_FILEHANDLE:
            print("Unable to write to {}".format(target))
            sys.exit(1)

    if 'level' in dbg['default']:
        DEBUG_DEFAULT_LEVEL = dbg['default']['level']


# ------------------------------------
def debug(msg,level=DEBUG_DEFAULT_LEVEL):
    """ Add debug information to screen and or file. """

    if config['debug']['screen']['enable'] and \
      level <= config['debug']['screen']['threshold']:
        print(msg)

    if config['debug']['log']['enable'] and \
      level <= config['debug']['log']['threshold']:
        DEBUG_FILEHANDLE.write("{}: ".format(
          datetime.datetime.now())
          )
        DEBUG_FILEHANDLE.write(msg)
        DEBUG_FILEHANDLE.write('\n')

# ------------------------------------
def download_csvs():
    creds = auth_to_google()

    debug("---- Beginning run ----",1)

    changed_files = []

    sources = config['sources']

    for syncfile in sources:
        if 'remotesrc' in sources[syncfile]:
            debug("file: {}, target: {}".format(
                    syncfile,
                    sources[syncfile]['remotesrc'],
                    ),
                    3)
            r = requests.get(sources[syncfile]['remotesrc'])
             
            # Check that we actually got the file. Otherwise 
            # just continue.

            # https://stackabuse.com/download-files-with-python/
            if r.status_code == 200:

                candidate="{}/{}.csv".format(TMPDIR.name,syncfile)

                # There is a problem here. Google sheets add ^M to the end as
                # newlines. 
                with open(candidate, 'wb') as f:
                    f.write(r.content)
                    f.close()

                origfile=os.path.join(
                  config['gitdir'],
                  config['targetdir'],
                  sources[syncfile]['folder'],
                  "{}.csv".format(syncfile),
                  )

                if not filecmp.cmp(candidate, origfile):
                    debug("Found different files: "
                          "{}. Overwriting.".format(syncfile),
                         2)
                    changed_files.append(syncfile)

                    with open(origfile, 'wb') as f_orig:
                        f_orig.write(r.content)
                        f_orig.close()
                else:
                    debug("{}: files are the same".format(syncfile),2)

            else:
                debug("Oops. Received status "
                      "{} when downloading {} "
                       "from {} .".format(
                          r.status_code,
                          syncfile,
                          sources[syncfile]
                          ),
                     0,
                     )

    if changed_files:
        if config['no_commit']:
            debug("--no-commit specified, so not committing.", 2)
        else: 
            try: 
                ssh_cmd = "ssh -i {}".format(config['github_ssh_key'])
                repo = Repo(config['gitdir'])
                with repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):

                    origin = repo.remote('origin')
                    origin.pull()


                    commit_msg = "Auto-commit: updated "
                    commit_msg += "{} from Google Docs".format( 
                                     ", ".join(changed_files))

                    debug(commit_msg, 1)

                    changed_with_path = map(
                      lambda x: "{}/{}".format(config['targetdir'], x),
                      changed_files)

                    repo.index.add(changed_with_path)
                    repo.index.commit(commit_msg)
                    origin.push()
            except Exception as e: 
                debug("Git exception:\n{}".format(e), 0)
                raise
    else:
        debug("All files are the same. Not committing.", 2)

    debug("---- Completed run ----",1)


# ------------------------------------
def cleanup():
    """ Clean up file handles. """
    if DEBUG_FILEHANDLE:
        DEBUG_FILEHANDLE.close()

# --- END FUNCTIONS ---

args = parse_args()
global config
config = load_config(args)
setup_debug_log()

if not config['no_download']:
    download_csvs()

# The CSV checker does its own debug script. Ugh I should
# just use the logging module instead of this.
cleanup()

if not config['no_lint']:
    csv_lint.run_linter(config)


