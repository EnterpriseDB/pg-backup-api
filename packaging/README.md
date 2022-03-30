# Releasing pg-backup-api

## Increment the version

Update the version string in [pg_backup_api/version.txt](../pg_backup_api/version.txt).
Use [semantic versioning](https://semver.org/) when determining the new version.

If you are publishing new packages for a version of pg-backup-api which has already been published then the pg-backup-api version should remain the same.

## Set the package release version

### New pg-backup-api releases

Check that the `RELEASE_VERSION` in [.github/workflows/publish-to-cloudsmith.yml](../.github/workflows/publish-to-cloudsmith.yml) is set to `1`.

### Re-publishing existing pg-backup-api releases

Increment the `RELEASE_VERSION` in [.github/workflows/publish-to-cloudsmith.yml](../.github/workflows/publish-to-cloudsmith.yml).

## Update the release notes

* Add release notes to [pg_backup_api/news.yml](../pg_backup_api/news.yml).
* Make sure you include your name and email in the `author` field as this will be included in the rpm and deb changelogs.
* If you are re-publishing an existing pg-backup-api release then include the `iteration` field and set this to the value of `RELEASE_VERSION` used in the above step.
* Generate the changelogs by running `./changelogs.py`.
* Update the changelogs and news.md by moving the newly generated ones into their target locations:
  * `mv templates/deb.changelog changelogs`
  * `mv templates/rpm.changelog changelogs`
  * `mv templates/news.md ../pg_backup_api`

## Publish the release

Once the changes are pushed and tagged, the release packages can be built and pushed to the staging repo in Cloudsmith, so:

* Commit and PR the above changes, including the changelogs, `news.md` file, `version.txt` and if necessary the GitHub workflow file.
* Tag the release with `git tag release/major.minor.patch-iteration` and push the tag.
* Run the [Publish to Cloudsmith](https://github.com/EnterpriseDB/pg-backup-api/actions/workflows/publish-to-cloudsmith.yml) workflow being sure to set the `Is release` option to `Y`.

Once happy with the packages in staging they need to be copied to the production repositories.

### Cloudsmith prod repo

* Using the Cloudsmith cli, copy the packages from the `ibm-dev` staging repo to the `edb` repo.
* Also using the Cloudsmith cli, add the `production` tag to packages you just copied in the `edb` repo.

### EDB repos `{apt,yum,zypp}.enterprisedb.com`

Once packages are tagged with `production` in the `edb` Cloudsmith repository they will automatically be synced to the EDB repositories.

### 2ndQuadrant repos

Use the following (non-public) Jenkins job to sync packages from the `edb` Cloudsmith repo to the 2ndQuadrant repositories: https://ci.2ndquadrant.com/jenkins/job/pg-backup-api/job/pg-backup-api/.
