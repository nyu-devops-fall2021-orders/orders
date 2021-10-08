# orders
This repo maintains the orders API for the ecommerce website being developed by NYU DevOps Fall 2021.

## Development Workflow

### Initial Setup
git clone https://github.com/nyu-devops-fall2021-orders/orders.git
git checkout -b

### Every New Task
<code>
git checkout main<br>
git pull<br>
git checkout -b [new-branch-name]
</code>

<br>
<br>
[make your changes - create, update, delete files]

#### Either this
<code>
git status // see which files are added/modified/deleted <br>
git diff // see your changes line by line<br>
git add [file name1] [file name2] ... // stage your changed files which you want to commit<br>
git commit -m "[commit message]" // commit to your local repo with a short message<br>
git push // push your changes to github
</code>

#### Or this (if you have VSCode)
1. Open "Source Control" tab on the sidebar
2. Click on each changed file to see your changes and correct anything if needed
3. Click the "+" next to a file name if you want to stage the file for commit
4. Once all the needed files are staged, write a commit message in the text box at the top
5. Press command+Enter (or control+Enter) to commit your staged changes
6. Click the three dots next to "Source Control" and click "Push" to push your changes to Github
7. If you have created a new branch, you will have to click OK on a dialog box to create the branch on Github

### Finally
1. Open the Github repo
2. Create a Pull Request (PR) from your branch to the main branch
3. Share the PR link on Slack (or add reviewers on the sidebar)
4. Once the PR has been approved, it can be merged
5. Hooray, it's done!
