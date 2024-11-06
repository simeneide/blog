# Blog site eide.ai
Repo for running the blog site eide.ai. The site is built using Quarto and published on github pages. These are my own notes for whenever i need to do any updates here. If you actually want to read the site, go to [eide.ai](https://eide.ai).

- Model is deployed using github pages in the repo simeneide/blog. Deployment info found [here](https://quarto.org/docs/publishing/github-pages.html).



### To write a new post
Instructions found [here](https://quarto.org/docs/get-started/authoring/vscode.html).

- Create a new markdown file in the `posts` folder.

### Basically to deploy:
```
quarto render
git add docs
git commit -m "Update docs"
git push
```