
issue=300
issue_title=$(gh issue view "$issue" | sed -n 1p| sed "s/title:\t//g"  )
issue_title_cleaned=$(echo "$issue_title" | sed "s/ /_/g" | tr '[:upper:]' '[:lower:]')

branch_name="$issue"_"$issue_title_cleaned"

git checkout -b "$branch_name"
git commit --allow-empty -m "make pull request"
git push -u origin "$branch_name"

gh pr create --title "$issue_title" --body "Closes #$issue"