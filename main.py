import configparser
import praw
import prawcore
    
config = configparser.ConfigParser()
config.read('config.ini')

client_id = config['REDDIT']['CLIENT_ID']
client_secret = config['REDDIT']['CLIENT_SECRET']
password = config['REDDIT']['REDDIT_PASSWORD']
username = config['REDDIT']['REDDIT_USERNAME']

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    password=password,
    username=username,
    user_agent='Subreddit Transfer Script v1.0 by ARandomBoiIsMe'
)

def main():
    from_subreddit_name = config['VARS']['FROM_SUBREDDIT']
    to_subreddit_name = config['VARS']['TO_SUBREDDIT']

    from_subreddit = validate_subreddit(from_subreddit_name)
    if from_subreddit == None:
        print(f"This subreddit does not exist: r/{from_subreddit_name}.")
        exit()

    to_subreddit = validate_subreddit(to_subreddit_name)
    if to_subreddit == None:
        print(f"This subreddit does not exist: r/{to_subreddit_name}.")
        exit()

    if to_subreddit.user_is_moderator == False:
        print(f"You must be a mod in this sub to set rules or removal reasons: r/{to_subreddit_name}")
        exit()

    rules = retrieve_rules(from_subreddit)

    removal_reasons = retrieve_reasons(from_subreddit)

    transfer_rules(rules, to_subreddit)

    transfer_reasons(removal_reasons, to_subreddit)

def validate_subreddit(subreddit_name):
    try:
        return reddit.subreddits.search_by_name(subreddit_name, exact=True)[0]

    except prawcore.exceptions.NotFound:
        return None

def retrieve_rules(from_sub):
    print(f'Retrieving rules from {from_sub.display_name}...')

    rules = list(from_sub.rules)
    if len(rules) == 0:
        print('No rules found.')
    else:
        print('Rules retrieved successfully.')

    return rules

def retrieve_reasons(from_sub):
    print(f'Retrieving removal reasons from {from_sub.display_name}...')

    removal_reasons = list(from_sub.mod.removal_reasons)
    if len(removal_reasons) == 0:
        print('No removal reasons found.')
    else:
        print('Removal reasons retrieved successfully.')

    return removal_reasons

def transfer_rules(rules, to_sub):
    for rule in rules:
        try:
            to_sub.rules.mod.add(
            short_name=rule.short_name, kind=rule.kind, description=rule.description, violation_reason=rule.violation_reason
            )

            print(f'Rule \'{rule.short_name}\' added to {to_sub.display_name}')

        except praw.exceptions.RedditAPIException as e:
            if 'SR_RULE_EXISTS' in str(e):
                print(f'Error: {rule.short_name} - This rule already exists in this subreddit.')

def transfer_reasons(reasons, to_sub):
    for reason in reasons:
        if reason_exists_in_sub(to_sub, reason) == True:
            print(f'Error: {reason.title} - This removal reason already exists in this subreddit.')
            continue

        to_sub.mod.removal_reasons.add(title=reason.title, message=reason.message)
        print(f'Removal reason \'{reason.title}\' added to {to_sub.display_name}')

def reason_exists_in_sub(subreddit, removal_reason):
    for reason in subreddit.mod.removal_reasons:
        if removal_reason.title == reason.title:
            return True
    
    return False

main()
