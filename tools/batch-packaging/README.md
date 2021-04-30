- Use following script to build docker image
```shell script
bash build-img.sh
```

- Run container for package building
```shell script
docker run --name openeuler-pkg --hostname openeuler-pkg -it openeuler-pkg-build bash
```

- Run package building script in container
```shell script
export GITEE_USER="your gitee account"
export GITEE_PAT="you gitee personall access token"
export GITEE_EMAIL="you gitee account email"

python3 batch-packaging.py build
```
By default, above command will build `spec` and `rpm` for all the projects in
`.csv` format projects list file, and then will command and create PR to openEuler
source package repo one by one. This tool will also check the dependencies,
source repo existence, remote branch existence, will record to log file.
For more functionality, you can run `python3 openeuler_pkg.py --help` to get more help info.

**NOTE:**
Before run this tool, you may need to check and modify following fields according to real conditions:
- daily build docker images URL in `build-img.sh`
- daily build openEuler packages repo URL
- the bash openEuler docker image name for `FROM` field in Dockerfile