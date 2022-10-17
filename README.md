# LaTeX-Paper-Autobuild

I always struggled to find a good solution to automate builds and track versions while writing a paper in LaTeX. Well, I decided to write a tool myself. Overleaf is one nice solution where you don't have to worry about anything, till it goes down for maintenance at the very time you need to make a crucial update (jk we all love Overleaf don't we). Compiling locally is always nice, auto-building and version tracking for it is even better. Plus I thought I could support some custom builds too.

Default build:

* Latest compiled pdf : [main.pdf](https://github.com/Siddhant-Ray/LaTeX-Paper-Autobuild/releases/download/release/main.pdf)

Advanced builds:

* Greyscale pdf : [main_grey.pdf](https://github.com/Siddhant-Ray/LaTeX-Paper-Autobuild/releases/download/release/main_grey.pdf)
* No appendix : [main_no-appendix.pdf](https://github.com/Siddhant-Ray/LaTeX-Paper-Autobuild/releases/download/release/main_no-appendix.pdf)
* No acknowledgements : [main_no-acknowledgements.pdf](https://github.com/Siddhant-Ray/LaTeX-Paper-Autobuild/releases/download/release/main_no-acknowledgements.pdf)
* Abstract only: 

## How to use:

### GitLab

Tbh, using this build system works much better with GitLab CI, as GitLab's integrated CI/CD supports building, storing artifacts etc. To run as part of a GitLab repository, this repository can be mirrored into a GitLab repository, and the file [.gitlab-ci.yml](.gitlab-ci.yml) can be used for autobuilding. All PDFs are built on every push. The caveat is that GitLab doesn't come with an in-built autoconfigured runner, so you will have to create a runner and replace the ```ci-runner``` with your own runner tag in [.gitlab-ci.yml](.gitlab-ci.yml). More inforamtion about setting up runners can be found here: [gitlab-ci-runners](https://docs.gitlab.com/runner/register/).

Once setup, the built PDFs will be stored as artifacts on the successful completion of every job, and they can be linked to the ReadMe (or whatever you want to do with them).

### GitHub

Well if GitLab is not an option, you can make it work with GitHub too. The file [.build-paper.yml](.github/workflows/build-paper.yml) automatically builds every version of the paper on push to master. The caveat here is that GitHub doesn't let you store artifacts with an expiry date. Hence, here we package every built PDF as part of a new release, and the release PDFs are linked in the ReadMe to download.

## Comments:

This template relies a bit too much on the ACM templates as a base. I would argue that is not an issue in academia in general, as ACM is a good standard to follow. Plus you can always change the document template inside [main.tex](main.tex).

If you do include new packages in the preamble (you will at some point), you may run into package clashes with the ACM class. With a little bit of investigation, I am sure they can be fixed.

I have also included [ACM-Reference-Format](lib/ACM-Reference-Format.bst) and the [acmart](lib/acmart.cls) class files as a reference in case you want to play around with them (I do not own these files, all are &copy; ACM).

New features will be added to this template from time to time, when I can think of them. If you want to contribute, feel free to create a PR. Improvements and suggestions are welcome.





