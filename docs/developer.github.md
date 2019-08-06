# Workflow

![Git workflow](img/namex-gitflow.png)

## 1 Fork in the GitHub

1. Visit https://github.com/bcgov/sbc-auth
2. Click `Fork` button (top right)

## 2 Clone fork to your workstation

- Create your clone:

```sh
export workspace_dir=<your workstations dir>
export user=<your github account name>
mkdir -p $workspace_dir
cd $workspace_dir
git clone https://github.com/$user/sbc-auth.git
cd $workspace_dir/sbc-auth
git remote add upstream https://github.com/bcgov/sbc-auth.git
# Never push to upstream master and development
git remote set-url --push upstream no_push
# Confirm that your remotes make sense:
git remote -v
```

## 3 Get your local master and fork up to date

- Sync your local master with upstream/development branch:

  ```sh
  cd $workspace_dir/sbc-auth
  git fetch upstream
  git checkout master
  git rebase upstream/development
  git push
  ```

## 4 Development

- Create a new feature Branch and push to your local fork:

  ```sh
  git checkout -b <feature# from ZenHub>-<short_name_for_this_work>
  git push
  ```

- Keep your branch in sync:

  ```sh
  git checkout <feature# from ZenHub>-<short_name_for_this_work>
  git fetch upstream
  git rebase upstream/development
  ```

- Commit your changes every day to your branch

  ```sh
  git status
  git add .
  git commit -s -m "a useful comment including the issue #"
  git push origin <feature# from ZenHub>-<short_name_for_this_work>
  ```

  Likely you will need to go back and edit/build/test some more.
  Use `commit --amend` in a few cycles.

## 5 Before submit a pull request

> [**Code Review Checklist**<https://github.com/bcgov/sbc-auth/wiki/API-Code-Review-Checklist]>

- Keep your branch in sync and merge any conflicts you see in your branch:

  ```sh
  git checkout <feature# from ZenHub>-<short_name_for_this_work>
  git fetch upstream
  git rebase upstream/development
  ```

- Run the following command and fix anything you need:

  Windows:

  ```sh
  flake8 src/auth-api tests
  pylint --rcfile=setup.cfg --load-plugins=pylint_flask --disable=C0301,W0511 src/auth_api
  pytest
  coverage report
  start chrome htmlcov/index.html
  ```

  Mac or Linux:

  ```sh
  make flake8
  make pylint
  make local-test
  make local-coverage
  make mac-cov
  ```

## 6 Create a pull request

1. Visit your fork at `https://github.com/$user/sbc-auth`
2. Click the `Pull Request` button next to your `<feature# from ZenHub>-<short_name_for_this_work>` branch
3. Compare `https://github.com/bcgov/sbc-auth` development branch with your `<feature# from ZenHub>-<short_name_for_this_work>` branch
4. If you see `Able to merge.` text then Click the `Create Pull Request` button and add the comments
5. Submit your zenhub task to `Dev Code Review` and let the team know your pull request need to do a code review

## 7 Code review, pipeline process (unittest, Sonarqube, build and development) or QA fail

Back to Step 4 or 5 fix your code
