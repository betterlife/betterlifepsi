#!/usr/bin/env bash
echo "chmod 600 .travis/deploy.pem"
chmod 600 .travis/deploy.pem

echo "ssh-add .travis/deploy.pem"
ssh-add .travis/deploy.pem

echo "git remote add deploy $PRODUCTION_REPO_URI"
git remote add deploy $PRODUCTION_REPO_URI

# Follow Section needed on production
# [receive]
#	denyCurrentBranch = ignore
git config push.default simple
# git fetch --unshallow
git add swtag
git commit -m "Add swtag"

echo "git push deploy HEAD:master"
git push deploy HEAD:master

echo "reload service uwsgi9090"
ssh -i .travis/deploy.pem root@$PRODUCTION_HOST "service uwsgi9090 reload"
