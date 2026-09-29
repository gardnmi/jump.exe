# Releases

Releases are managed by **Release Please**, with the repository's built-in
`GITHUB_TOKEN`. There is no personal access token or hardcoded download checksum
to maintain.

1. Merge conventional commits to `main`.
2. CI tests the game and builds a deterministic runtime archive.
3. Release Please opens or updates a release PR containing `version.txt`,
   `CHANGELOG.md`, and `.release-please-manifest.json`.
4. Review and merge that release PR when ready.
5. The same workflow validates the merged commit, creates a draft release,
   attaches the runtime archive, installer, and checksums, then publishes it.

The public release is the runtime archive plus `install.py` and `SHA256SUMS`.
The archive excludes tests, render tools, previews, and retired assets. Its file
manifest is generated from the files actually packaged.

## Why the workflow is arranged this way

Most events created by `GITHUB_TOKEN` do not start other workflows. Bot-created
pull-request events now produce runs requiring manual approval. Publishing runs
in the **same workflow** as Release Please; it does not depend on a second workflow
triggered by the release tag. The release job explicitly dispatches read-only CI
on Release Please's PR branch so its checks run without a PAT. The three generated
version/changelog files are excluded from the ordinary PR trigger to avoid a
duplicate approval-gated run. Code PRs still run the ordinary checks, and every
commit to `main` is tested before the release job can run.

Enable **Settings → Actions → General → Allow GitHub Actions to create and approve
pull requests** when setting up a fork. This repository already has it enabled.

The release job has `contents`, `pull-requests`, `issues`, and `actions` write
permissions. Test jobs have read-only repository access. Fork PRs only run CI.

## Recovering a failed publish

Re-run the failed Release Please workflow on the **same commit**. An existing
draft for that version is reused and its assets can be safely re-uploaded before
publication. The publishing helper checks that the release tag points to the
tested commit. It refuses to publish a draft from a different commit and never
overwrites assets on an already public release.

Once published, fix a defect through a new conventional commit and a new release.
The installer resolves the latest published release once and downloads all its
assets from that exact tag. Players can pin a version or run `jump.exe --rollback`.

## Local packaging check

```sh
python tools/test.py
python tools/build_release.py
cd dist
sha256sum -c SHA256SUMS
```

The test suite also installs into temporary prefixes, checks the installed
launcher, updates and rolls back, and verifies that corrupt or unsafe archives
cannot replace the working installation.

Upstream references:
[Release Please Action](https://github.com/googleapis/release-please-action) and
[manifest configuration](https://github.com/googleapis/release-please/blob/main/docs/manifest-releaser.md),
plus [GitHub token event rules](https://docs.github.com/en/actions/concepts/security/github_token).
