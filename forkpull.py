#!/usr/bin/python3

__author__ = "Veda Vyas"
__github__ = "veda-vyas"

import os
import sys
from subprocess import call, check_output
import github3  
from git import Repo 
from giturlparse import parse 
from retrying import retry 
import requests

"""
   This script runs a bunch of boilerplate code to synchronise
   your locally cloned fork to its parent github repository.
"""
CLONE_REPO = ['git', 'clone']
CURRENT_REPO_ORIGIN = ['git', 'config', '--get', 'remote.origin.url']
CURRENT_REPO_UPSTREAM = ['git', 'config', '--get', 'remote.upstream.url']
ADD_REMOTE_CMD = ['git', 'remote', 'add', 'upstream']
CHECK_REMOTES_CMD = ['git', 'remote', '-v']
FETCH_UPSTREAM_CMD = ['git', 'fetch', 'upstream']
CHECKOUT_MASTER_CMD = ['git', 'checkout', 'master']
MERGE_UPSTREAM_CMD = ['git', 'merge', 'upstream/master']
PUSH_TO_UPSTREAM_CMD = ['git', 'push', 'origin', 'master']

def forkRepository(github_token,upstream_url):
    """ Fork a github repository """
    gh = github3.login(token=github_token)
    parsed_url = parse(upstream_url)

    # Fork the repo
    user = gh.me()
    print(user.login)
    try:
        upstream_repo = gh.repository(parsed_url.owner, parsed_url.repo)
        if upstream_repo is None:
            print("Unable to find repo %s" % upstream_url)
            exit(1)
        forked_repo = upstream_repo.create_fork()
        print(forked_repo)
        print("Forked %s to %s" % (upstream_url, forked_repo.ssh_url))
        return forked_repo.ssh_url
    except:
        forked_repo = gh.repository(user.login, parsed_url.repo)
        print("Forked repo %s already exists" % forked_repo.full_name)
        return forked_repo.ssh_url

def checkGitRepository():
    """
        Returns True if the repository is a git repository.
    """
    return os.path.isdir('.git')

def getRepoOriginUrl():
    """
        Return origin url of the git repository.
    """
    try:
        repo_origin_url = str(check_output(CURRENT_REPO_ORIGIN))
        repo_origin_url = repo_origin_url.replace("b'", "")
        repo_origin_url = repo_origin_url.rstrip()

        print("origin url for this repository:- ", repo_origin_url)
        return repo_origin_url
    except Exception as e:
        print("Unable to get origin url for the repository")
        print(e)
        raise

def getRepoUpstreamUrl():
    """
        Return upstream url of the git repository.
    """

    try:
        repo_upstream_url = str(check_output(CURRENT_REPO_UPSTREAM))
        repo_upstream_url = repo_upstream_url.replace("b'", "")
        repo_upstream_url = repo_upstream_url.replace("\\n'", "")

        print("upstream url for this repository:- ", repo_upstream_url)
        return repo_upstream_url.strip()
    except Exception as e:
        print("Unable to get upstream url for the repository")
        print(e)
        raise

def fetchUpstream():
    """
        Fetches upstream changes to your local repository.
    """

    try:
        print("Fetching upstream...")
        print(".........")

        call(FETCH_UPSTREAM_CMD)

        print("Upstream fetch done")

    except Exception as e:
        print("Unable to fetch upstream for the repository")
        print(e)
        raise

def checkoutMasterBranch():
    """
        Checkouts master branch of the repository.
    """

    try:
        print("Checking out master")
        print(".........")

        call(CHECKOUT_MASTER_CMD)

        print("Master checkout done")
    except Exception as e:
        print("Unable to checkout master branch")
        print(e)
        raise

def mergeUpstream():
    """
        Merges upstream and local branch.
    """
    try:
        print("Merging master")
        print("..........")

        call(MERGE_UPSTREAM_CMD)

        print("Syncing done.")
    except Exception as e:
        print("Unable to merge.")
        print(e)
        raise

def pushToOrigin():
    """
        Pushes the locally sysnced code to your remote fork.
    """
    try:
        print("Pushing to origin master")
        print("........")

        call(PUSH_TO_UPSTREAM_CMD)

        print("Push done.")
    except Exception as e:
        print("Unable to push to origin")
        print(e)
        raise

def addRepoUpstream():
    """
        Adds upstream url of parent repository to the locally cloned
        fork if upstream not available.
    """

    repo_origin_url = getRepoOriginUrl()

    if repo_origin_url[0] == "h":
        url_segments = repo_origin_url.split("https://github.com/")

    if repo_origin_url[0] == "g":
        url_segments = repo_origin_url.split("git@github.com:")

    user_and_repo = url_segments[1]
    user_and_repo = user_and_repo.replace(".git", "")
    user, repo = user_and_repo.split("/")

    print("Getting upstream url for the repo ...")
    url = "https://api.github.com/repos/{}/{}".format(user, repo)

    try:
        response = requests.get(url)
        repo_upstream_url = response.json()["parent"]["clone_url"]

        print("Upstream URL is:-", repo_upstream_url)

        ADD_REMOTE_CMD.append(repo_upstream_url)
        print(ADD_REMOTE_CMD)

        print("Upstream is added to the fork")
        call(ADD_REMOTE_CMD)
    except Exception as e:
        print("Unable to add upstream url to the repository")
        print(e)
        raise

def sync():
    """
        Main function to sync the local forks with parents repository.
    """
    print("-" * 120)
    print("|" + "Starting Fork Syncing Process".center(118) + "|")
    print("-" * 120)

    # Check if the current repository is a git repository
    assert checkGitRepository()

    # Check if the git repository has a origin
    assert getRepoOriginUrl()

    try:
        # Now try to get the upstream for the repository.
        assert getRepoUpstreamUrl()

        # If upstream is present do following.
        # First fetch the upstream
        fetchUpstream()

        # Then checkout master branch
        checkoutMasterBranch()

        # Then merge upstream master and local branch
        mergeUpstream()

        # Now finally push the delta to the origin master
        pushToOrigin()
    except Exception as e:
        print(e)
        print("Trying to add upstream automatically.")

        # Since upstream is not present do following
        # First add the upstream of the parent repository.
        addRepoUpstream()

        # Then fetch the upstream
        fetchUpstream()

        # Then checkout master branch
        checkoutMasterBranch

        # Then merge upstream master and local branch
        mergeUpstream()

        # Now finally push the delta to the origin master
        pushToOrigin()

    print("-" * 120)
    print("|" + "Ending Fork Syncing Process".center(118) + "|")
    print("-" * 120)

def checkUserExists(github_token,username):
    try:
        gh = github3.login(token=github_token)
        gh.user(username)
        return True
    except Exception as e:
        # if 'NotFoundError' in e:
        return False

def main(argv):
    """ Main Function """
    print(os.getcwd())

    if len(argv) > 1:
        repository_to_be_forked = argv[1]
        gh_token = '<gh_token>'

    gh_user = repository_to_be_forked.split('/')[-2]
    
    print("-" * 120)
    print("|" + "Forking the repository".center(118) + "|")
    print("-" * 120)
    fork = forkRepository(gh_token, repository_to_be_forked)

    if fork[0] == "g":
        url_segments = fork.split("git@github.com:")

    user_and_repo = url_segments[1]
    user_and_repo = user_and_repo.replace(".git", "")
    user, repo = user_and_repo.split("/")

    repository_to_be_cloned = 'https://github.com/'+user+'/'+repo

    try:
        os.makedirs(gh_user)
    except:
        pass

    os.chdir(gh_user)
    
    if repo not in os.listdir('.'):
        print("-" * 120)
        print("|" + "Cloning the repository".center(118) + "|")
        print("-" * 120)
        CLONE_REPO.append(repository_to_be_cloned)
        call(CLONE_REPO)
        print('cloned the repository')

    os.chdir(repo)

    sync()

if __name__ == '__main__':
    print(checkUserExists('<gh_token>','veda-vya'))
    # main(sys.argv)
