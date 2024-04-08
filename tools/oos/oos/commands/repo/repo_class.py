import os
import subprocess

import click
import requests

from oos.common import CONSTANTS
from oos.common import utils


class PkgGitRepo(object):
    def __init__(self, gitee_pat=None, gitee_org='src-openeuler',
                 gitee_user=None, gitee_email=None,
                 pypi_name=None, repo_name=None):
        self.pypi_name = pypi_name
        self.gitee_org = gitee_org
        self.gitee_pat = gitee_pat
        self.gitee_user = gitee_user
        self.gitee_email = gitee_email
        self.not_found = False
        self.branch_not_found = False
        self.repo_dir = ''
        self.commit_pushed = False
        if not repo_name:
            self.repo_name, _ = utils.get_openeuler_repo_name_and_sig(
                self.pypi_name)
        else:
            self.repo_name = repo_name

    def fork_repo(self, repo_name):
        try:
            url = "https://gitee.com/api/v5/repos/%s/%s/forks" % (
                self.gitee_org, repo_name)
            resp = requests.request("POST", url,
                                    data={"access_token": self.gitee_pat})
            if resp.status_code == 404:
                click.echo("Repo not found for: %s/%s" % (self.gitee_org,
                                                          repo_name),
                           err=True)
                self.not_found = True
            elif resp.status_code != 201:
                click.echo("Fork repo %s failed, %s" % (repo_name, resp.text), err=True)
        except requests.RequestException as e:
            click.echo("HTTP request to gitee failed: %s" % e, err=True)

    def clone_repo(self, src_dir):
        clone_url = "https://gitee.com/%s/%s" % (
            self.gitee_user, self.repo_name)
        click.echo("Cloning source repo from: %s" % clone_url)
        repo_dir = os.path.join(src_dir, self.repo_name)
        if os.path.exists(repo_dir):
            subprocess.call(["rm", "-fr", repo_dir])
        subprocess.call(["git", "clone", clone_url, repo_dir])
        self.repo_dir = os.path.join(src_dir, self.repo_name)

    def add_branch(self, src_branch, dest_branch, reuse_branch=False):
        url = "https://gitee.com/api/v5/repos/{gitee_org}/{repo_name}/" \
              "branches/{dest_branch}".format(gitee_org=self.gitee_org,
                                              repo_name=self.repo_name,
                                              dest_branch=dest_branch)
        resp = requests.request("GET", url)
        if resp.status_code == 404:
            click.echo("Branch: %s not found for project: %s/%s" %
                       (dest_branch, self.gitee_org, self.repo_name),
                       err=True)
            self.branch_not_found = True
            return
        click.echo("Adding branch for %s/%s" % (self.gitee_org, self.repo_name))
        cmd = 'cd %(repo_dir)s; ' \
              'git config --global user.email "%(gitee_email)s";' \
              'git config --global user.name "%(gitee_user)s";' \
              'git remote add upstream "https://gitee.com/%(gitee_org)s/' \
              '%(repo_name)s";' \
              'git remote update;' \
              'git checkout -b %(src_branch)s upstream/%(dest_branch)s; ' % {
                  "repo_dir": self.repo_dir,
                  "gitee_user": self.gitee_user,
                  "gitee_email": self.gitee_email,
                  "gitee_org": self.gitee_org,
                  "repo_name": self.repo_name,
                  "src_branch": src_branch,
                  "dest_branch": dest_branch}
        click.echo("CMD: %s" % cmd)
        status = subprocess.call(cmd, shell=True)
        if not reuse_branch and status != 0:
            raise Exception("Add branch %s for repo %s FAILED!!" % (
                src_branch, self.repo_name))

    def commit(self, commit_message, do_push=True, amend=False):
        click.echo("Commit changes for %s/%s" % (
            self.gitee_org, self.repo_name))
        _commit_cmd = 'git commit -am "%(commit_message)s";'
        if amend:
              _commit_cmd = 'git commit --amend -m "%(commit_message)s";'
        commit_cmd = 'cd %(repo_dir)s/; ' \
                     'git add .; ' \
                     f"{_commit_cmd}" \
                     'git remote set-url origin https://%(gitee_user)s:' \
                     '%(gitee_pat)s@gitee.com/%(gitee_user)s/%(repo_name)s;' \
                     % {"repo_dir": self.repo_dir,
                        "repo_name": self.repo_name,
                        "gitee_user": self.gitee_user,
                        "gitee_pat": self.gitee_pat,
                        "commit_message": commit_message}
        if do_push:
            commit_cmd += 'git push origin -f'
            self.commit_pushed = True
        click.echo("CMD: %s" % commit_cmd)
        subprocess.call(commit_cmd, shell=True)

    def create_pr(self, src_branch, remote_branch, tittle):
        if not self.commit_pushed:
            click.secho("WARNING: Commit was not pushed of %s, exit!" %
                        self.repo_name, fg='red')
            return
        click.echo("Creating pull request for project: %s" % self.repo_name)
        try:
            url = "https://gitee.com/api/v5/repos/%s/%s/pulls" % (
                self.gitee_org, self.repo_name)
            resp = requests.request(
                "POST", url, data={"access_token": self.gitee_pat,
                                   "title": tittle,
                                   "head": self.gitee_user + ":" + src_branch,
                                   "base": remote_branch})
            if resp.status_code != 201:
                click.echo("Create pull request failed, %s" % resp.text)
                return
            try:
                return resp.json()['number']
            except Exception:
                click.echo('please get pr number manual')
        except requests.RequestException as e:
            click.echo("HTTP request to gitee failed: %s" % e, err=True)

    def delete_fork(self):
        url = 'https://gitee.com/api/v5/repos/%s/%s?access_token=%s' % (
            self.gitee_user, self.repo_name, self.gitee_pat)
        resp = requests.request("DELETE", url)
        if resp.status_code == 404:
            click.echo("Repo %s/%s not found" % (
                self.gitee_user, self.repo_name))

    def pr_add_comment(self, comment, pr_num):
        click.echo("Adding comment: %s for project: %s in PR: %s" % (
            comment, self.repo_name, pr_num))
        url = 'https://gitee.com/api/v5/repos/%s/%s/pulls/%s/comments' % (
            self.gitee_org, self.repo_name, pr_num)
        body = {"access_token": "%s" % self.gitee_pat,
                "body": "%s" % comment}
        resp = requests.request("POST", url, data=body)
        if resp.status_code != 201:
            click.echo("Comment PR %s failed, reason: %s" %
                       (pr_num, resp.reason), err=True)
    
    def pr_get_comments(self, pr_num):
        click.echo("Getting comments for %s/%s in PR: %s" % (
            self.gitee_org, self.repo_name, pr_num))
        url = 'https://gitee.com/api/v5/repos/%s/%s/pulls/%s/comments' % (
            self.gitee_org, self.repo_name, pr_num)
        param = {'comment_type': 'pr_comment', 'direction': 'desc'}
        resp = requests.get(url, params=param)
        if resp.status_code != 200:
            click.echo("Getting comments of %s failed, reason: %s" %
                       (pr_num, resp.reason), err=True)
        return resp.json()

    def get_pr_list(self, filter=None):
        click.echo("Getting PR list for %s/%s" % (
            self.gitee_org, self.repo_name))
        url = 'https://gitee.com/api/v5/repos/%s/%s/pulls?access_token=%s' % (
            self.gitee_org, self.repo_name, self.gitee_pat)
        resp = requests.get(url, params=filter)
        if resp.status_code != 200:
            click.echo("Getting PR list failed, reason: %s" % resp.reason,
                       err=True)
        return resp.json()

    def branch_version_list(self, suffix, keyword):
        try:
            # https://gitee.com/api/v5/repos/{owner}/{repo}/branches
            br_url = 'https://gitee.com/api/v5/repos/%s/%s/branches' % (
                    self.gitee_org, self.repo_name)
            resp = requests.request('GET', br_url,
                                    data={'access_token': self.gitee_pat})
        except requests.RequestException as e:
            click.echo("HTTP request to gitee failed: %s" % e, err=True)
            return

        res = ''
        try:
            for ele in resp.json():
                try:
                    br = ele['name']
                except:
                    # 获取ele['name']失败的直接跳过
                    res += br + '\t' + 'BAD BRANCH' + '\n'
                    continue

                if keyword and keyword not in br:
                    continue

                # https://gitee.com/api/v5/repos/{owner}/{repo}/contents(/{path})
                url = 'https://gitee.com/api/v5/repos/%s/%s/contents/' % (
                        self.gitee_org, 
                        self.repo_name)
                headers = {
                    'Content-Type': 'application/json;charset=UTF-8',
                }
                params = {
                    'access_token': self.gitee_pat,
                    'ref': br
                }

                try:
                    branch_content = requests.get(url, headers=headers, params=params)
                except Exception as e:
                    res += br + '\t' + e + '\n'
                    continue

                not_found = True
                for content in branch_content.json():
                    if 'file' == content['type'] and content['name'].endswith(suffix):
                        res += br + '\t' + content['name'] + '\n'
                        not_found = False
                        break

                if not_found:
                    res += br + '\t' + 'NO TAR FILE' + '\n'
                    continue

        except Exception as e:
            click.echo('exception info: %s' % e)
            return

        click.echo(res)


    def _add_file_and_commit_with_last_change(slef, title):
        try:
            subprocess.call(['git', 'add', '.'])
            subprocess.call(['git', 'commit', '-m', title])
            subprocess.call(['git', 'push'])
            click.echo('******Finish the CMD: git add, commit and push******')

        except Exception:
            raise click.ClickException('git add or git commit fail')

    def create_pr_for_rpm_in_current_dir(self, remote_branch, add_commit, comment):
        cur_dir = os.getcwd()
        self.repo_name = os.path.basename(cur_dir)
        os.chdir(cur_dir)
        try:
            res = subprocess.check_output(['git', 'config', '--list']).decode()
            p_start = res.find('user.name') + 10
            p_end = res.find('\n', p_start)
            self.gitee_user = res[p_start:p_end]

            res = subprocess.check_output(['git', 'branch']).decode()
            p_start = res.find('* ') + 2
            p_end = res.find('\n', p_start)
            src_branch = res[p_start:p_end]
        except Exception:
            raise click.ClickException('get user.name or branch failed')

        if not remote_branch:  # 默认使用src_branch
            remote_branch = src_branch

        # title直接获取spec文件的 未获取到认为异常 更改必改spec文件
        title = None
        for file in os.listdir(cur_dir):
            if file.endswith('.spec'):
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    title = content[content.find('%changelog'):].split('\n')[2][2:]
                    break

        if title:
            if add_commit:
                self._add_file_and_commit_with_last_change(title)

            self.commit_pushed = True
            pr_num = self.create_pr(src_branch, remote_branch, title)

            if pr_num and comment:
                self.pr_add_comment(comment, pr_num)
                pr_link = 'PR link:\nhttps://gitee.com/%s/%s/pulls/%s' % (
                    self.gitee_org, self.repo_name, pr_num
                )
                click.echo(pr_link)
