class vote:
  text = '**Upvote** if this post has **good rhyme AND meter ("True BootTooBig"). Downvote** if this post has **bad rhyme/meter ("Small Boots"). Report** this post if it requires further moderator action, such as being a repost or being offensive. \n\n'
  notSunday = 'If the score of this comment falls too low, the post will be removed. \n\n'
  sunday = 'This post is posted on Small Boot Sunday \n\n'

class botm:
  title = "Welcome to BotM: {month} {year} Contest! " 
  body = "{intro}\n\n&nbsp;\n\n{rule}\n\n&nbsp;\n\n{conclusion}"  
  
  intro = "Hello r/boottoobig, \n\nWelcome to another Boot of the Month (BotM) Contest. BotM is still in its very early stage, please read the rules below carefully before particpating, as the rule may subject to change. "
  rule = 'Rules: \n\n1. Top 10 upvoted posts from last month will enter the contest. \n\n2. If the post is flaired as "Small Boots", it will be disqualified, and next most upvoted post will enter the contest. \n\n3. If you think a post deserves to be BotM, just upvote the corresponding comment. \n\n4. Please upvote up to 3 comments. \n\n5. All top level comments other than those by u/boot_size_judge will be removed. '
  conclusion = "The winner will be announced in one week. "
  
  comment = "[{title}]({link}), by u/{op}"
  
  winner_title = ""
  winner_body = ""

class report:
  smallboot = "Bot comment less than -10, not posted on sunday"
  
class remove_message:
  smallboot = 'Hello {op}, \n\nThank you for your post! Unfortunately, due to the score on [this comment]({url}) is too low, your post is automatically removed under rule 3b: \n\n---\n\n>Try to make sure your post has good rhyme/meter. Good rhyme/meter is "True BootTooBig" while bad rhyme/meter is "Small Boots." If a "Small Boots" post is posted outside of Small Boots Sunday, it will be removed. Low effort posts will also be removed. At the moment, final discretion is up to the mods. \n\nYou are welcome to try it again on Small Boots Sunday. \n\n--- \n\nIf you have any further questions, please feel free to [message the moderators](https://www.reddit.com/message/compose?to=%2Fr%2Fboottoobig&subject=My+post+is+removed+incorrectly)'
  self_post = 'Hello {op}, \n\nThank you for your post! Unfortunately, self post other than mod announcement is automatically removed. \n\nIf you have any further questions, please feel free to [message the moderators](https://www.reddit.com/message/compose?to=%2Fr%2Fboottoobig&subject=My+post+is+removed+incorrectly)'

footer = "---\n\nBoot_Size_Judge v0.2.2 (beta) | [GitHub](https://github.com/aguamenti78/boot_size_judge/) | Contact: [bot maker](https://www.reddit.com/message/compose?to=le_haos&subject=[BSJ]) / [Mod Team](https://www.reddit.com/message/compose?to=%2Fr%2Fboottoobig)"

